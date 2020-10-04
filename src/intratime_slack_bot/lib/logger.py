from datetime import datetime

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import time_utils
from intratime_slack_bot.lib import messages

# ----------------------------------------------------------------------------------------------------------------------


DEBUG = 'DEBUG'
INFO = 'INFO'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'

LEVELS = {
    'DEBUG': 1,
    'INFO': 2,
    'ERROR': 3,
    'CRITICAL': 4
}

# ----------------------------------------------------------------------------------------------------------------------


def log(file, level, message_id=-1, custom_message=""):
    """
    Post a log in the indicated file

    Parameters
    ----------
    file: String
        File path to log
    level: String
        Log level
    message_id: int
        message id from messages module
    """

    datetime = time_utils.get_current_date_time()

    if message_id != -1:
        try:
            description = messages.message[f"{message_id}"]
        except KeyError:
            level = ERROR
            description = f"Could not get the message description from message with id {message_id}"
    else:
        description = custom_message

    if LEVELS[level] >= LEVELS[settings.LOG_LEVEL]:
        with open(file, 'a') as f:
            f.write(f"[{datetime}] {level}: {description}\n")
