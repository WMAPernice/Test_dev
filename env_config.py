import sys

import logging.handlers
import os
import yaml
from datetime import datetime

# when imported all the logging variables needed for other modules become available

IS_PRODUCTION = True if os.getenv("PRODUCTION") == 'TRUE' else False


def get_config() -> dict:
    config_file_path = os.getenv("CONFIG_FILE_PATH")
    with open(config_file_path) as file:
        try:
            config = yaml.load(file)
        except yaml.YAMLError as exc:
            print("get_config got an error" + str(exc)), exit(1)
        else:
            return config


PROGRAM_CONFIG = get_config()


def exception_handler(type, value, tb):
    root_logger.exception("Uncaught exception: {0}".format(str(value)))


if IS_PRODUCTION:
    date = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")

    LOG_FILE_BASE = PROGRAM_CONFIG['logdir'] + date + "." + PROGRAM_CONFIG['version'] + "." + PROGRAM_CONFIG['name']
    LOG_FILE_NAME = LOG_FILE_BASE + ".log"

    handler = logging.handlers.RotatingFileHandler(LOG_FILE_NAME, maxBytes=2000000, backupCount=3)  # max size is 2mb
    handler.setLevel(logging.INFO)  # Set logging level.

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    STDOUT_FILE = LOG_FILE_BASE + '.stdout'
    sys.stdout = open(STDOUT_FILE, 'wt')
    sys.excepthook = exception_handler

else:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    channel = logging.StreamHandler(sys.stdout)
    channel.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    channel.setFormatter(formatter)
    root_logger.addHandler(channel)
