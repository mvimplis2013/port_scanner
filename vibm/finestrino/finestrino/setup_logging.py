"""
This module contains helper classes for configuring logging for 
finestrinod and workers via command-line arguments and 
options from congiguration files.
"""
import logging
import os

from finestrino.configuration import get_config, FinestrinoConfigParser

# In Python3 ConfigParser was renamed. 
try:
    from ConfigParser import NoSectionError
except ImportError:
    from configparser import NoSectionError

class BaseLogging(object):
    config = get_config()

    @classmethod
    def _section(cls, opts):
        """ 
        Get logging settings from config file "logging".
        """
        if isinstance(cls.config, FinestrinoConfigParser):
            return False

        try:
            logging_config = cls.config["logging"]
        except (TypeError, KeyError, NoSectionError):
            return False

        logging.config.dictConfig(logging_config)

        return True

    @classmethod
    def setup(cls, opts=type(
        'opts', (), {
            'background': None, 
            'logdir': None, 
            'logging_conf_file': None, 
            'log_level': 'DEBUG',
        }
    )):
        """ 
        Setup logging via CLI params and config. 
        """
        print("************************************* HHHHHHHHHHHHHHHHHHHHHHHH")
        logger = logging.getLogger("finestrino")

        if cls._configured:
            logger.info("logging already configured")
            return False

        cls._configured = True

        if cls.config.getboolean('core', 'no_configure_logging', False):
            logger.info('logging disabled in settings')
            return False

        configured = cls._cli(opts)
        if configured:
            logger = logging.getLogger("finestrino")
            logger.info("logging configured via special settings")
            return True

        configured = cls._conf(opts)
        if configured:
            logger = logging.getLogger("finestrino")
            logger.info("logging configured via *.conf file")
            return True

        configured = cls._section('finestrino')
        if configured:
            logger = logging.getLogger("finestrino")
            logger.info("logging configured via config section")
            return True

        configured = cls._default(opts)
        if configured:
            logger = logging.getLogger("finestrino")
            logger.info("logging configured by default settings")
        
        return configured

class InterfaceLogging(BaseLogging):
    """ 
    Configure logging for worker.
    """
    _configured = False

    @classmethod
    def _cli(cls, opts):
        return False

    @classmethod
    def _conf(cls, opts):
        """ 
        Setup logging via ini-file from logging_conf_file option.
        """
        if not opts.logging_conf_file:
            return False

        if not os.path.exists(opts.logging_conf_file):
            # FileNotFoundError added only in Python 3.3
            raise OSError("Error: Unable to locate specified logging configuration file!")

        logging.config.fileConfig(opts.logging_conf_file, disable_existing_loggers = False)

        return True

    @classmethod
    def _default(cls, opts):
        """ 
        Setup default logger.
        """
        level = getattr(logging, opts.log_level, logging.DEBUG)

        logger = logging.getLogger("finestrino-interface")
        logger.setLevel(level)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)

        formatter = logging.Formatter("%(levelname)s: %(message)s")
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)

        return True

class DaemonLogging(BaseLogging):
    """
    Configure logging for finestrinod
    """
    _configured = False
    _log_format = "%(asctime)s %(name)s[%(process)s]%(levelname)s: %(message)s"

    @classmethod
    def _cli(cls, opts):
        """
        Setup logging via CLI options.

        If `--background` ... set INFO level for root logger.
        If `--logdir`     ... set logging with next params:
            default finestrino formatter,
            INFO level,
            output in `finestrino-server.log` file
        """
        if opts.background:
            logging.getLogger().setLevel(logging.INFO)
            return True

        if opts.logdir:
            logging.basicConfig(
                level = logging.INFO,
                format = cls._log_format,
                filename = os.path.join(opts.logdir, "finestrino-server.log")
            )

            return True

        return False

    @classmethod
    def _conf(cls, opts):
        """
        Setup logging via ini-file from logging_conf_file option.
        """
        logging_conf = cls.config.get("core", "logging_conf_file", None)

        if logging_conf is None:
            return False 

        if not os.path.exists(logging_conf):
            # FileNotFoundError added only in Python 3.3
            raise OSError("Error: Unable to locate specified logging configuration file!")

        logging.config.fileConfig(logging_conf)

        return True
