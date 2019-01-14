"""The system for scheduling tasks and executing them in order.
Deals with dependencies, priorities, resources, etc.
The :py:class:`~finestrino.worker.Worker` pulls tasks from the scheduler
(usually over the REST interface) and executes them.
"""
import collections
import inspect
import json

#from finestrino.batch_notifier import BatchNotifier

try:
    import cPickle as pickle
except ImportError:
    import pickle

import functools
import hashlib
import itertools
import logging
import os
import re
import time
import uuid

from finestrino import configuration
from finestrino import notifications

from finestrino.task import Config
from finestrino import parameter

from finestrino.batch_notifier import BatchNotifier

from finestrino import task_history as history

from finestrino.batch_notifier import BatchNotifier

from finestrino.metrics import MetricsCollectors

from finestrino.task_status import DISABLED, DONE, FAILED, \
    PENDING, RUNNING, \
    SUSPENDED, UNKNOWN, \
    BATCH_RUNNING

from finestrino import six

from finestrino.parameter import ParameterVisibility

WORKER_STATE_DISABLED = 'disabled'
WORKER_STATE_ACTIVE = 'active'

UPSTREAM_RUNNING = 'UPSTREAM_RUNNING'
UPSTREAM_MISSING_INPUT = 'UPSTREAM_MISSING_INPUT'
UPSTREAM_FAILED = 'UPSTREAM_FAILED'
UPSTREAM_DISABLED = 'UPSTREAM_DISABLED'

_retry_policy_fields = [
    "retry_count",
    "disable_hard_timeout",
    "disable_window",
]
RetryPolicy = collections.namedtuple("RetryPolicy", _retry_policy_fields)

UPSTREAM_SEVERITY_ORDER = (
    '',
    UPSTREAM_RUNNING,
    UPSTREAM_MISSING_INPUT,
    UPSTREAM_FAILED,
    UPSTREAM_DISABLED,
)

UPSTREAM_SEVERITY_KEY = UPSTREAM_SEVERITY_ORDER.index

RPC_METHODS = {}

STATUS_TO_UPSTREAM_MAP = {
    FAILED: UPSTREAM_FAILED,
    RUNNING: UPSTREAM_RUNNING,
    BATCH_RUNNING: UPSTREAM_RUNNING,
    PENDING: UPSTREAM_MISSING_INPUT,
    DISABLED: UPSTREAM_DISABLED,
}

logger = logging.getLogger(__name__)

def rpc_method(**request_args):
    def _rpc_method(fn):
        # if request args are passed, return this function again for us as 
        # the decorator function with the request args attached.
        fn_args = inspect.getargspec(fn)

        assert not fn_args.varargs
        assert fn_args.args[0] == 'self'

        all_args = fn_args.args[1:]
        defaults = dict(zip(reversed(all_args), reversed(fn_args.defaults or ())))
        required_args = frozenset(arg for arg in all_args if arg not in defaults)
        fn_name = fn.__name__

        @functools.wraps(fn)
        def rpc_func(self, *args, **kwargs):
            actual_args = defaults.copy()
            actual_args.update(dict(zip(all_args, args)))
            actual_args.update(kwargs)

            if not all(arg in actual_args for arg in required_args):
                raise TypeError('{} takes {} arguments ({} given)'.format(
                    fn_name, len(all_args), len(actual_args)
                ))

            return self._request('/api/{}'.format(fn_name), actual_args, **request_args)

        RPC_METHODS[fn_name] = rpc_func

        return fn

    return _rpc_method

class scheduler(Config):
    retry_delay = parameter.FloatParameter(default=900.0)
    remove_delay = parameter.FloatParameter(default=600.0)
    worker_disconnect_delay = parameter.FloatParameter(default=60.0)
    state_path = parameter.Parameter(default='/var/lib/finestrino-server/state.pickle')

    batch_emails = parameter.BoolParameter(default=False, description='Send e-mails in batches rather than immediately')

    # Jobs are disabled if we see more than retry_count failures in disable_window seconds.
    # These disables last for disable_persist_seconds.
    disable_window = parameter.IntParameter(default=3600)
    retry_count = parameter.IntParameter(default=9999999999999)
    disable_hard_timeout = parameter.IntParameter(default=999999999)
    disable_persist = parameter.IntParameter(default=86400)
    max_shown_tasks = parameter.IntParameter(default=100000)
    max_graph_nodes = parameter.IntParameter(default=100000)

    record_task_history = parameter.BoolParameter(default=False)

    prune_on_get_work = parameter.BoolParameter(default=False)

    pause_enabled = parameter.BoolParameter(default=True)

    send_messages = parameter.BoolParameter(default=True)

    metrics_collector = parameter.EnumParameter(enum=MetricsCollectors, default=MetricsCollectors.default)

    def _get_retry_policy(self):
        return RetryPolicy(self.retry_count, self.disable_hard_timeout, self.disable_window)

def _get_default(x, default):
    if x is not None:
        return x
    else:
        return default 

