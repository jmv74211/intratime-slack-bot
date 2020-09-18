from datetime import datetime

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.messages import message

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


def get_current_date_time():
    """
    Get the current date time

    Returns
    -------
        (Datetime): 2020-03-21 13:44:21
    """

    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    return date_time


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

    datetime = get_current_date_time()

    if message_id != -1:
        try:
            description = message[f"{message_id}"]
        except KeyError:
            level = ERROR
            description = f"Could not get the message description from message with id {message_id}"
    else:
        description = custom_message

    if LEVELS[level] >= LEVELS[settings.LOG_LEVEL]:
        with open(file, 'a') as f:
            f.write(f"[{datetime}] {level}: {description}\n")
