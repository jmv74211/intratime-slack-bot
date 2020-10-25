import pytest

from datetime import datetime
from intratime_slack_bot.lib import time_utils, logger, codes, messages
from intratime_slack_bot.lib.test_utils import check_if_log_exist, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------


DATETIME_FROM = '2020-09-01 01:00:00'
DATETIME_TO = '2020-09-26 05:00:00'
DATE = '2020-10-01'

# ----------------------------------------------------------------------------------------------------------------------


def test_get_current_date_time():
    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"

    assert date_time == time_utils.get_current_date_time()

# ----------------------------------------------------------------------------------------------------------------------


def test_get_current_date():
    now = datetime.now()
    date_time = f"{now.strftime('%Y-%m-%d')}"

    assert date_time == time_utils.get_current_date()

# ----------------------------------------------------------------------------------------------------------------------


def test_get_time_difference():
    # BAD CASES
    assert time_utils.get_time_difference(DATETIME_FROM, DATETIME_TO, 'invalid_unit', TEST_FILE) == codes.INVALID_VALUE
    assert check_if_log_exist(messages.make_message(3018, f"of 'UNIT' parameter. Received UNIT = invalid_unit"),
                              TEST_FILE, logger.ERROR)
    # VALID CASES
    assert time_utils.get_time_difference(DATETIME_FROM, DATETIME_TO, time_utils.DAYS, TEST_FILE) == 25
    assert time_utils.get_time_difference(DATETIME_FROM, DATETIME_TO, time_utils.HOURS, TEST_FILE) == 604
    assert time_utils.get_time_difference(DATETIME_FROM, DATETIME_TO, time_utils.MINUTES, TEST_FILE) == 36240
    assert time_utils.get_time_difference(DATETIME_FROM, DATETIME_TO, time_utils.SECONDS, TEST_FILE) == 2174400

# ----------------------------------------------------------------------------------------------------------------------


def test_get_next_day():
    assert time_utils.get_next_day(DATE) == '2020-10-02'

# ----------------------------------------------------------------------------------------------------------------------


def test_sum_days_to_date():
    assert time_utils.sum_days_to_date(DATE, 5) == '2020-10-06'

# ----------------------------------------------------------------------------------------------------------------------


def test_date_included_in_range():
    assert time_utils.date_included_in_range(DATETIME_FROM, DATETIME_TO, '2020-9-07 10:00:00')
    assert not time_utils.date_included_in_range(DATETIME_TO, DATETIME_TO, '2020-10-06 10:00:00')

# ----------------------------------------------------------------------------------------------------------------------


def test_convert_datetime_string_to_date_string():
    assert time_utils.convert_datetime_string_to_date_string(DATETIME_FROM) == '2020-09-01'

# ----------------------------------------------------------------------------------------------------------------------


def get_time_string_from_seconds():
    assert time_utils.get_time_string_from_seconds(3680) == '1h 01m 20s'
