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


def sum_days_to_date(date, days):
    """
    Get the next day from a date

    Parameters
    ----------
    date:str
        Date in format %Y-%m-%d
    days:int
        Number of days to add

    Returns
    -------
    str:
        Date in format %Y-%m-%d
    """

    date_object = datetime.strptime(date, '%Y-%m-%d')
    return datetime.strftime(date_object + timedelta(days=days), '%Y-%m-%d')

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
