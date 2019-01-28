import logging 
import logging.config

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
    return my_logger

logger = nomads_logger()