class Worker(object):
    """ 
    Structure for tracking worker activity and keeping their references.
    """
    def __init__(self, worker_id, last_active=None):
        self.id = worker_id
        self.reference = None # reference to the worker in the real world
        self.last_active = last_active or time.time() # seconds since epoch
        self.last_get_work = None
        self.started = time.time() # seconds since epoch
        self.tasks = set() # task objects
        self.info = {}
        self.disabled = False
        self.rpc_messages = []

    def add_info(self, info):
        self.info.update(info)

    def update(self, worker_reference, get_work=False):
        if worker_reference:
            self.reference = worker_reference
        self.last_active = time.time()

        if get_work:
            self.last_get_work = time.time()

    @property
    def assistant(self):
        return self.info.get('assistant', False)

    @property
    def enabled(self):
        return not self.disabled

    @property
    def state(self):
        if self.enabled:
            return WORKER_STATE_ACTIVE
        else:
            return WORKER_STATE_DISABLED 

    def is_trivial_worker(self, state):
        """
        If it is not an assistant having only tasks that are 
        without requirements
        
        Arguments:
            state {[type]} -- [description]
        """
        if self.assistant:
            return False
        
        return all(not task.resources for task in self.get_tasks(state, PENDING))

    def get_tasks(self, state, *statuses):
        num_self_tasks = len(self.tasks)
        num_state_tasks = sum(len(state._status_tasks[status]) for status in statuses)

        if num_self_tasks < num_state_tasks:
            return six.moves.filter(lambda task: task.status in statuses, self.tasks)
        else:
            return six.moves.filter(lambda task: self.id in task.workers, state.get_active_tasks_by_status(*statuses)) 

    def prune(self, config):
        if self.last_active + config.worker_disconnect_delay < time.time():
            return True

    def add_rpc_message(self, name, **kwargs):
        # the message has the format {'name': <function_name>, 'kwargs': <function_kwargs>}
        self.rpc_messages.append({'name': name, 'kwargs': kwargs})

    def fetch_rpc_messages(self):
        messages = self.rpc_messages[:]
        del self.rpc_messages[:]
        return messages

    def __str__(self):
        return self.id  

