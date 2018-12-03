import os
import tempfile

from finestrino import task 
from finestrino import parameter
from finestrino.setup_logging import InterfaceLogging 

class core(task.Config):
    """ 
    Keeps track of a bunch of environment params.

    Uses the internal finestrino parameter mechanism.
    
    The nice thing is that we can instantiate this class and get an
    object with all the environment variables set.
    """
    use_cmdline_section = False

    local_scheduler = parameter.BoolParameter(
        default = False,
        description = 'Use an in-memory central scheduler. Useful for testing.',
        always_in_help = True
    )

    scheduler_host = parameter.Parameter( 
        default = "localhost",
        description = "Hostname of machine running remote scheduler",
        config_path = dict(section="core", name="default-scheduler-host"),
    )

    scheduler_port = parameter.IntParameter(
        default = 8082,
        description = "Port of Remote Scheduler API Process",
        config_path = dict(section="core", name="default-scheduler-port"),
    )

    scheduler_url = parameter.Parameter(
        default = "",
        description = "Full path to remote scheduler",
        config_path = dict(section="core", name="default-scheduler-url"),
    )

    lock_size = parameter.IntParameter(
        default = 1,
        description = "Maximum number of workers running the same command",
    )

    no_lock = parameter.BoolParameter(
        default=False,
        description="Ignore if similar process is already running"
    )

    lock_pid_dir = parameter.Parameter(
        default = os.path.join(tempfile.gettempdir(), 'finestrino'),
        description = "Directory to store the pid file",
    )

    take_lock = parameter.BoolParameter(
        default = False,
        description = "Signal other processes to stop getting work if already running",
    )

    workers = parameter.IntParameter(
        default = 1,
        description = "Maximum number of parallel tasks to run",
    )

    logging_conf_file = parameter.Parameter( 
        default = "",
        description = "Configuration file for logging",
    )

    log_level = parameter.ChoiseParameter(
        default = "DEBUG",
        choices = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        description = "Default log level to use when logging_conf file is not set",
    )

    module = parameter.Parameter(
        default = "",
        description = "Used for dynamic loading of modules",
        always_in_help = True,
    )

    parallel_scheduling = parameter.BoolParameter(
        default = False,
        description = "Use multiprocessing to do scheduling in parallel.",
    )

    parallel_scheduling_process = parameter.IntParameter(
        default = 0,
        description = "The number of processes to use for scheduling in parallel."
            "By default the number of available CPUs will be used.",
    )

    assistant = parameter.BoolParameter(
        default = False,
        description = "Run any task from the scheduler.",
    )

    help = parameter.BoolParameter(
        default = False,
        description = "Show most common flags and all task-specific flags",
        always_in_help = True,
    )

    help_all = parameter.BoolParameter(
        default = False,
        description = "Show all command line flags",
        always_in_help = True,
    )

    InterfaceLogging.setup(env_params)

class _WorkerSchedulerFactory(object):
    
    def create_local_scheduler(self):
        return scheduler.Scheduler(prune_on_get_work=True, record_task_history=False)

    def create_remote_scheduler(self, url):
        return rpc.RemoteScheduler(url)

    def create_worker(self, scheduler, worker_processes, assistant=False):
        return worker.Worker(self, scheduler, worker_processes=worker_processes, assistant=assistant)

def _schedule_and_run(tasks, worker_scheduler_factory=None, override_defaults=None):
    """
    :param tasks:
    :param worker_scheduler_factory:
    :param override_defaults:

    :return: True if all tasks and their dependencies were successfully run (or already completed).
        False if any error occured.
    """
    if worker_scheduler_factory is None:
        worker_scheduler_factory = _WorkerSchedulerFactory()

    if override_defaults is None:
        override_defaults = {}

    env_params = core(**override_defaults)

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