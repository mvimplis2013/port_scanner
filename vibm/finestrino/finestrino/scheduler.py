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
        self._task_tachers = {}

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
