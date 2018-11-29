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

class TaskException(Exception):
    pass
    
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

class Worker(object):
    """Worker object communicates with a scheduler.

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
            worker_id = 'Worker(%s)' % ', '.join(['%s=%s' % (k, v) for k, v in self._worker_info])

        self._config = worker(**kwargs)        

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

if __name__ == "__main__":
    w = Worker()
    