class SimpleTaskState(object):
    """Keep track of the current state and handle persistance.

    The point of this class is to enable other ways to keep state, eg by using a database.
    
    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, state_path):
        self._state_path = state_path
        self._tasks = {}
        self._status_tasks = collections.defaultdict(dict)
        self._active_workers = {}
        self._task_batchers = {}
        self._metrics_collector = None

    def get_state(self):
        return self._tasks, self._active_workers, self._task_batchers

    def set_state(self, state):
        self._tasks, self._active_workers = state[:2]
        if len(state) >= 3:
            self._task_batchers = state[2]

    def dump(self):
        try:
            with open(self._state_path, 'wb') as fobj:
                pickle.dump(self.get_state(), fobj)
        except IOError:
            logger.warning("Failed saving scheduler state", exc_info=1)
        else:
            logger.info("Saved state in %s", self._state_path)

    def load(self):
        if os.path.exists(self._state_path):
            logger.info("Attempting to load state from %s", self._state_path)

            try:
                with open(self._state_path, 'rb') as fobj:
                    state = pickle.load(fobj)
            except BaseException:
                logger.exception("Error when loading state. Starting from empty state.")
                return 

            self.set_state(state)
            self._status_tasks = collections.defaultdict(dict)
            for task in six.itervalues(self._tasks):
                self._status_tasks[task.status][task.id] = True

        else:
            logger.info("No prior state file exists at %s. Staring with empty state", self._state_path)

    def get_worker(self, worker_id):
        return self._active_workers.setdefault(worker_id, Worker(worker_id))

    def get_active_tasks_by_status(self, *statuses):
        return itertools.chain.from_iterable( \
            six.itervalues(self._status_tasks[status]) for status in statuses)

    def get_active_workers(self, last_active_lt=None, last_get_work_gt=None):
        for worker in six.itervalues(self._active_workers):
            if last_active_lt is not None and worker.last_active >= last_active_lt:
                continue 
            
            last_get_work = worker.last_get_work

            if last_get_work_gt is not None and (
                        last_get_work is None or last_get_work <= last_get_work_gt):
                continue

            yield worker

    def set_batcher(self, worker_id, family, batcher_args, max_batch_size):
        self._task_batchers.setdefault(worker_id, {})
        self._task_batchers[worker_id][family] = (batcher_args, max_batch_size)

    def get_batcher(self, worker_id, family):
        return self._task_batchers.get(worker_id, {}).get(family, (None, 1))

    def set_batch_running(self, task, batch_id, worker_id):
        self.set_status(task, BATCH_RUNNING)
        task.batch_id = batch_id
        task.worker_running = worker_id
        task.resources_running = task.resources
        task.time_running = time.time()     

    def set_status(self, task, new_status, config=None):
        if new_status == FAILED:
            assert config is not None

        if new_status == DISABLED and task.status in (RUNNING, BATCH_RUNNING):
            return

        remove_on_failure = task.batch_id is not None and not task.batchable

        if task.status == DISABLED:
            if new_status == DONE:
                self.re_enable(task)

            # don't allow workers to override a scheduler disable
            elif task.scheduler_disable_time is not None and new_status != DISABLED:
                return

        if task.status == RUNNING and task.batch_id is not None and new_status != RUNNING:
            for batch_task in self.get_batch_running_tasks(task.batch_id):
                self.set_status(batch_task, new_status, config)
                batch_task.batch_id = None
            task.batch_id = None

        if new_status == FAILED and task.status != DISABLED:
            task.add_failure()
            self.update_metrics_task_failed(task)
            if task.has_excessive_failures():
                task.scheduler_disable_time = time.time()
                new_status = DISABLED
                self.update_metrics_task_disabled(task, config)
                if not config.batch_emails:
                    notifications.send_error_email(
                        'Luigi Scheduler: DISABLED {task} due to excessive failures'.format(task=task.id),
                        '{task} failed {failures} times in the last {window} seconds, so it is being '
                        'disabled for {persist} seconds'.format(
                            failures=task.retry_policy.retry_count,
                            task=task.id,
                            window=config.disable_window,
                            persist=config.disable_persist,
                        ))
        elif new_status == DISABLED:
            task.scheduler_disable_time = None

        if new_status != task.status:
            self._status_tasks[task.status].pop(task.id)
            self._status_tasks[new_status][task.id] = task
            task.status = new_status
            task.updated = time.time()

            if new_status == DONE:
                self.update_metrics_task_done(task)

        if new_status == FAILED:
            task.retry = time.time() + config.retry_delay
            if remove_on_failure:
                task.remove = time.time()

    def get_active_tasks(self):
        return six.itervalues(self._tasks)

    def _remove_workers_from_tasks(self, workers, remove_stakeholders=True):
        for task in self.get_active_tasks():
            if remove_stakeholders:
                task.stakeholders.difference_update(workers)

            task.workers -= workers

    def inactivate_workers(self, delete_workers):
        for worker in delete_workers:
            self._active_workers.pop(worker)

        self._remove_workers_from_tasks(delete_workers)

    def get_assistants(self, last_active_lt=None):
        return filter(lambda w: w.assistant, self.get_active_workers(last_active_lt))

    def update_metrics_task_started(self, task):
        self._metrics_collector.handle_task_started(task)

    def update_metrics_task_disabled(self, task, config):
        self._metrics_collector.handle_task_disabled(task, config)

    def update_metrics_task_failed(self, task):
        self._metrics_collector.handle_task_failed(task)

    def update_metrics_task_done(self, task):
        self._metrics_collector.handle_task_done(task)   

    def re_enable(self, task, config=None):
        task.scheduler_disable_time = None
        task.failures.clear()
        if config:
            self.set_status(task, FAILED, config)
            task.failures.clear()
     
    def get_batch_running_tasks(self, batch_id):
        assert batch_id is not None
        return [
            task for task in self.get_active_tasks_by_status(BATCH_RUNNING)
            if task.batch_id == batch_id
        ]

    def update_status(self, task, config):
        # Mark tasks with no remaining active stakeholders for deletion
        if (not task.stakeholders) and (task.remove is None) and (task.status != RUNNING):
            # We don't check for the RUNNING case, because that is already handled
            # by the fail_dead_worker_task function.
            logger.debug("Task %r has no stakeholders anymore -> might remove "
                         "task in %s seconds", task.id, config.remove_delay)
            task.remove = time.time() + config.remove_delay

        # Re-enable task after the disable time expires
        if task.status == DISABLED and task.scheduler_disable_time is not None:
            if time.time() - task.scheduler_disable_time > config.disable_persist:
                self.re_enable(task, config)

        # Reset FAILED tasks to PENDING if max timeout is reached, and retry delay is >= 0
        if task.status == FAILED and config.retry_delay >= 0 and task.retry < time.time():
            self.set_status(task, PENDING, config)

    def may_prune(self, task):
        return task.remove and time.time() >= task.remove

    def inactivate_tasks(self, delete_tasks):
        # The terminology is a bit confusing: we used to "delete" tasks when they became inactive,
        # but with a pluggable state storage, you might very well want to keep some history of
        # older tasks as well. That's why we call it "inactivate" (as in the verb)
        for task in delete_tasks:
            task_obj = self._tasks.pop(task)
            self._status_tasks[task_obj.status].pop(task)

    def fail_dead_worker_task(self, task, config, assistants):
        # If a running worker disconnects, tag all its jobs as FAILED and subject it to the same retry logic
        if task.status in (BATCH_RUNNING, RUNNING) and task.worker_running and task.worker_running not in task.stakeholders | assistants:
            logger.info("Task %r is marked as running by disconnected worker %r -> marking as "
                        "FAILED with retry delay of %rs", task.id, task.worker_running,
                        config.retry_delay)
            task.worker_running = None
            self.set_status(task, FAILED, config)
            task.retry = time.time() + config.retry_delay
 
    def get_task(self, task_id, default=None, setdefault=None):
        if setdefault:
            task = self._tasks.setdefault(task_id, setdefault)
            self._status_tasks[task.status][task.id] = task
            return task
        else:
            return self._tasks.get(task_id, default)

    def has_task(self, task_id):
        return task_id in self._tasks

class Failures(object):
    """
    This class tracks the number of failures in a given time window.
    Failures added are marked with the current timestamp, and this class counts
    the number of failures in a sliding time window ending at the present.
    """

    def __init__(self, window):
        """
        Initialize with the given window.
        :param window: how long to track failures for, as a float (number of seconds).
        """
        self.window = window
        self.failures = collections.deque()
        self.first_failure_time = None

    def add_failure(self):
        """
        Add a failure event with the current timestamp.
        """
        failure_time = time.time()

        if not self.first_failure_time:
            self.first_failure_time = failure_time

        self.failures.append(failure_time)

    def num_failures(self):
        """
        Return the number of failures in the window.
        """
        min_time = time.time() - self.window

        while self.failures and self.failures[0] < min_time:
            self.failures.popleft()

        return len(self.failures)

    def clear(self):
        """
        Clear the failure queue.
        """
        self.failures.clear()

class OrderedSet(collections.MutableSet):
    """
    Standard Python OrderedSet recipe found at http://code.activestate.com/recipes/576694/
    Modified to include a peek function to get the last element
    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def peek(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        return key

    def pop(self, last=True):
        key = self.peek(last)
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

class Task(object):
    def __init__(self, task_id, status, deps, resources=None, priority=0, family='', module=None,
                 params=None, param_visibilities=None, accepts_messages=False, tracking_url=None, status_message=None,
                 progress_percentage=None, retry_policy='notoptional'):
        self.id = task_id
        self.stakeholders = set()  # workers ids that are somehow related to this task (i.e. don't prune while any of these workers are still active)
        self.workers = OrderedSet()  # workers ids that can perform task - task is 'BROKEN' if none of these workers are active
        if deps is None:
            self.deps = set()
        else:
            self.deps = set(deps)
        self.status = status  # PENDING, RUNNING, FAILED or DONE
        self.time = time.time()  # Timestamp when task was first added
        self.updated = self.time
        self.retry = None
        self.remove = None
        self.worker_running = None  # the worker id that is currently running the task or None
        self.time_running = None  # Timestamp when picked up by worker
        self.expl = None
        self.priority = priority
        self.resources = _get_default(resources, {})
        self.family = family
        self.module = module
        self.param_visibilities = _get_default(param_visibilities, {})
        self.params = {}
        self.public_params = {}
        self.hidden_params = {}
        self.set_params(params)
        self.accepts_messages = accepts_messages
        self.retry_policy = retry_policy
        self.failures = Failures(self.retry_policy.disable_window)
        self.tracking_url = tracking_url
        self.status_message = status_message
        self.progress_percentage = progress_percentage
        self.scheduler_message_responses = {}
        self.scheduler_disable_time = None
        self.runnable = False
        self.batchable = False
        self.batch_id = None

    def __repr__(self):
        return "Task(%r)" % vars(self)

    def set_params(self, params):
        self.params = _get_default(params, {})
        self.public_params = {key: value for key, value in self.params.items() if
                              self.param_visibilities.get(key, ParameterVisibility.PUBLIC) == ParameterVisibility.PUBLIC}
        self.hidden_params = {key: value for key, value in self.params.items() if
                              self.param_visibilities.get(key, ParameterVisibility.PUBLIC) == ParameterVisibility.HIDDEN}

    # TODO(2017-08-10) replace this function with direct calls to batchable
    # this only exists for backward compatibility
    def is_batchable(self):
        try:
            return self.batchable
        except AttributeError:
            return False

    def add_failure(self):
        self.failures.add_failure()

    def has_excessive_failures(self):
        if self.failures.first_failure_time is not None:
            if (time.time() >= self.failures.first_failure_time + self.retry_policy.disable_hard_timeout):
                return True

        logger.debug('%s task num failures is %s and limit is %s', self.id, self.failures.num_failures(), self.retry_policy.retry_count)
        if self.failures.num_failures() >= self.retry_policy.retry_count:
            logger.debug('%s task num failures limit(%s) is exceeded', self.id, self.retry_policy.retry_count)
            return True

        return False

    @property
    def pretty_id(self):
        param_str = ', '.join(u'{}={}'.format(key, value) for key, value in sorted(self.public_params.items()))
        return u'{}({})'.format(self.family, param_str)

class Scheduler(object):
    """Async scheduler that can handle multiple workers, etc.

    Can be run locally or on a server (using RemoteScheduler + server.Server).    
    
    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self, config=None, resources=None, task_history_impl=None, **kwargs):
        self._config = config or scheduler(**kwargs)
        self._state = SimpleTaskState(self._config.state_path)

        if task_history_impl:
            self._task_history = task_history_impl
        elif self._config.record_task_history:
            from finestrino import db_task_history # Needs sqlalchemy, thus imported here
            self.task_history = db_task_history.DbTaskHistory()
        else:
            self._task_history = history.NopHistory()

        self._resources = resources or configuration.get_config().getintdict('resources')

        self._make_task = functools.partial(Task, retry_policy=self._config._get_retry_policy())

        self._worker_requests = {}

        self._paused = False

        if self._config.batch_emails:
            self._email_batcher = BatchNotifier()

        print("+++++ Metrics Collector %s +++++" % self._config.metrics_collector)
        self._state._metrics_collector = MetricsCollectors.get(self._config.metrics_collector)

    def load(self):
        self._state.load()

    def dump(self):
        self._state.dump()
        if self._config.batch_emails:
            self._email_batcher.send_email()

    @rpc_method()
    def announce_scheduling_failure(self, task_name, family, params, expl, owners, **kwargs):
        if not self._config.batch_emails:
            return 

        worker_id = kwargs['worker']
        batched_params, _ = self._state.get_batcher(worker_id, family)

        if batched_params:
            unbatched_params = {
                param: value
                for param, value in six.iteritems(params) \
                    if param not in batched_params
            }
        else:
            unbatched_params = params

        self._email_batcher.add_scheduling_fail(task_name, family, unbatched_params, expl, owners)

    @rpc_method()
    def add_task_batcher(self, worker, task_family, batched_args, max_batch_size=float('inf')):
        self._state.set_batcher(worker, task_family, batched_args, max_batch_size)

    @rpc_method()
    def prune(self):
        logger.debug("Starting pruning of task graph")
        self._prune_workers()
        self._prune_tasks()
        self._prune_emails()
        logger.debug("Done pruning task graph")

    def _prune_workers(self):
        remove_workers = []

        for worker in self._state.get_active_workers():
            if worker.prune(self._config):
                logger.debug("Worker %s timed out (no contact for >=%ss",
                    worker, self._config.worker_disconnect_delay)
                remove_workers.append(worker.id)

        self._state.inactivate_workers(remove_workers)

    @rpc_method(allow_null=False)
    def get_work(self, host=None, assistant=False, current_tasks=None, worker=None, **kwargs):
        if self._config.prune_on_get_work:
            self.prune()

        assert worker is not None

        worker_id = worker
        worker = self._update_worker(worker_id, 
            worker_reference={'host': host}, 
            get_work=True)

        if not worker.enabled:
            reply = {'n_pending_tasks': 0, 'running_tasks': [], 'task_id': None,
                'n_unique_pending': 0, 'worker_state': worker.state,
            }

            return reply

        print("The Old Man and the Gun")

        if assistant:
            self.add_worker(worker_id, [('assistant', assistant)])

        batched_params, unbatched_params, batched_tasks, max_batch_size = None, None, [], 1
        best_task = None
        print("Current Tasks are .... %s" % current_tasks)

        if current_tasks is not None:
            ct_set = set(current_tasks)

            for task in sorted(self._state.get_active_tasks_by_status(RUNNING), key=self._rank):
                if task.worker_running == worker_id and task.id not in ct_set:
                    best_task = task 

        if current_tasks is not None:
            # batch running tasks that were not claimed sine the last get_work .. go back in the pool
            self._reset_orphaned_batch_running_tasks(worker_id)

        greedy_resources = collections.defaultdict(int)

        worker = self._state.get_worker(worker_id)
        print("Worker is ... %s" % worker)
        print("Is Trivial Worker ???? .... %s" % worker.is_trivial_worker(self._state))

        if self._paused:
            relevant_tasks = []
        elif worker.is_trivial_worker(self._state):
            relevant_tasks = worker.get_tasks(self._state, PENDING, RUNNING)
            print("Relevant Tasks are ... %s" % relevant_tasks)

            used_resources = collections.defaultdict(int)
            greedy_workers = dict() # if there is no resources, then they can grab any task
        else:
            relevant_tasks = self._state.get_active_tasks_by_status(PENDING, RUNNING)
            used_resources = self._used_resources()
            activity_limit = time.time() - self._config.worker_disconnect_delay
            active_workers = self._state.get_active_workers(last_get_work_gt=activity_limit)
            greedy_workers = dict((worker_id, worker.info.get('workers', 1)) for worker in active_workers)

        tasks = list(relevant_tasks)
        #print("Tasks List is ... %s" %tasks)
        tasks.sort(key=self._rank, reverse=True)
        #print("Sorted Tasks are ... %s" %tasks)

        for task in tasks:
            print("******** Pending Tasks in Scheduler Queue are ... %s (%s) , resources &&&&&&&&&&&&&&&&&&&&" % (task.id, task.status))

            if (best_task and batched_params and task.family == best_task.family and 
                len(batched_tasks) < max_batch_size and task.is_batchable() and all(
                    task.params.get(name) == value for name, value in unbatched_params.items()
                ) and task.resources == best_task.resources and self._schedulable(task)):
                
                for name, params in batched_params.items():
                    params.append(task.params.get(name))
                
                batched_tasks.append(task)

            if best_task:
                continue

            if task.status == RUNNING and (task.worker_running in greedy_workers):
                greedy_workers[task.worker_running] -= 1

                for resource, amount in six.iteritems((getattr(task, 'resources_running', task.resources) or {})):
                    greedy_resources[resource] += amount

            print("Self._Schedulable(task) is .... %s" % self._schedulable(task))
            print("Task Resources are ... %s (greedy %s)" % (task.resources, greedy_resources))
            print("self._has_resources ???? %s" % self._has_resources(task.resources, greedy_resources))

            if self._schedulable(task) and self._has_resources(task.resources, greedy_resources):
                in_workers = (assistant and task.runnable) or worker_id in task.workers
                print("In Workers ... %d" % in_workers)
                print( "Has Resources %d" %self._has_resources(task.resources, used_resources))
                #return
                  
                if in_workers and self._has_resources(task.resources, used_resources):
                    best_task = task
                    batch_param_names, max_batch_size = self._state.get_batcher(worker_id, task.family)

                    if batch_param_names and task.is_batchable():
                        print("Inside IoTs")
                        #return 

                        try:
                            batched_params = {
                                name: [task.params[name]] for name in batch_param_names
                            }
                            unbatched_params = {
                                name: value for name, value in task.params.items()
                                if name not in batched_params 
                            }
                            batched_tasks.append(task)
                        except KeyError:
                            batched_params, unbatched_params = None, None
                else:
                    print("Run Forest Run ...")
                    #return 

                    workers = itertools.chain(task.workers, [worker_id]) if assistant else task.workers

                    for task_worker in workers:
                        if greedy_workers.get(task_worker, 0) > 0:
                            # use up a worker 
                            greedy_workers[task_worker] -= 1

                            # keep track of the resources used in greedy scheduling
                            for resource, amount in six.iteritems(task.resources or {}):
                                greedy_resources[resource] += amount

                            break

        reply = self.count_pending(worker_id)
        print("Reply = %s" % reply)
        
        print("Batched Tasks Length === %d" %(len(batched_tasks)))
        print("Best Task is === %s" %best_task)

        if len(batched_tasks) > 1:
            batch_string = '|'.join(task.id for task in batched_tasks)
            batch_id = hashlib.md5(batch_string.encode('utf-8')).hexdigest()

            for task in batched_tasks:
                self._state.set_batch_running(task, batch_id, worker_id)

            combined_params = best_task.params.copy()
            combined_params.update(batched_params)

            reply['task_id'] = None
            reply['task_family'] = best_task.family
            reply['task_module'] = getattr(best_task, 'module', None)
            reply['task_params'] = combined_params
            reply['batch_id'] = batch_id
            reply['batch_task_ids'] = [task.id for task in batched_tasks]
        
        elif best_task:
            print("Inside Best Task !!!")
            print("Best Task is ... %s" %best_task)
            #return 

            self.update_metrics_task_started(best_task)
            self._state.set_status(best_task, RUNNING, self._config)
            best_task.worker_running = worker_id
            best_task.resources_running = best_task.resources.copy()
            best_task.time_running = time.time()
            self._update_task_history(best_task, RUNNING, host=host)

            reply['task_id'] = best_task.id
            reply['task_family'] = best_task.family
            reply['task_module'] = getattr(best_task, 'module', None)
            reply['task_params'] = best_task.params

        else:
            reply['task_id'] = None

        print("7777777 Reply is %s" % reply)
        
        return reply 

    @rpc_method(attempts=1)
    def ping(self, **kwargs):
        print("Some one is pinging the scheduler")
        worker_id = kwargs["worker"]
        worker = self._update_worker(worker_id)

        return {"rpc_messages": worker.fetch_rpc_messages()} 

    @rpc_method()
    def add_task(self, task_id=None, status=PENDING, runnable=True,
                 deps=None, new_deps=None, expl=None, resources=None,
                 priority=0, family='', module=None, params=None, param_visibilities=None, accepts_messages=False,
                 assistant=False, tracking_url=None, worker=None, batchable=None,
                 batch_id=None, retry_policy_dict=None, owners=None, **kwargs):
        """
        * add task identified by task_id if it doesn't exist
        * if deps is not None, update dependency list
        * update status of task
        * add additional workers/stakeholders
        * update priority when needed
        """
        assert worker is not None
        worker_id = worker
        worker = self._update_worker(worker_id)

        resources = {} if resources is None else resources.copy()

        if retry_policy_dict is None:
            retry_policy_dict = {}

        retry_policy = self._generate_retry_policy(retry_policy_dict)
        #print("++++++ Retry Policy : %s" % retry_policy)

        print("++++ Is Worker Enabled ? %s ++++" % worker.enabled)
        if worker.enabled:
            _default_task = self._make_task(
                task_id=task_id, status=PENDING, deps=deps, resources=resources,
                priority=priority, family=family, module=module, params=params, param_visibilities=param_visibilities,
            )
        else:
            _default_task = None

        print("++++++ Default Task is %s +++++++++" % _default_task)
        task = self._state.get_task(task_id, setdefault=_default_task)

        print("TASK STATUS IS %s" % task.status)
        if task is None or (task.status != RUNNING and not worker.enabled):
            return

        # for setting priority, we'll sometimes create tasks with unset family and params
        if not task.family:
            task.family = family
        if not getattr(task, 'module', None):
            task.module = module
        if not getattr(task, 'param_visibilities', None):
            task.param_visibilities = _get_default(param_visibilities, {})
        if not task.params:
            task.set_params(params)

        print("&&&& Task Family %s &&&&" % task.family)
        print("&&&& Task Module %s &&&&" % task.module)
        print("&&&& Param Visibility is ... %s &&&&&" % task.param_visibilities)
        print("&&&& Task Params is ... %s &&&&&" % task.params)

        if batch_id is not None:
            task.batch_id = batch_id
        print("&&&& Task Batch ID is ... %s &&&&&" % task.batch_id)
        
        if status == RUNNING and not task.worker_running:
            task.worker_running = worker_id
            if batch_id:
                # copy resources_running of the first batch task
                batch_tasks = self._state.get_batch_running_tasks(batch_id)
                task.resources_running = batch_tasks[0].resources_running.copy()
            task.time_running = time.time()

        if accepts_messages is not None:
            task.accepts_messages = accepts_messages

        if tracking_url is not None or task.status != RUNNING:
            task.tracking_url = tracking_url
            if task.batch_id is not None:
                for batch_task in self._state.get_batch_running_tasks(task.batch_id):
                    batch_task.tracking_url = tracking_url
        print("&&&& Tracking URL ... %s &&&&&" % task.tracking_url)

        if batchable is not None:
            task.batchable = batchable

        if task.remove is not None:
            task.remove = None  # unmark task for removal so it isn't removed after being added

        if expl is not None:
            task.expl = expl
            if task.batch_id is not None:
                for batch_task in self._state.get_batch_running_tasks(task.batch_id):
                    batch_task.expl = expl

        task_is_not_running = task.status not in (RUNNING, BATCH_RUNNING)
        task_started_a_run = status in (DONE, FAILED, RUNNING)
        running_on_this_worker = task.worker_running == worker_id
        if task_is_not_running or (task_started_a_run and running_on_this_worker) or new_deps:
            # don't allow re-scheduling of task while it is running, it must either fail or succeed on the worker actually running it
            if status != task.status or status == PENDING:
                # Update the DB only if there was a acctual change, to prevent noise.
                # We also check for status == PENDING b/c that's the default value
                # (so checking for status != task.status woule lie)
                self._update_task_history(task, status)

            print("_____ Task is   _____ %s" % task)
            print("_____ Status is _____ %s" % status)
            print("_____ Config is _____ %s" % self._config)

            self._state.set_status(task, PENDING if status == SUSPENDED else status, self._config)

        if status == FAILED and self._config.batch_emails:
            batched_params, _ = self._state.get_batcher(worker_id, family)
            if batched_params:
                unbatched_params = {
                    param: value
                    for param, value in six.iteritems(task.params)
                    if param not in batched_params
                }
            else:
                unbatched_params = task.params
            try:
                expl_raw = json.loads(expl)
            except ValueError:
                expl_raw = expl

            self._email_batcher.add_failure(
                task.pretty_id, task.family, unbatched_params, expl_raw, owners)
            if task.status == DISABLED:
                self._email_batcher.add_disable(
                    task.pretty_id, task.family, unbatched_params, owners)

        if deps is not None:
            task.deps = set(deps)

        if new_deps is not None:
            task.deps.update(new_deps)

        if resources is not None:
            task.resources = resources

        if worker.enabled and not assistant:
            task.stakeholders.add(worker_id)

            # Task dependencies might not exist yet. Let's create dummy tasks for them for now.
            # Otherwise the task dependencies might end up being pruned if scheduling takes a long time
            for dep in task.deps or []:
                t = self._state.get_task(dep, setdefault=self._make_task(task_id=dep, status=UNKNOWN, deps=None, priority=priority))
                t.stakeholders.add(worker_id)

        self._update_priority(task, priority, worker_id)

        # Because some tasks (non-dynamic dependencies) are `_make_task`ed
        # before we know their retry_policy, we always set it here
        task.retry_policy = retry_policy

        if runnable and status != FAILED and worker.enabled:
            task.workers.add(worker_id)
            self._state.get_worker(worker_id).tasks.add(task)
            task.runnable = runnable
   
    def add_worker(self, worker, info, **kwargs):
        self._state.get_worker(worker).add_info(info)

    def _prune_tasks(self):
        assistant_ids = {w.id for w in self._state.get_assistants()}

        remove_tasks = []

        for task in self._state.get_active_tasks():
            self._state.fail_dead_worker_task(task, self._config, assistant_ids)
            self._state.update_status(task, self._config)

            if self._state.may_prune(task):
                logger.debug("Removing task %r", task.id)
                remove_tasks.append(task.id)

            self._state.inactivate_tasks(remove_tasks)         

    def _prune_emails(self):
        if self._config.batch_emails:
            self._email_batcher.update()  

    def _update_worker(self, worker_id, worker_reference=None, get_work=False):
        # Keep track of whenever the worker was last active.
        # For convenience also return the worker object.
        worker = self._state.get_worker(worker_id)
        worker.update(worker_reference, get_work=get_work)

        return worker

    def _rank(self, task):
        """ 
        Return worker's rank function for task scheduling
        """
        return task.priority, -task.time

    def _reset_orphaned_batch_running_tasks(self, worker_id):
        running_batch_ids = {
            task.batch_id 
            for task in self._state.get_active_tasks_by_status(RUNNING)
            if task.worker_running == worker_id
        }

        orphaned_tasks = [
            task for task in self._state.get_active_tasks_by_status(BATCH_RUNNING)
            if task.worker_running == worker_id and task.batch_id not in running_batch_ids
        ]

        for task in orphaned_tasks:
            self._state.set_status(task, PENDING)

    @rpc_method()
    def count_pending(self, worker):
        worker_id, worker = worker, self._state.get_worker(worker)

        num_pending, num_unique_pending, num_pending_last_scheduled = 0, 0, 0
        running_tasks = []

        upstream_status_table = {}
        for task in worker.get_tasks(self._state, RUNNING):
            if self._upstream_status(task.id, upstream_status_table) == UPSTREAM_DISABLED:
                continue

            # Return a list of currently running tasks to the client
            other_worker = self._state.get_worker(task.worker_running)

            if other_worker is not None:
                more_info = {'task_id': task.id, 'worker': str(other_worker)}
                more_info.update(other_worker.info)
                running_tasks.append(more_info) 

        for task in worker.get_tasks(self._state, PENDING, FAILED):
            if self._upstream_status(task.id, upstream_status_table) == UPSTREAM_DISABLED:
                continue

            num_pending += 1
            num_unique_pending += int(len(task.workers) == 1)
            num_pending_last_scheduled += int(task.workers.peek(last=True) == worker_id)

        return {
            'n_pending_tasks': num_pending, 
            'n_unique_pending': num_unique_pending,
            'n_pending_last_scheduled': num_pending_last_scheduled,
            'worker_state': worker.state,
            'running_tasks': running_tasks,
        }

    def _used_resources(self):
        used_resources = collections.defaultdict(int)
        if self._resources is not None:
            for task in self._state.get_active_tasks_by_status(RUNNING):
                resources_running = getattr(task, "resources_running", task.resources)
                if resources_running:
                    for resource, amount in six.iteritems(resources_running):
                        used_resources[resource] += amount
        return used_resources

    def _schedulable(self, task):
        if task.status != PENDING:
            return False
        for dep in task.deps:
            dep_task = self._state.get_task(dep, default=None)
            if dep_task is None or dep_task.status != DONE:
                return False
        return True

    def _has_resources(self, needed_resources, used_resources):
        if needed_resources is None:
            return True

        available_resources = self._resources or {}
        for resource, amount in six.iteritems(needed_resources):
            if amount + used_resources[resource] > available_resources.get(resource, 1):
                return False
        
        return True

    def _update_task_history(self, task, status, host=None):
        try:
            if status == DONE or status == FAILED:
                successful = (status == DONE)
                self._task_history.task_finished(task, successful)
            elif status == PENDING:
                self._task_history.task_scheduled(task)
            elif status == RUNNING:
                self._task_history.task_started(task, host)
        except BaseException:
            logger.warning("Error saving Task history", exc_info=True)

    @property
    def task_history(self):
        # Used by server.py to expose the calls
        return self._task_history

    @rpc_method()
    def update_metrics_task_started(self, task):
        self._state._metrics_collector.handle_task_started(task)

    def _upstream_status(self, task_id, upstream_status_table):
        if task_id in upstream_status_table:
            return upstream_status_table[task_id]
        elif self._state.has_task(task_id):
            task_stack = [task_id]

            while task_stack:
                dep_id = task_stack.pop()
                dep = self._state.get_task(dep_id)
                if dep:
                    if dep.status == DONE:
                        continue
                    if dep_id not in upstream_status_table:
                        if dep.status == PENDING and dep.deps:
                            task_stack += [dep_id] + list(dep.deps)
                            upstream_status_table[dep_id] = ''  # will be updated postorder
                        else:
                            dep_status = STATUS_TO_UPSTREAM_MAP.get(dep.status, '')
                            upstream_status_table[dep_id] = dep_status
                    elif upstream_status_table[dep_id] == '' and dep.deps:
                        # This is the postorder update step when we set the
                        # status based on the previously calculated child elements
                        status = max((upstream_status_table.get(a_task_id, '')
                                      for a_task_id in dep.deps),
                                     key=UPSTREAM_SEVERITY_KEY)
                        upstream_status_table[dep_id] = status

    
            return upstream_status_table[dep_id]

    def _generate_retry_policy(self, task_retry_policy_dict):
        retry_policy_dict = self._config._get_retry_policy()._asdict()
        print("+++ Retry Policy Dict +++ %s" %retry_policy_dict)

        retry_policy_dict.update({k: v for k, v in six.iteritems(task_retry_policy_dict) if v is not None})
        print("+++ Retry Policy Dict 2 +++ %s" %retry_policy_dict)
        
        return RetryPolicy(**retry_policy_dict)

    def _update_priority(self, task, prio, worker):
        """
        Update priority of the given task.
        Priority can only be increased.
        If the task doesn't exist, a placeholder task is created to preserve priority when the task is later scheduled.
        """
        task.priority = prio = max(prio, task.priority)
        for dep in task.deps or []:
            t = self._state.get_task(dep)
            if t is not None and prio > t.priority:
                self._update_priority(t, prio, worker)
