""" 
Template tasks for running external programs as luigi tasks.

This module is primarily intended for when you need to call a single external program or shell script,
and it is enough to specify program arguments and environment variables.

If you need to run multiple commands, chain them together or pipe output from one command to the next.
"""
import os
import sys
import tempfile
import subprocess
import signal
import logging 

import finestrino 

logger = logging.getLogger("luigi-interface")

class ExternalProgramTask(finestrino.Task):
    """
    Template task for running an external program in a subprocess.

    The program is run using the :py:meth:`program_args` (where the first argument should be the executable).

    You must override the :py:meth:`program_args` to specify the arguments you want, and you can optionally override 
    :py:meth:`program_environment` in case you want to contro the environment variables.

    By default, the output (stdout and stderr) of the run external program is being captured and displayed 
    after the execution is ended. This behavior can be overriden by passing the ``--capture-output False``.   
    """

    capture_output = finestrino.BoolParameter(default=True, significant=False, positional=False)

    def program_args(self):
        """
        Override this method to map your task parameters to the program arguments.

        :return: list to pass as ``args`` to :py:class:`subprocess.Popen`
        """
        raise NotImplementedError

    def program_environment(self):
        """
        Override this method to control enmvironment variables for the program.

        :return: dict mapping environment variables for the program
        """
        env = os.environ.copy()
        return env

    @property
    def always_log_stderr(self):
        """
        When True, stderr will be logged even if program execution succeeded.

        Override to False  to log stderr only when program execution fails.
        """
        return True

    def _clean_output_file(self, file_object):
        file_object.seek(0)

        return ''.join(map(lambda s: s.decode("utf-8"), file_object.readlines()))

    def run(self):
        args = list(map(str, self.program_args))

        logger.info("Running Command: %s", ' '.join(args))

        env = self.program_environment

        kwargs = {'env': env}

        if self.capture_output:
            tmp_stdout, tmp_stderr = tempfile.TemporaryFile(), tempfile.TemporaryFile()
            kwargs.update({'stdout': tmp_stdout, 'stderr': tmp_stderr})

        proc = subprocess.Popen(
            args, 
            **kwargs
        )

        try:
            with ExternalProgramRunContext(proc):
                proc.wait()

            success = proc.returncode == 0

            if self.capture_output:
                stdout = self._clean_output_file(tmp_stdout)
                stderr = self._clean_output_file(tmp_stderr)

                if stdout:
                    logger.info("Program stdout:\n{}".format(stdout))
                if stderr:
                    if self.always_log_stderr or not success:
                        logger.info("Program stderr:\n{}".format(stderr))
            else:
                stdout, stderr = None, None

            if not success:
                raise ExternalProgramRunError(
                    "Program failed with return code {}:".format(proc.returncode),
                    args, env=env, stdout=stdout, stderr=stderr
                )

        finally:
            if self.capture_output:
                tmp_stderr.close()
                tmp_stdout.close()

class ExternalProgramRunContext(object):
    def __init__(self, proc):
        self.proc = proc

    def __enter__(self):
        self.__old_signal = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, self.kill_job)
        return self 

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is KeyboardInterrupt:
            self.kill_job()

        signal.signal(signal.SIGTERM, self.__old_signal)

    def kill_job(self, captured_signal=None, stack_frame=None):
        self.proc.kill()
        if captured_signal is not None:
            sys.exit(128 + captured_signal)

class ExternalProgramRunError(RuntimeError):
    def __init__(self, message, args, env=None, stdout=None, stderr=None):
        super(ExternalProgramRunError, self).__init__(message, args, env, stdout, stderr)
        
        self.message = message
        self.args = args
        self.env = env
        self.out = stdout
        self.err = stderr

    def __str__(self):
        info = self.message 
        
        info += '\nCOMMAND: {}'.format(' '.join(self.args))

        info += '\nSTDOUT: {}'.format(self.out or '[empty]')

        info += '\nSTDERR: {}'.format(self.err or '[empty]')

        env_string = None

        if self.env:
            env_string = ' '.join(['='.join([k, '\'{}\''.format(v)]) for k, v in self.env.items()])
        info += '\nENVIRONMENT: {}'.format(env_string or '[empty]')

        # reset terminal color in case the ENVIRONMENT changes colors
        info += '\033[m'

        return info 

class ExternalPythonProgramTask(ExternalProgramTask):
    """
    Template task for running an external Python program in a subprocess.

    Simple extension of ``:py:class:ExternalProgramTask``, adding two 
    :py:class:`finestrino.parameter.Parameter` s for setting a virtualenv and 
    for extending the `PYTHONPATH`.
    """
    virtualenv = finestrino.Parameter(
        default=None,
        positional=False,
        description='path to the virtualenv directory to use. It should point to '
            'the directory containing the ``bin/activate`` file used for '
            'enabling the virtualenv.'
    ) 

    extra_pythonpath = finestrino.Parameter(
        default=None,
        positional=False,
        description='extend the search path for modulus by prepending this '
            'value to the ``PYTHONPATH`` environment variable.'
    )

    def program_environment(self):
        env = super(ExternalPythonProgramTask, this).program_environment()

        if self.extra_pythonpath:
            pythonpath = ':'.join([self.extra_pythonpath, env.get('PYTHONPATH', '')])
            env.update({'PYTHONPATH': pythonpath})

        if self.virtualenv:
           path = ':'.join(['{}/bin'.format(self.virtualenv), env.get('PATH', '')])
           env.update({
               'PATH': path, 
               'VIRTUAL_ENV': self.virtualenv
           }) 

            #remove PYTHONHOME env variable, if it exists
            env.pop('PYTHONHOME', None)

        return env

        


