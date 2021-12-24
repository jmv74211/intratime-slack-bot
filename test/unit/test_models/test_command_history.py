import pytest

from clockzy.lib.models.command_history import CommandHistory
from clockzy.lib.test_framework.database import item_exists, intratime_user_parameters, command_history_parameters
from clockzy.lib.db.db_schema import COMMANDS_HISTORY_TABLE


# Pytest tierdown fixture is executed from righ to left position
@pytest.mark.parametrize('user_parameters, command_history_parameters', [(intratime_user_parameters,
                                                                          command_history_parameters)])
def test_save_command_history(add_pre_user, delete_post_user, delete_post_command_history):
    test_command_history = CommandHistory(**command_history_parameters)

    # Add the command_history and check that 1 row has been affected (no exception when running)
    test_command_history.save()
    command_history_parameters['id'] = test_command_history.id

    # Query and check that the command history exist
    assert item_exists({'id': test_command_history.id}, COMMANDS_HISTORY_TABLE)


@pytest.mark.parametrize('user_parameters, command_history_parameters', [(intratime_user_parameters,
                                                                          command_history_parameters)])
def test_update_command_history(add_pre_user, add_pre_command_history, delete_post_user, delete_post_command_history):
    test_command_history = CommandHistory(**command_history_parameters)
    test_command_history.id = add_pre_command_history
    command_history_parameters['id'] = test_command_history.id

    # Update the command history info and check that 1 row has been affected (no exception when running)
    test_command_history.command = '/time_history'
    test_command_history.update()

    # Query and check that the command history exist
    assert item_exists({'id': test_command_history.id, 'command': '/time_history'}, COMMANDS_HISTORY_TABLE)


@pytest.mark.parametrize('user_parameters, command_history_parameters', [(intratime_user_parameters,
                                                                          command_history_parameters)])
def test_delete_command_history(add_pre_user, add_pre_command_history, delete_post_user):
    test_command_history = CommandHistory(**command_history_parameters)
    test_command_history.id = add_pre_command_history
    command_history_parameters['id'] = test_command_history.id

    # Delete the command history info and check that 1 row has been affected (no exception when running)
    test_command_history.delete()

    # Query and check that the command_history does not exist
    assert not item_exists({'id': test_command_history.id}, COMMANDS_HISTORY_TABLE)
