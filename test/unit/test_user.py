import pytest

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.lib.db.database import validate_data, USER_MODEL
from intratime_slack_bot.lib import codes, messages
from intratime_slack_bot.lib.test_utils import check_if_log_exist
from conftest import TEST_USER_DATA

# ----------------------------------------------------------------------------------------------------------------------


BAD_USER_DATA = {'user_id': '123', 'user_name': 'test'}

UPDATE_USER_DATA = {'user_id': 'test', 'user_name': 'test', 'password': 'test_password',
                    'intratime_mail': 'update_mail@gmail.com', 'registration_date': '2020-09-18 15:57:00',
                    'last_registration_date': '2020-09-15 15:58:00'}

# ----------------------------------------------------------------------------------------------------------------------


def test_validate_data():
    # BAD USER MODEL
    assert not validate_data(BAD_USER_DATA, USER_MODEL)

    # VALID USER MODEL
    assert validate_data(TEST_USER_DATA, USER_MODEL)

# ----------------------------------------------------------------------------------------------------------------------


def test_user_exist(add_user, post_delete_user):
    # BAD USER
    assert not user.user_exist('fake_user')

    # VALID USER
    assert user.user_exist(TEST_USER_DATA['user_id'])

# ----------------------------------------------------------------------------------------------------------------------


def test_add_user(post_delete_user, mock_user_logger):
    # BAD USER DATA
    assert user.add_user(BAD_USER_DATA) == codes.BAD_USER_DATA
    assert check_if_log_exist(messages.get(3028))

    # ADD THE TEST USER
    assert user.add_user(TEST_USER_DATA) == codes.SUCCESS
    assert user.user_exist(TEST_USER_DATA['user_id'])
    assert check_if_log_exist(messages.get(2001, TEST_USER_DATA['user_id']), 'INFO')

    # ADD THE SAME USER AND CHECK RESULT
    assert user.add_user(TEST_USER_DATA) == codes.USER_ALREADY_EXIST
    assert check_if_log_exist(messages.get(3010))

# ----------------------------------------------------------------------------------------------------------------------


def test_delete_user(mock_user_logger):
    # BAD USER_ID
    assert user.delete_user(TEST_USER_DATA['user_id']) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3008, "user not exists"))

    # ADD AN USER
    user.add_user(TEST_USER_DATA)
    assert user.user_exist(TEST_USER_DATA['user_id'])

    # DELETE THE USER AND CHECK THE RESULT
    assert user.delete_user(TEST_USER_DATA['user_id']) == codes.SUCCESS
    assert check_if_log_exist(messages.get(2002, TEST_USER_DATA['user_id']), 'INFO')
    assert user.user_exist(TEST_USER_DATA['user_id']) is False

# ----------------------------------------------------------------------------------------------------------------------


def test_update_user(add_user, post_delete_user, mock_user_logger):
    # BAD USER_ID
    assert user.update_user('fake_user', UPDATE_USER_DATA) == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3009, "user not exists"))

    # BAD USER DATA
    assert user.update_user(TEST_USER_DATA['user_id'], BAD_USER_DATA) == codes.BAD_USER_DATA
    assert check_if_log_exist(messages.get(3028))

    # UPDATE THE USER AND CHECK THE USER DATA
    assert user.update_user(TEST_USER_DATA['user_id'], UPDATE_USER_DATA) == codes.SUCCESS
    assert check_if_log_exist(messages.get(2004, f"user_id = {TEST_USER_DATA['user_id']}"), 'INFO')
    assert user.get_user_data(TEST_USER_DATA['user_id'])['intratime_mail'] == UPDATE_USER_DATA['intratime_mail']

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_data(add_user, post_delete_user, mock_user_logger):
    # BAD USER
    assert user.get_user_data('fake_user') == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3009, "user not exists"))

    # GET AND CHECK USER DATA
    assert user.get_user_data(TEST_USER_DATA['user_id'])['intratime_mail'] == TEST_USER_DATA['intratime_mail']

# ----------------------------------------------------------------------------------------------------------------------


def test_get_all_users_data():
    # ADD AN USER AND CHECK DATA
    user.add_user(TEST_USER_DATA)
    num_users = len(user.get_all_users_data())
    assert num_users > 0

    # DELETE THE USER AND CHECK DATA
    user.delete_user(TEST_USER_DATA['user_id'])
    assert len(user.get_all_users_data()) == num_users - 1

# ----------------------------------------------------------------------------------------------------------------------


def test_update_last_registration_datetime(add_user, post_delete_user, mock_user_logger):
    # BAD USER_ID
    assert user.update_last_registration_datetime('bad_user_id') == codes.USER_NOT_FOUND
    assert check_if_log_exist(messages.get(3009, "user not exists"))

    # VALID USER_ID
    assert user.update_last_registration_datetime(TEST_USER_DATA['user_id']) == codes.SUCCESS
    assert user.get_user_data(TEST_USER_DATA['user_id'])['last_registration_date'] \
        != TEST_USER_DATA['last_registration_date']

# ----------------------------------------------------------------------------------------------------------------------


def test_get_user_id(add_user, post_delete_user):
    # BAD USER MAIL
    assert user.get_user_id('fake_mail@mail.com') == codes.BAD_USER_EMAIL

    # VALID USER MAIL
    print(TEST_USER_DATA['intratime_mail'])
    print(TEST_USER_DATA['user_id'])
    assert user.get_user_id(TEST_USER_DATA['intratime_mail']) == settings.SLACK_TEST_USER_ID
