import os
import json
import re

from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------


TEST_DATA_PATH = os.path.join(settings.APP_PATH, 'test', 'data')
UNIT_TEST_DATA_PATH = os.path.join(TEST_DATA_PATH, 'unit')
INTEGRATION_TEST_DATA_PATH = os.path.join(TEST_DATA_PATH, 'integration')
TEST_FILE = os.path.join('/tmp', 'test.log')

# ----------------------------------------------------------------------------------------------------------------------


def read_raw_file_data(input_file):
    """
    Function read a file content

    Parameters
    ----------
    input_file: str
        Path were the file to read is located

    Returns
    -------
        (String): File content
    """

    with open(input_file, 'r') as file_data:
        raw_data = file_data.read()

    return raw_data

# ----------------------------------------------------------------------------------------------------------------------


def read_json_file_data(input_file):
    """
    Function read a json file content

    Parameters
    ----------
    input_file: str
        Path were the file to read is located

    Returns
    -------
        (Dict): File json content
    """
    with open(input_file, 'r') as file_data:
        json_data = json.loads(file_data.read())

    return json_data

# ----------------------------------------------------------------------------------------------------------------------


def check_if_log_exist(string_to_match, log_file, log_level=None):
    """
    Function to check if a log has been logged in the file

    Parameters
    ----------
    string_to_match: str
        Log to find in the file
    log_file: str
        Path where the log file is located
    log_level: str
        Log level: DEBUG, INFO...

    Returns
    -------
        (Boolean): True if log exists, false otherwise
    """

    data = read_raw_file_data(log_file)

    if log_level is None:
        full_log = rf'\[\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\] {string_to_match}'
    else:
        full_log = rf'\[\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\] {log_level}: {string_to_match}'

    if re.search(full_log, data):
        return True
    else:
        return False

# ----------------------------------------------------------------------------------------------------------------------


def load_template_test_data(module, test_file):
    """
    Function to read and get test data from a template file

    Parameters
    ----------
    module: str
        Test module name. e.g slack, intratime...
    test_file: str
        Template file name

    Returns
    -------
        (List): Test data formated to use it as parametrized test
    """
    return [item.values() for item in read_json_file_data(os.path.join(UNIT_TEST_DATA_PATH, module, test_file))]
