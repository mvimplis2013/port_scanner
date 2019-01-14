"""
Contains some helper functions to run `finestrinod` in deamon mode.
"""
from __future__ import print_function

import os
import datetime 
import logging 

rootlogger = logging.getLogger()
server_logger = logging.getLogger("finestrino.server")

def check_pid(pidfile):
    if pidfile and os.path.exists(pidfile):
        try:
            pid = int(open(pidfile).read().strip())
            os.kill(pid, 0)

            return pid
        except BaseException:
            return 0

    return 0

def write_pid(pidfile):
    server_logger.info("Writing pid file")
    piddir = os.path.dirname(pidfile)

    if piddir != '':
        try:
            os.makedirs(piddir)
        except OSError:
            pass 

    with open(pidfile, 'w') as fobj:
        fobj.write(str(os.getpid()))

def get_log_format():
    return "%(asctime)s %(name)s %[(process)s]: %(message)s"

def get_spool_handler(filename):
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=filename,
        when='d',
        encoding='utf8',
        backupCount=7 # keep one week of historical logs 
    )

    formatter = logging.Formatter( get_log_format() )

    handler.setFormatter( formatter )

    return handler 

def _server_already_running(pidfile):
    existing_pid = check_pid(pidfile)

    if pidfile and existing_pid:
        return True

    return False 

def daemonize(cmd, pidfile=None, logdir=None, api_port=8082, address=None, unix_socket=None):
    import daemon

    logdir = logdir or '/var/log/finestrino'

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    log_path = os.path.join(logdir, "finestrino-server.log")

    # redirect stdout/ stderr
    today = datetime.date.today()

    stdout_path = os.path.join(
        logdir, 
        "finestrino-server-{0:%Y-%m-%d}.out".format(today))

    stderr_path = os.path.join(
        logdir,
        "finestring-server-{0:%Y-%m-%d}.err".format(today))

    stdout_proxy = open(stdout_path, 'a+') 
    stderr_proxy = open(stderr_path, 'a+')

    try:
        ctx = daemon.DaemonContext(
            stdout = stdout_proxy,
            stderr = stderr_proxy,
            working_dir = '.',
            initgroup = False,
        )

    except TypeError:
        # Older versions of python-daemon cannot deal with initgroups args
        ctx = daemon.DaemonContext(
            stdout = stdout_proxy,
            stderr = stderr_proxy,
            working_dir = '.',
        )

    with ctx:
        loghandler = get_spool_handler(log_path)
        rootlogger.addHandler(loghandler)

        if pidfile:
            server_logger.info("Checking pid file")
            existing_pid = check_pid(pidfile)

            if pidfile and existing_pid:
                server_logger.info("Server already running (pid=%s)", existing_pid)
                return

            write_pid(pidfile)

        cmd(api_port=api_port, address=address, unix_socket=unix_socket) 



    