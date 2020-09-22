import pytest

from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib.db.database import validate_data, USER_MODEL
from intratime_slack_bot.lib import codes, messages, logger
from intratime_slack_bot.lib.test_utils import check_if_log_exist, TEST_FILE

# ----------------------------------------------------------------------------------------------------------------------

TEST_USER_DATA = {'user_id': '1234', 'username': 'test', 'password': 'test_password',
                  'intratime_mail': 'test@gmail.com', 'registration_date': '2020-09-18 15:57:00',
                  'last_registration_date': '2020-09-15 15:58:00'}

BAD_USER_DATA = {'user_id': '123', 'username': 'test'}

UPDATE_USER_DATA = {'user_id': '1234', 'username': 'test', 'password': 'test_password',
                    'intratime_mail': 'update_mail@gmail.com', 'registration_date': '2020-09-18 15:57:00',
                    'last_registration_date': '2020-09-15 15:58:00'}

# ----------------------------------------------------------------------------------------------------------------------


@pytest.fixture
def add_remove_user(request):
    if not user.user_exist(TEST_USER_DATA['user_id']):
        user.add_user(TEST_USER_DATA)

    yield

    if user.user_exist(TEST_USER_DATA['user_id']):
        user.delete_user(TEST_USER_DATA['user_id'])

# ----------------------------------------------------------------------------------------------------------------------


def test_user_exist(add_remove_user):
    assert user.user_exist('fake_user') is False
    assert user.user_exist(TEST_USER_DATA['user_id'])

# ----------------------------------------------------------------------------------------------------------------------


def test_validate_data():
    assert validate_data(BAD_USER_DATA, USER_MODEL) is False
    assert validate_data(TEST_USER_DATA, USER_MODEL)

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_data(add_remove_user, remove_test_file):
    assert user.get_user_data('fake_user', TEST_FILE) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3007, TEST_FILE), TEST_FILE, logger.ERROR)
    assert user.get_user_data(TEST_USER_DATA['user_id'], TEST_FILE)['intratime_mail'] == \
        TEST_USER_DATA['intratime_mail']

# ----------------------------------------------------------------------------------------------------------------------


def test_add_user(remove_test_file):
    assert user.user_exist(TEST_USER_DATA['user_id']) is False
    assert user.add_user(BAD_USER_DATA, TEST_FILE) == codes.BAD_USER_DATA
    assert check_if_log_exist(messages.make_message(3005, rf"Expected model .* and got this data: .*"), TEST_FILE,
                              logger.ERROR)
    assert user.add_user(TEST_USER_DATA, TEST_FILE) == codes.SUCCESS
    assert check_if_log_exist(messages.get(2001, TEST_FILE), TEST_FILE, logger.INFO)
    assert user.user_exist(TEST_USER_DATA['user_id'])
    assert user.add_user(TEST_USER_DATA, TEST_FILE) == codes.USER_ALREADY_EXIST
    assert check_if_log_exist(messages.get(3010, TEST_FILE), TEST_FILE, logger.ERROR)
    assert user.delete_user(TEST_USER_DATA['user_id']) == codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def test_update_user(add_remove_user):
    assert user.user_exist(TEST_USER_DATA['user_id'])
    assert user.update_user('fake_user', UPDATE_USER_DATA, TEST_FILE) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3007, TEST_FILE), TEST_FILE, logger.ERROR)
    assert user.update_user(TEST_USER_DATA['user_id'], BAD_USER_DATA, TEST_FILE) == codes.BAD_USER_DATA
    assert check_if_log_exist(messages.make_message(3005, rf"Expected model .* and got this data: .*"), TEST_FILE,
                              logger.ERROR)
    assert user.update_user(TEST_USER_DATA['user_id'], UPDATE_USER_DATA, TEST_FILE) == codes.SUCCESS
    assert check_if_log_exist(messages.get(2003, TEST_FILE), TEST_FILE, logger.INFO)
    assert user.get_user_data(TEST_USER_DATA['user_id'], TEST_FILE)['intratime_mail'] == \
        UPDATE_USER_DATA['intratime_mail']

# ----------------------------------------------------------------------------------------------------------------------


def test_delete_user():
    assert user.delete_user(TEST_USER_DATA['user_id'], TEST_FILE) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3007, TEST_FILE), TEST_FILE, logger.ERROR)
    user.add_user(TEST_USER_DATA, TEST_FILE)
    assert user.user_exist(TEST_USER_DATA['user_id'])
    assert user.delete_user(TEST_USER_DATA['user_id'], TEST_FILE) == codes.SUCCESS
    assert check_if_log_exist(messages.get(2002, TEST_FILE), TEST_FILE, logger.INFO)
    assert user.user_exist(TEST_USER_DATA['user_id']) is False

# ----------------------------------------------------------------------------------------------------------------------


def test_get_all_users_data():
    assert len(user.get_all_users_data()) == 0
    user.add_user(TEST_USER_DATA, TEST_FILE)
    assert len(user.get_all_users_data()) == 1
    user.delete_user(TEST_USER_DATA['user_id'])
    assert len(user.get_all_users_data()) == 0

# ----------------------------------------------------------------------------------------------------------------------


def test_update_last_registration_datetime(add_remove_user):
    assert user.update_last_registration_datetime('bad_user_id', TEST_FILE) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3007, TEST_FILE), TEST_FILE, logger.ERROR)
    assert user.update_last_registration_datetime(TEST_USER_DATA['user_id'], TEST_FILE) == codes.SUCCESS
    assert user.get_user_data(TEST_USER_DATA['user_id'], TEST_FILE)['last_registration_date'] \
        != TEST_USER_DATA['last_registration_date']

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_id(add_remove_user):
    assert user.get_user_id('fake_mail@mail.com', TEST_FILE) == codes.BAD_USER_EMAIL
    assert check_if_log_exist(messages.make_message(3011, f"with mail = fake_mail@mail.com"), TEST_FILE, logger.ERROR)
    assert user.get_user_id(TEST_USER_DATA['intratime_mail']) == TEST_USER_DATA['user_id']
