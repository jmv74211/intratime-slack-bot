import pytest
from pymysql import MySQLError

from clockzy.lib.models.user import User
from clockzy.lib.db.database_interface import item_exists
from clockzy.lib.test_framework.database import intratime_user_parameters, no_intratime_user_parameters
from clockzy.lib.db.db_schema import USER_TABLE
from clockzy.lib.handlers.codes import SUCCESS, ITEM_ALREADY_EXISTS


@pytest.mark.parametrize('user_parameters', [intratime_user_parameters, no_intratime_user_parameters])
def test_save_user(user_parameters, delete_post_user):
    test_user = User(**user_parameters)

    # Add the users and check that 1 row has been affected (no exception when running)
    assert test_user.save() == SUCCESS

    # If we try to add the same user, check that it can not be inserted
    assert test_user.save() == ITEM_ALREADY_EXISTS

    # Query and check that the user exist
    assert item_exists({'id': test_user.id}, USER_TABLE)


@pytest.mark.parametrize('user_parameters', [intratime_user_parameters])
def test_update_user(user_parameters, add_pre_user, delete_post_user):
    test_user = User(**user_parameters)
    user_name_updated = 'user_name_updated'

    # Update the user info and check that 1 row has been affected (no exception when running)
    test_user.user_name = user_name_updated
    assert test_user.update() == SUCCESS

    # Query and check that the user exist
    assert item_exists({'id': test_user.id, 'user_name': user_name_updated}, USER_TABLE)


@pytest.mark.parametrize('user_parameters', [intratime_user_parameters])
def test_delete_user(user_parameters, add_pre_user):
    test_user = User(**user_parameters)

    # Delete the user and check that 1 row has been affected (no exception when running)
    assert test_user.delete() == SUCCESS

    # Query and check that the user does not exist
    assert not item_exists({'id': test_user.id}, USER_TABLE)
