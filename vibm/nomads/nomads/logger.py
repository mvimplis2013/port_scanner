import os
from os import environ

import logging 
import logging.config

PATH = "NOMADS_PATH"

# Default Logging Full Filename
if PATH not in os.environ:
    raise EnvironmentError("NOMADS_PATH Not Set")

# 
parent = os.environ.get( PATH )
logs_folder = parent + "/logs/"

if not os._exists( logs_folder ):
    raise EnvironmentError( "Logs Folder Not Found: %s", logs_folder )  

# Custom Logger Class

LOG_CONFIG = {
    'version': 1.0,
    'disable_existing_loggers': False,
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console'],
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s -- %(levelname)s -- %(name)s: %(message)s'
        },
        'short': {
            'format': '%(levelname)s -- %(message)s'
        },
        'long': {
            'format': '%(asctime)s -- %(levelname)s: %(message)s (%(funcName)s in %(filename)s)'
        },
        'free': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILENAME
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'finestrino': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

def nomads_logger():
    _logger = logging.getLogger()

    config = LOG_CONFIG

    logging.config.dictConfig( config )

    return _logger

my_logger = nomads_logger()