from datetime import datetime, timedelta

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import codes, messages, logger

# ----------------------------------------------------------------------------------------------------------------------

DAYS = 'day'
HOURS = 'hour'
MINUTES = 'minute'
SECONDS = 'second'

# ----------------------------------------------------------------------------------------------------------------------


def get_current_date_time():
    """
    Get the current date time

    Returns
    -------
    str:
        Datetime in format %Y-%m-%d %H:%M:%S
    """

    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    return date_time

# ----------------------------------------------------------------------------------------------------------------------


def get_current_date():
    """
    Get the current date

    Returns
    -------
    str:
        Date in format in format %Y-%m-%d
    """

    return f"{datetime.now().strftime('%Y-%m-%d')}"

# ----------------------------------------------------------------------------------------------------------------------


def get_time_difference(datetime_from, datetime_to, unit, log_file=settings.APP_LOG_FILE):
    """
    Get the time difference between two datetimes (time subtraction).

    Parameters
    ----------
    datetime_from: str
        Upper limit datetime in format %Y-%m-%d %H:%M:%S
    datetime_to: str
        Upper limit datetime  in format %Y-%m-%d %H:%M:%S
    unit: str
        Unit of time to express the result. enum: ['day', 'hour', 'minute', 'second']
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
        codes.INVALID_VALUE if unit is not correct
        Time elapsed between the two datetimes
    """

    datetime_from_object = datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S')
    datetime_to_object = datetime.strptime(datetime_to, '%Y-%m-%d %H:%M:%S')

    if unit == DAYS:
        return int((datetime_to_object - datetime_from_object).total_seconds() / (60*60*24))
    elif unit == HOURS:
        return int((datetime_to_object - datetime_from_object).total_seconds() / (60*60))
    elif unit == MINUTES:
        return int((datetime_to_object - datetime_from_object).total_seconds() / 60)
    elif unit == SECONDS:
        return int((datetime_to_object - datetime_from_object).total_seconds())
    else:
        logger.log(file=log_file, level=logger.ERROR,
                   custom_message=messages.make_message(3018, f"of 'UNIT' parameter. Received UNIT = {unit}"))
        return codes.INVALID_VALUE

# ----------------------------------------------------------------------------------------------------------------------


def get_next_day(date):
    """
    Get the next day from a date

    Parameters
    ----------
    date: str
        Date in format %Y-%m-%d

    Returns
    -------
    str:
        Date in format %Y-%m-%d
    """

    date_object = datetime.strptime(date, '%Y-%m-%d')
    return datetime.strftime(date_object + timedelta(days=1), '%Y-%m-%d')

# ----------------------------------------------------------------------------------------------------------------------


def subtract_days_to_datetime(date_time, days):
    """
    Subtract a number of days from a given date

    Parameters
    ----------
    date_time: str
        Date in format %Y-%m-%d %H:%M:%S
    days: int
        Number of days to subtract

    Returns
    -------
    str:
        Datetime in format %Y-%m-%d %H:%M:%S
    """

    date_object = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return datetime.strftime(date_object - timedelta(days=days), '%Y-%m-%d %H:%M:%S')

# ----------------------------------------------------------------------------------------------------------------------


def date_included_in_range(datetime_from, datetime_to, date):
    """
    Get the next day from a date

    Parameters
    ----------
    datetime_from: str
        Upper limit datetime in format %Y-%m-%d %H:%M:%S
    datetime_to: str
        Upper limit datetime in format %Y-%m-%d %H:%M:%S
    date:str
        Date to check if it is included in the range in format %Y-%m-%d %H:%M:%S

    Returns
    -------
    boolean:
        True if date is in range, False otherwise
    """

    start_date = datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(datetime_to, '%Y-%m-%d %H:%M:%S')
    target_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return start_date <= target_date <= end_date


# ----------------------------------------------------------------------------------------------------------------------


def convert_datetime_string_to_date_string(date_time):
    """
    Convert a date in %Y-%m-%d %H:%M:%S format to %Y-%m-%d format

    Parameters
    ----------
    datetime: str
        datetime in format %Y-%m-%d %H:%M:%S

    Returns
    -------
    str:
        Date in format %Y-%m-%d
    """

    date_time_object = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    date_string = datetime.strftime(date_time_object.date(), '%Y-%m-%d')
    return date_string

# ----------------------------------------------------------------------------------------------------------------------


def get_past_datetime_from_current_datetime(seconds):
    """
    Get the datetime after x seconds from current time

    Parameters
    ----------
    seconds: int
        Number of seconds

    Returns
    -------
    str:
        Date in format %Y-%m-%d %H:%M:%S
    """

    date_object = datetime.strptime(get_current_date_time(), '%Y-%m-%d %H:%M:%S')
    past_datetime = datetime.strftime(date_object - timedelta(seconds=seconds), '%Y-%m-%d %H:%M:%S')

    return past_datetime

# ----------------------------------------------------------------------------------------------------------------------


def get_time_string_from_seconds(seconds):
    """
    Function to get the time string from seconds. e.g
    3660 --> 1h 1m 0s

    Parameters
    ----------
    seconds: int
        Number of seconds

    Returns
    -------
    str:
        Time string in format [x]h [y]m [z]s
    """

    _time = str(timedelta(seconds=seconds)).split(':')

    return f"{_time[0]}h {_time[1]}m {_time[2]}s"

# ----------------------------------------------------------------------------------------------------------------------


def get_week_day(date_time):
    """
    Function to get current day of the week, where Monday is 0 and Sunday is 6.

    Parameters
    ----------
    date_time: str
        datetime to find out what day of the week it is

    Returns
    -------
    int:
        [0-6] where Monday is 0 and Sunday is 6
    """

    date_object = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return date_object.weekday()

# ----------------------------------------------------------------------------------------------------------------------


def get_month_day(date_time):
    """
    Function to get current day of the month.

    Parameters
    ----------
    date_time: str
        datetime to get the month day

    Returns
    -------
    int:
        Month day
    """

    date_object = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return int(date_object.strftime("%d"))
