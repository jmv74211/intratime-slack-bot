import pytest

from clockzy.lib.models.config import Config
from clockzy.lib.db.database_interface import item_exists
from clockzy.lib.test_framework.database import intratime_user_parameters, config_parameters
from clockzy.lib.db.db_schema import CONFIG_TABLE
from clockzy.lib.handlers.codes import SUCCESS, ITEM_ALREADY_EXISTS


# Pytest tierdown fixture is executed from righ to left position
@pytest.mark.parametrize('user_parameters, config_parameters', [(intratime_user_parameters, config_parameters)])
def test_save_config(add_pre_user, delete_post_user, delete_post_config):
    test_config = Config(**config_parameters)

    # Add the config and check that 1 row has been affected (no exception when running)
    assert test_config.save() == SUCCESS

    # If we try to add the same config, check that it can not be inserted
    assert test_config.save() == ITEM_ALREADY_EXISTS

    # Query and check that the config exist
    assert item_exists({'user_id': test_config.user_id}, CONFIG_TABLE)


@pytest.mark.parametrize('user_parameters, config_parameters', [(intratime_user_parameters, config_parameters)])
def test_update_config(add_pre_user, add_pre_config, delete_post_user, delete_post_config):
    test_config = Config(**config_parameters)

    # Update the config info and check that 1 row has been affected (no exception when running)
    test_config.intratime_integration = True
    assert test_config.update() == SUCCESS

    # Query and check that the config exist
    assert item_exists({'user_id': test_config.user_id, 'intratime_integration': True}, CONFIG_TABLE)


@pytest.mark.parametrize('user_parameters, config_parameters', [(intratime_user_parameters, config_parameters)])
def test_delete_config(add_pre_user, add_pre_config, delete_post_user):
    test_config = Config(**config_parameters)

    # Delete the config info and check that 1 row has been affected (no exception when running)
    assert test_config.delete() == SUCCESS

    # Query and check that the config does not exist
    assert not item_exists({'user_id': test_config.user_id}, CONFIG_TABLE)
