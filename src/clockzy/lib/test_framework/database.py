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
