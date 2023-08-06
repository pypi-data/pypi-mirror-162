# -*- coding: utf-8 -*-
import logging
from logging import config  # pylint: disable=W0611

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "%(asctime)s %(levelname)-10s: %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'extended': {
            'format': "%(asctime)s %(filename)s:%(lineno)-5s %(levelname)-10s: %(message)s",
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'extended',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["default"]
    }
}


def get_logger():
    """
    Get looger method
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger("root")
