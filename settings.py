import logging

import yaml

with open("config.yml", 'r') as stream:
    config = yaml.load(stream)

DB_CONFIG = config.get('database')

LOG_LEVEL_MAP = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET,
}

LOG_LEVEL = LOG_LEVEL_MAP.get(config.get('log_level', 'INFO'), logging.INFO)
