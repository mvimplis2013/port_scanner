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
from finestrino.task import Config
from finestrino import parameter

from finestrino import task_history as history

from finestrino.batch_notifier import BatchNotifier

from finestrino.task_status import DISABLED, DONE, FAILED, \
    PENDING, RUNNING, \
    SUSPENDED, UNKNOWN, \
    BATCH_RUNNING

from finestrino import six

_retry_policy_fields = [
    "retry_count",
    "disable_hard_timeout",
    "disable_window",
]
RetryPolicy = collections.namedtuple("RetryPolicy", _retry_policy_fields)

RPC_METHODS = {}

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
                raise TypeError('{} takes {} arguments ({} given)'.fomrat(
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
            return six.moves.filter(lambda task: self.id in task.workers, state.get_active_tasksby_statuses(*statuses)) 

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

    def get_state(self):
        return self._tasks, self._active_workers, self._task_batchers

    def get_worker(self, worker_id):
        return self._active_workers.setdefault(worker_id, Worker(worker_id))

    def get_active_tasks_by_status(self, *statuses):
        return itertools.chain.from_iterable( \
            six.itervalues(self._status_tasks[status]) for status in statuses)

class Task(object):
    """
    
    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, task_id, status, deps, resources=None, priority=0, 
        family='', module=None, params=None, param_visibilities=None,
        accepts_messages=False, tracking_url=None, status_message=None,
        progress_percentage=None, retry_policy='notoptional'):
        self.id = task_id

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
            self.task_history = db_task_history/DbTaskHistory()
        else:
            self._task_history = history.NopHistory()

        self.resources = resources or configuration.get_config().getintdict('resources')

        self._make_task = functools.partial(Task, retry_policy=self._config._get_retry_policy())

        self._worker_requests = {}

        self._paused = False

        if self._config.batch_emails:
            self._email_batcher = BatchNotifier()

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

        for worker in self._state.get_active_wokers():
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
            worker_reference={'host': host}, get_work=True)

        if not worker.enabled:
            reply = {'n_pending_taks': 0, 'running_tasks': [], 'task_id': None,
                'n_unique_pending': 0, 'worker_state': worker.state,
            }

            return reply

        if assistant:
            self.add_worker(worker_id, [('assistant', assistant)])

        batched_params, unbatched_params, batched_tasks, max_batch_size = \
            None, None, [], 1
        best_task = None
        if current_tasks is not None:
            ct_test = set(current_tasks)

            for task in sorted(self._state.get_active_tasks_by_status(RUNNING) \
                , key=self._rank):
                if task.worker_running == worker_id and task.id not in ct_test:
                    best_task = task 

        if current_tasks is not None:
            # batch running tasks that were not claimed sine the last get_work .. go back in the pool
            self._reset_orphaned_batch_running_tasks(worker_id)

        greedy_resources = collections.defaultdict(int)

        worker = self._state.get_worker(worker_id)

        if self._paused:
            relevant_tasks = []
        elif worker.is_trivial_worker(self._state):
            pass
        else:
            pass 
    

    @rpc_method()
    def add_task(self, task_id=None, status=PENDING, runnable=True, 
        deps=None, new_deps=None, expl=None, resources=None,priority=0,
        family='', module=None, params=None, param_visibilities=None, accepts_messages=False,
        assistant=False, tracking_url=None, worker=None, batchable=None, batch_id=None,
        retry_policy_dict=None, owners=None, **kwargs):
        """ 
        Add task identified by task_id if it doesn't already exists. 
        If deps is NOT None, update dependency list
        update status of task
        add additional workers/ stakeholders
        update priority when needed
        """
        assert worker is not None
        worker_id = worker
        worker = self._update_worker(worker_id) 

        resources = {} if resources is None else resources.copy() 

    def add_worker(self, worker, info, **kwargs):
        self._state.get_worker(worker).add_info(info)

    def _prune_tasks(self):
        assistant_ids = {w.id for w in self._state.get_active_assistants()}

        remove_tasks = []

        for task in self._state.get_active_tasks():
            self._state.fail_dead_worher_task(task, self._config, assistant_ids)
            self._state.update_status(task, self._config)

            if self._state.may_prune(task):
                logger.debug("Removing task %r", task.id)
                remove_tasks.append(task.id)

            self._state.inactivate_tasks(remove_tasks)           

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
