def _WorkerSchedulerFactory(object):

    def create_local_scheduler(self):
        return scheduler.Scheduler(prune_on_get_work=True, record_task_history=False)

    def create_worker(self, scheduler, worker_processes, assistant=False):
        return worker.Worker(self, scheduler, worker_processes=worker_processes, assistant=assistant)

def _schedule_and_run(tasks, worker_scheduler_factory=None, override_defaults=None):
    """True if all tasks and their dependencies were successfully run
    """
    if worker_scheduler_factory is None:
        worker_scheduler_factory = _WorkerSchedulerFactory()

def build(tasks, worker_scheduler_factory=None, **env_params):
    """Run internally, bypassing the command-line parsing.

    Useful if you have some luigi code that you want to run internally
    
    Arguments:
        tasks {[type]} -- [description]
    
    Keyword Arguments:
        worker_scheduler_factory {[type]} -- [description] (default: {None})\

    :return: True if there were no scheduling errors, even if tasks may fail

    Example:

    .. code-block:: python
        finestrino.build([MyTask1(), MyTask2()], local_scheduler=True)
    """
    if "no_lock" not in env_params:
        env_params["no_lock"] = True

    return _schedule_and_run(tasks, worker_scheduler_factory, override_defaults=env_params)['success']

def run():
    pass