from pymysql import MySQLError

from clockzy.lib.db.database_interface import run_query
from clockzy.lib.utils.time import get_current_date_time

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


def build_exist_query_from_parameters(parameters, table_name):
    query_string = f"SELECT * FROM {table_name} WHERE "

    for parameter, value in parameters.items():
        formatted_value = f"'{value}'" if isinstance(value, str) else value
        query_string += f"{parameter}={formatted_value} and "

    # Delete the last "," character
    query_string = query_string[:-4]

    return query_string


def item_exists(object_parameters, table_name):
    query = build_exist_query_from_parameters(object_parameters, table_name)

    return len(run_query(query)) > 0
