"""The worker communicates with the scheduler and does two(2) things:

1) Sends all tasks that has to be run 
2) Get tasks from the scheduler that should be run

When running in LOCAL mode, the worker tals directly to a 
:py:class:`~finestrino.scheduler.Scheduler` instance.

When we run a central server, the worker will talk to the scheduler using a
:py:class:`~finestrino.rpc.RemoteScheduler' instance.
"""

import collections
import getpass
import importlib
import logging
import multiprocessing
import os
import signal
import subprocess
import sys
import contextlib

try:
    import Queue
except ImportError:
    import queue as Queue

import random
import socket
import threading
import time
import traceback
import types

from finestrino import six
from finestrino.scheduler import Scheduler
from finestrino.task import Task, Config
from finestrino.parameter import FloatParameter, BoolParameter, IntParameter, OptionalParameter
from finestrino import notifications 

from finestrino.event import Event

logger = logging.getLogger("finestrino-interface")

_WAIT_INTERVAL_EPS = 0.00001

def _is_external(task):
    return task.run is None or task.run == NotImplemented

class TaskException(Exception):
    pass
    
class KeepAliveThread(threading.Thread):
    """ 
    Periodically tell the scheduler that the worker still lives.
    """
    def __init__(self, scheduler, worker_id, ping_interval, rpc_message_callback):
        super(KeepAliveThread, self).__init__()
        self._should_stop = threading.Event()
        self._scheduler = scheduler
        self._worker_id = worker_id
        self._ping_interval = ping_interval
        self._rpc_message_callback = rpc_message_callback

    def stop(self):
        self._should_stop.set()

    def run(self):
        while True:
            self._should_stop.wait(self._ping_interval)
            
            if self._should_stop.is_set():
                logger.info("Worker %s was stopped. Shutting down Keep-Alive thread" % self._worker_id)
                break;

            with fork_lock:
                response = None
                try:
                    response = self._scheduler.ping(worker=self._worker_id)
                except BaseException: # http.BadStatusLine:
                    logger.warning("Failed pinging scheduler")

                # handle rpc messages
                if response:
                    for message in response["rpc_messages"]:
                        self._rpc_message_callback(message)

class SingleProcessPool(object):
    """
    Dummy process pool for using a single processor.

    Imitates the api of multiprocessing. Pool using single-processor. 
    """
    def apply_async(self, function, args):
        return function(*args)

    def close(self):
        pass

    def join(self):
        pass
    
class DequeQueue(collections.deque):
    """
    Dequeue wrapper implementing the Queue interface 
    """
    def put(self, obj, block=None, timeout=None):
        return self.append(obj)

    def get(self, block=None, timeout=None):
        try:
            return self.pop()
        except IndexError:
            raise QueueEmpty
    
def check_complete(task, out_queue):
    """
    Checks if task is complete, puts the result to out_queue 
    """
    logger.debug("Checking if %s is complete !" , task)

    try:
        is_complete = task.complete()
    except Exception:
        is_complete = TracebackWrapper(traceback.format_exc())

    out_queue.put((task, is_complete))
    
