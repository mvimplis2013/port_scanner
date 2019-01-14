import finestrino 

from finestrino import IntParameter

import logging 
import sys 

class retcode(finestrino.Config):
    unhandled_exception = IntParameter(default=4, description="For internal finestrino errors.")

    missing_data = IntParameter(default=0, description="When there are incomplete ExternalTask dependencies.")

    task_failed = IntParameter(default=0, description="For when a task's run() method fails.")

    already_running = IntParameter(default=0, description='For both local --lock and luigid "lock".')

    scheduling_error = IntParameter(default=0, description="For when a task's complete() or requires() fails, or task-limit reached.")

    not_run = IntParameter(default=0, description="When a task is not granted run permission by the scheduler.")

def run_with_retcodes(argv):
    """ 
    Run finestrino with command line parser, but raise ``SystemExit`` with the configured
    exit code.

    Note: Usually you use the finestrino binary directly and don't call this function yourself.

    :param argv: Should be ``sys.argv[1:]``.
    """
    logger = logging.getLogger('finestrino-interface')
    #logger.debug("Strong")
    
    with finestrino.cmdline_parser.CmdlineParser.global_instance(argv):
        retcodes = retcode()

    worker = None
    try:
        worker = finestrino.interface._run(argv)['worker']
    except finestrino.interface.PidLockAlreadyTakenExit:
        sys.exit(retcodes.already_running)
    except Exception:
        # Some errors occur before logging is setup, we set it up now
        finestrino.interface.setup_interface_logging()
        logger.exception("Uncaught exception in finestrino")
        sys.exit(retcodes.unhandled_exception)

    with finestrino.cmdline_parser.CmdlineParser.global_instance(argv):
        task_sets = finestrino.execution_summary._summary_dict(worker)
        root_task = finestrino.execution_summary._root_task(worker)
        non_empty_categories = {k: v for k, v in task_sets.items() if v}.keys()

    def has(status):
        assert status in finestrino.execution_summary._ORDERED_STATUSES
        return status in non_empty_categories

    codes_and_conds = (
        (retcodes.missing_data, has('still_pending_ext')),
        (retcodes.task_failed, has('failed')),
        (retcodes.already_running, has('run_by_other_worker')),
        (retcodes.scheduling_error, has('scheduling_error')),
        (retcodes.not_run, has('not_run')),
    )

    expected_ret_code = max(code * (1 if cond else 0) for code, cond in codes_and_conds)

    if expected_ret_code == 0 and root_task not in task_sets["completed"] and root_task not in task_sets["already_done"]:
        sys.exit(retcodes.not_run)
    else:
        sys.exit(expected_ret_code)

