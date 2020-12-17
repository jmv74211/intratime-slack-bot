import logging
import sys
import os
from logging.handlers import TimedRotatingFileHandler
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.test_utils import TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


FORMATTER = logging.Formatter("%(asctime)s — %(levelname)s — %(filename)s:%(funcName)s:%(lineno)d — %(message)s")

DEBUG = logging.DEBUG
INFO = logging.INFO
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# ----------------------------------------------------------------------------------------------------------------------


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

# ----------------------------------------------------------------------------------------------------------------------


def get_file_handler(log_file_path):
    file_handler = TimedRotatingFileHandler(log_file_path, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler

# ----------------------------------------------------------------------------------------------------------------------


def get_logger(logger_name, level, custom_file=None):
    if custom_file is None:
        log_file_path = os.path.join(settings.LOGS_PATH, f"{logger_name}.log")
    else:
        log_file_path = os.path.join(custom_file)

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file_path))

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False

    return logger