class worker(Config):
    # NOTE: `section.config-variable` in the config_path argument is deprecated in favor of `worker.config-variable`
    ping_interval = FloatParameter(default=1.0, 
        config_path=dict(section='core', name='worker-ping-interval'))

    keep_alive = BoolParameter(default=False,
        config_path=dict(section='core', name='worker-keep-alive'))

    count_uniques = BoolParameter(default=False, 
        config_path=dict(section='core', name='worker-count-uniques'),
        description='worker-count-uniques means that we will keep a ' 
        'worker alive only if it has a unique pending task,as well as '
        'having keep-alive true')

    count_last_scheduled = BoolParameter(default=False,
        description='Keep a worker alive only if there are '
        'pending tasks which it was the last to schedule.')

    wait_interval = FloatParameter(default=1.0,
        config_path=dict(section='core', name='worker-wait-interval'))

    wait_jitter = FloatParameter(default=5.0)

    max_reschedules = IntParameter(default=1,
        config_path=dict(section='core', name='worker-max-reschedules'))

    timeout = IntParameter(default=0,
        config_path=dict(section='core', name='worker-timeout'))

    task_limit = IntParameter(default=None, 
        config_path=dict(section='core', name='worker-task-limit'))

    retry_external_tasks = BoolParameter(default=False,
        config_path=dict(section='core', name='retry-external-tasks'),
        description='If True, incomplete external tasks will be retested '
        'for completion while finestrino is running.')

    send_failure_email = BoolParameter(default=True,
        description='If True, send e-mails directly from the worker on failure')

    no_install_shutdown_handler = BoolParameter(default=False,
        description='If True, the SIGUSR1 shutdown handler will '
        'NOT be install on the worker')

    check_unfulfilled_deps = BoolParameter(default=True,
        description='If True, check for completeness of dependencies before '
        'running a task')

    force_multiprocessing = BoolParameter(default=False,
        description='If True, use multiprocessing also when '
        'running a task')

    task_process_context = OptionalParameter(default=None, 
        description='If set to a fully qualified name, the class wil be '
        'instantiated with a TaskProcess as its constructor parameter and '
        'applied as a context manager around its run() call, so this '
        'can be used for obtaining high level customizable monitoring or '
        'logging of each individual Task run.')
    
def rpc_message_callback(fn):
    fn.is_rpc_message_callback = True
    return fn

