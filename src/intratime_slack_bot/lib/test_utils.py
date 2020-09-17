import os
import json
import re

from intratime_slack_bot.config import settings

TEST_DATA_PATH = os.path.join(settings.APP_PATH, 'test', 'data')

UNIT_TEST_DATA_PATH = os.path.join(TEST_DATA_PATH, 'unit')

TEST_FILE = os.path.join('/tmp', 'test.log')

# ----------------------------------------------------------------------------------------------------------------------

def read_raw_file_data(input_file):
    with open(input_file, 'r') as file_data:
        raw_data = file_data.read()

    return raw_data

# ----------------------------------------------------------------------------------------------------------------------


def read_json_file_data(input_file):
    with open(input_file, 'r') as file_data:
        json_data = json.loads(file_data.read())

    return json_data


# ----------------------------------------------------------------------------------------------------------------------


def check_if_log_exist(string_to_match, log_file, log_level=""):
    data = read_raw_file_data(log_file)

    if log_level == "":
        full_log = rf'\[\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\] {string_to_match}'
    else:
        full_log = rf'\[\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\] {log_level}: {string_to_match}'

    if re.match(full_log, data):
        return True
    else:
        return False
