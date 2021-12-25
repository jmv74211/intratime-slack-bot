from clockzy.lib.utils.time import get_current_date_time
from clockzy.lib.models.user import User
from clockzy.lib.models.clock import Clock
from clockzy.lib.models.command_history import CommandHistory
from clockzy.lib.models.config import Config
from clockzy.lib.models.alias import Alias
from clockzy.lib.db.database_interface import run_query, build_select_query_from_object_parameters, \
                                              get_database_data_from_objects
from clockzy.lib.db.db_schema import CLOCK_TABLE, COMMANDS_HISTORY_TABLE, CONFIG_TABLE, ALIAS_TABLE, USER_TABLE


# User with intratime integration
intratime_user_parameters = {'id': 'test_user_1', 'user_name': 'test_user_1', 'password': 'test_password',
                             'email': 'test_email'}
# User without intratime integration
no_intratime_user_parameters = {'id': 'test_user_2', 'user_name': 'test_user_2'}
clock_parameters = {'user_id': intratime_user_parameters['id'], 'action': 'IN', 'date_time': get_current_date_time()}
command_history_parameters = {'user_id': intratime_user_parameters['id'], 'command': '/time', 'parameters': 'today',
                              'date_time': get_current_date_time()}
config_parameters = {'user_id': intratime_user_parameters['id'], 'intratime_integration': False}
alias_parameters = {'user_name': intratime_user_parameters['user_name'], 'alias': 'test'}


def clean_test_data():
    """Clean all test data from the DB"""
    # Get the test objects from the DB test data
    clock_data = get_database_data_from_objects({'user_id': clock_parameters['user_id']}, CLOCK_TABLE)
    command_history_data = get_database_data_from_objects({'user_id': command_history_parameters['user_id']},
                                                          COMMANDS_HISTORY_TABLE)
    config_data = get_database_data_from_objects({'user_id': config_parameters['user_id']}, CONFIG_TABLE)
    alias_data = get_database_data_from_objects({'alias': alias_parameters['alias']}, ALIAS_TABLE)
    intratime_user_data = get_database_data_from_objects({'id': intratime_user_parameters['id']}, USER_TABLE)
    normal_user_data = get_database_data_from_objects({'id': no_intratime_user_parameters['id']}, USER_TABLE)

    # Create objects from DB data and then delete them

    # Delete clock test data
    for clock_item in clock_data:
        clock_object = Clock(clock_item[1], clock_item[2], clock_item[3])
        clock_object.id = clock_item[0]
        cloc_object.delete()

    # Delete command history test data
    for command_history_item in command_history_data:
        command_history_object = CommandHistory(command_history_item[1], command_history_item[2],
                                                command_history_item[3], command_history_item[4])
        command_history_object.id = command_history_item[0]
        command_history_object.delete()

    # Delete config test data
    for config_item in config_data:
        config_object = Config(config_item[0], config_item[1])
        config_object.delete()

    # Delete alias test data
    for alias_item in alias_data:
        alias_object = Alias(alias_item[0], alias_item[1])
        alias_object.delete()

    # Delete intratime user data
    for intratime_user_item in intratime_user_data:
        intratime_user_object = User(intratime_user_item[0], intratime_user_item[1])
        intratime_user_object.delete()

    # Delete normal user data
    for normal_user_item in normal_user_data:
        normal_user_object = User(normal_user_item[0], normal_user_item[1])
        normal_user_object.delete()