class Worker(object):
    """
    Worker object communicates with a scheduler.

    Simple class that talks to a scheduler and:

    * tells the scheduler what it has to do + its dependencies
    * asks for sstuff to do (pulls it in a loop and runs it)
    
    Arguments:
        object {[type]} -- [description]
    """
    def __init__(self, scheduler=None, worker_id=None, worker_processes=1, assistant=False, **kwargs):
        if scheduler is None:
            scheduler = Scheduler()

        self.worker_processes = int(worker_processes)
        self._worker_info = self._generate_worker_info()

        if not worker_id:
            worker_id = 'worker(%s)' % ', '.join(['%s=%s' % (k, v) for k, v in self._worker_info])

        self._config = worker(**kwargs)

        assert self._config.wait_interval >= _WAIT_INTERVAL_EPS, "[worker] wait_interval must be positive"        
        assert self._config.wait_jitter >= 0.0 , "[worker] wait_jitter must be equal or greater than zero"

        self._id = worker_id
        self._scheduler = scheduler
        self._assistant = assistant
        self._stop_requesting_work = False

        self.host = socket.gethostname()
        self._scheduled_tasks = {}
        self._suspended_tasks = {}
        self._batch_running_tasks = {}
        self._batch_families_sent = set()

        self._first_task = None

        self.add_succeeded = True
        self.run_succeeded = True

        self.unfulfilled_counts = collections.defaultdict(int)

        if not self._config.no_install_shutdown_handler:
            try: 
                signal.signal(signal.SIGUSR1, self.handle_interrupt)
                signal.siginterrupt(signal.SIGUSR1, False)
            except AttributeError:
                pass

        # Keep info about what tasks are running (coule be in other processes)
        self._task_result_queue = multiprocessing.Queue()
        self._running_tasks = {}

        # Stuff for execution summary
        self._add_task_history = []
        self._get_work_response_history = []

    def _generate_worker_info(self):
        # Generate as much info as possible about the worker.
        # Some of these calls might not be available on all OS's
        args = [
            ('salt', '%09d' % random.randrange(0, 999999999)),
            ('workers', self.worker_processes)]

        try:
            args += [('host', socket.gethostname())]
        except BaseException:
            pass

        try:
            args += [('username', getpass.getuser())]
        except BaseException:
            pass

        try:
            args += [('pid', os.getpid())]
        except BaseException:
            pass

        try: 
            sudo_user = os.getenv("SUDO_USER")
            if sudo_user:
                args.append(('sudo_user', sudo_user))
        except BaseException:
            pass

        return args

    def _handle_rpc_message(self, message):
        logger.info("Worker %s got message %s" % (self._id, message))

        # the message is a dict {'name': <function-name>, 'kwargs': <function-kwargs>}
        name = message["name"]
        kwargs = message["kwargs"]

        # find the function and check if it is callable and configured to work 
        # as a message callback
        func = getattr(self, name, None)
        tpl = (self._id, name)

        if not callable(func):
            logger.error("Worker %s has no function '%s'" % tpl)
        elif not getattr(func, "is_rpc_message_callback", False):
            logger.error("Worker %s function '%s' is not available as rpc message callback" % tpl)
        else: 
            logger.info("Worker %s successfully dispatched rpc message to function '%s'" % tpl)
            func(**kwargs)

    @rpc_message_callback
    def set_worker_processes(self, n):
        # set the new value
        self.worker_processes = max(1, n)

        # tell the scheduler
        self._scheduler.add_worker(self._id, {'workers': self.worker_processes})
    
    def _add(self, task, is_complete):
        if self._config.task_limit is not None and len(self._scheduled_tasks) >= self._config.task_limit:
            logger.warning("Will not run %s or any dependencies due to exceed task-limit of %d", task, self._config.task_limit)
            deps = None
            status = UNKNOWN
            runnable = False 
        else:
            formatted_traceback = None

            try:
                self._check_complete_value(is_complete)
            except KeyboardInterrupt:
                raise
            except AsyncCompletionException as ex:
                formatted_traceback = ex.trace
            except BaseException:
                formatted_traceback = traceback.format_exc()

            if formatted_traceback is not None:
                self.add_succeeded = False
                self._log_complete_error(task, formatted_traceback)
                task.trigger_event(Event.DEPENDENCY_MISSING, task)
                self._email_complete_error(task, formatted_traceback)

                deps = None
                status = UNKNOWN
                runnable = False

            elif is_complete:
                deps = None
                status = DONE
                runnable = False
                task.trigger_event(Event.DEPENDENCY_PRESENT, task)

            elif _is_external(task):
                deps = None
                status = PENDING
                runnable = self._config.retry_external_tasks
                task.trigger_event(Event.DEPENDENCY_MISSING, task)
                logger.warning("Data for %s does not exists (yet ?). "
                    "The task is an external data dependency, so it cannot "
                    "run from this finestrino process.", task)

            else:
                try:
                    deps = task.deps()
                    self._add_task_batcher(task)
                except Exception as ex:
                    formatted_traceback = traceback.format_exc()
                    self.add_succeeded = False
                    self._log_dependency_error(task, formatted_traceback)
                    task.trigger_event(Event.BROKEN_TASK, task, ex)
                    self._email_dependency_error(task, formatted_traceback)
                    deps = None
                    status = UNKNOWN
                    runnable = False
                else:
                    status = PENDING
                    runnable = True

            if task.disabled:
                status = DISABLED

            if deps:
                for d in deps:
                    self._validate_dependency(d)
                    task.trigger_event(Event.DEPENDENCY_DISCOVERED, task, d)
                    yield d # return additional tasks to add

                deps = [d.task_id for d in deps]

        self._scheduled_tasks[task.task_id] = task
        self._add_task(
            worker = self.id,
            task_id = task.task_id,
            status = status,
            deps = deps,
            runnable = runnable,
            priority = task.priority,
            resources = task.process_resources(),
            params = task.to_str_params(),
            family = task.task_family,
            module = task.task_module,
            batchable = task.batchable,
            retry_policy_dict = get_retry_policy_dict(task),
            accepts_messages = task.accepts_messages, 
        )

    def add(self, task, multiprocess=False, processes=0):
        """ 
        Add a Task for the worker to check and possibly schedule and run.

        Returns True if task and its dependencies were successfully scheduled or completed before.
        """
        if self._first_task is None and hasattr(task, 'task_id'):
            self._first_task = task.task_id
        
        self.add_succeeded = True

        if multiprocess:
            queue = multiprocessing.Manager().Queue()
            pool = multiprocessing.Pool(processes=processes if processes > 0 else None)
        else:
            queue = DequeQueue()
            pool = SingleProcessPool()

        self._validate_task(task)

        pool.apply_async(check_complete, [task, queue])

        # we track queue size ourselves because len(queue) wont work for multiprocessing
        queue_size = 1
        try:
            seen = {task.task_id}

            while queue_size:
                current = queue.get()
                queue_size -= 1;

                item, is_complete = current

                for next in self._add(item, is_complete):
                    if next.task_id not in seen:
                        self._validate_task(next)
                        seen.add(next.task_id)
                        pool.apply_async(check_complete, [next, queue])
                        queue_size += 1
        except (KeyboardInterrupt, TaskException):
            raise
        except Exception as ex:
            self.add_succeeded = False
            formatted_traceback = traceback.format_exc()
            self._log_unexpected_error(task)
            task.trigger_event(Event.BROKEN_TASK, task, ex)
            self._email_unexpected_error(task, formatted_traceback)
            raise
        finally:
            pool.close()
            pool.join()

        return self.add_succeeded         

    def _check_complete_value(self, is_complete):
        if is_complete not in (True, False):
            if isinstance(is_complete, TracebackWrapper):
                raise AsynchCompletionException(is_complete.trace)

            raise Exception("Return value of Task.complete() must be boolean (was %s)" % is_complete )

    def __enter__(self):
        """
        Start the KeepAliveThread. 
        """
        self._keep_alive_thread = KeepAliveThread(
            self._scheduler, self._id, self._config.ping_interval,
            self._handle_rpc_message)

        self._keep_alive_thread.deamon = True
        self._keep_alive_thread.start()

        return self

    def __exit__(self, type, value, traceback):
        """ 
        Stop the KeepAliveThread and kill still running tasks.
        """
        self._keep_alive_thread.stop()
        self._keep_alive_thread.join()

        for task in self._running_tasks.values():
            if task.is_alive():
                task.terminate()

        return False

    def _validate_task(self, task):
        if not isinstance(task, Task):
            raise TaskException("Cannot schedule non-task %s" % task)

        if not task.initialized():
            raise TaskException("Task of class %s not initialized. Did you override __init__ and forget to call super(...).__init__ ?")

    def _log_unexpected_error(self, task):
        logger.exception("Finestrino unexpected framework error while scheduling %s", task)            

    def _log_dependency_error(self, task, tb):
        log_msg = "Will not run {task} or any dependencies due to an error in deps() method:\n{tb}".format(task=task, tb=tb)
        logger.warning(log_msg)

    def _email_dependency_error(self, task, formatted_traceback):
        self._announce_scheduling_failure(task, formatted_traceback)

        if self._config.send_failure_email:
            self._email_error(task, formatted_traceback, 
                subject="Finestrino: {task} failed scheduling. Host: {host}",
                headline="Will not run {task} or any dependencies due to error in deps() method",
            )

    def _email_unexpected_error(self, task, formatted_traceback):
        # this sends even if failure e-mails are disabled, as they may indicate 
        # a more severe failure that may not reach other alerting methods such as 
        # a scheduler batch notification.
        self._email_error(task, formatted_traceback, 
            subject = "Finestrino: Framework error while scheduling Task {task}. HostL: {host}",
                headline = "Finestrino framework error",
        )

    def _email_error(self, task, formatted_traceback, subject, headline):
        formatted_subject = subject.format(task=task, host=self.host)
        formatted_headline = headline.format(task=task, host=self.host)
        command = subprocess.list2cmdline(sys.argv)
        message = notifications.format_task_error(
            formatted_headline, task, command, formatted_traceback
        )
        notifications.send_error_email(formatted_subject, message, task.owner_email)

    def _announce_scheduling_failure(self, task, expl):
        try: 
            self._scheduler.announce_scheduling_failure(
                worker = self._id, 
                task_name = str(task),
                family = task.task_family,
                params = task.to_str_params(only_significant=True),
                expl = expl, 
                owners = task._owner_list(),
            )
        except Exception:
            formatted_traceback = traceback.format_exc()
            self._email_unexpected_error(task, formatted_traceback)
            raise
