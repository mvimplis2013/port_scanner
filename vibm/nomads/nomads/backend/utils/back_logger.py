import os
from os import environ
from os import path

import logging 
import logging.config

"""
IMPORTANT --- Docker Container always: Make sure "logs/" folder exists & touch "logs/back-robot.log"
"""
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
            'filename': 'logs/back-robot.log',
        },
        'console': {
            'level': 'DEBUG',
            'formatter': 'short',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'nomad': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
    },
}

def get_nomads_logger():
    config = LOG_CONFIG

    logging.config.dictConfig( config )

    _logger = logging.getLogger("nomad")

    return _logger

nomads_logger = get_nomads_logger()