import requests
import json
import re

from datetime import datetime, date
from http import HTTPStatus

from http import HTTPStatus
from intratime_slack_bot.lib import logger, codes, messages, time_utils
from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db import user

# ----------------------------------------------------------------------------------------------------------------------


IN_ACTION = 'in'
PAUSE_ACTION = 'pause'
RETURN_ACTION = 'return'
OUT_ACTION = 'out'

INTRATIME_API_URL = 'http://newapi.intratime.es'
INTRATIME_API_LOGIN_PATH = '/api/user/login'
INTRATIME_API_CLOCKING_PATH = f'{INTRATIME_API_URL}/api/user/clocking'
INTRATIME_API_USER_CLOCKINGS_PATH = f'{INTRATIME_API_URL}/api/user/clockings'
INTRATIME_API_APPLICATION_HEADER = 'Accept: application/vnd.apiintratime.v1+json'
INTRATIME_API_HEADER = {
                            'Accept': 'application/vnd.apiintratime.v1+json',
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'charset': 'utf8'
                        }

# ----------------------------------------------------------------------------------------------------------------------


def get_action_id(action, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the intratime action ID

    Parameters
    ----------
    action: str
        Action enum: ['in', 'out', 'pause', 'return']
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
        ID associated with the action
    """

    switcher = {
        'in': 0,
        'out': 1,
        'pause': 2,
        'return': 3,
    }

    try:
        return switcher[action]
    except KeyError as excetion:
        logger.log(file=log_file, level=logger.ERROR, message_id=3000)

# ----------------------------------------------------------------------------------------------------------------------


def get_auth_token(email, password, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the Intratime auth token

    Parameters
    ----------
    email: str
        User authentication email
    password: str
        User authentication password
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    str:
        User session token
    int:
       codes.INTRATIME_AUTH_ERROR if user authentication has failed
       codes.INTRATIME_API_CONNECTION_ERROR if there is a Intratime API connection error
    """

    payload = f"user={email}&pin={password}"

    try:
        request = requests.post(url=f"{INTRATIME_API_URL}{INTRATIME_API_LOGIN_PATH}", data=payload,
                                headers=INTRATIME_API_HEADER)
    except ConnectionError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3002)
        return codes.INTRATIME_API_CONNECTION_ERROR

    try:
        token = json.loads(request.text)['USER_TOKEN']
    except KeyError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3003)
        return codes.INTRATIME_AUTH_ERROR

    logger.log(file=log_file, level=logger.DEBUG, custom_message=messages.make_message(1000, f"for user {email}"))

    return token

# ----------------------------------------------------------------------------------------------------------------------


def get_action_name(action, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the intratime action name

    Parameters
    ----------
    action: int
        Action id: 0, 1, 2 or 3
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
        ID associated with the action
    """

    switcher = {
        0: 'in',
        1: 'out',
        2: 'pause',
        3: 'return',
    }

    try:
        return switcher[action]
    except KeyError as excetion:
        logger.log(file=log_file, level=logger.ERROR, message_id=3000)

# ----------------------------------------------------------------------------------------------------------------------


def check_user_credentials(email, password, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to check if user authentication is successful

    Parameters
    ----------
    email: str
        User email authentication
    password: str
        User password authentication
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    boolean:
        True if successful authentication False otherwise
    """

    token = get_auth_token(email=email, password=password, log_file=log_file)

    return token != codes.INTRATIME_API_CONNECTION_ERROR and token != codes.INTRATIME_AUTH_ERROR

# ----------------------------------------------------------------------------------------------------------------------


def get_user_clocks(token, datetime_from, datetime_to, action=None, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the user clocks in a range time

    Parameters
    ----------
    token: str
        User session token
    datetime_from: str
        Upper datetime limit in format %Y-%m-%d %H:%M:%S
    datetime_from: str
        Lower datetime limit in format %Y-%m-%d %H:%M:%S
    action: str
        Action enum: ['in', 'out', 'pause', 'return']
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    list:
        filtered user clocks info
    int:
       codes.UNAUTHORIZED if bad token
       codes.INTRATIME_NO_RESPONSE if intratime can not response the request.
       codes.INTRATIME_API_CONNECTION_ERROR if there is a Intratime API connection error
    """

    # Add user token to intratime header request
    INTRATIME_API_HEADER.update({'token': token})
    filtered_data = []

    try:
        request = requests.get(url=INTRATIME_API_USER_CLOCKINGS_PATH, headers=INTRATIME_API_HEADER)

        if request.status_code == HTTPStatus.UNAUTHORIZED:
            return codes.UNAUTHORIZED

        try:
            data = request.json()

            for item in data:
                # If date is between date_from and date_to
                if time_utils.date_included_in_range(datetime_from, datetime_to, item['INOUT_DATE']):
                    if action is None or (action is not None and get_action_id(action) == item['INOUT_TYPE']):
                        filtered_data.append(item)

            return filtered_data

        except KeyError as exception:
            return codes.INTRATIME_NO_RESPONSE

    except ConnectionError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3002)
        return codes.INTRATIME_API_CONNECTION_ERROR

# ----------------------------------------------------------------------------------------------------------------------


def clocking(action, token, email, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to register an action in Intratime API

    Parameters
    ----------
    action: str
        Action enum: ['in', 'out', 'pause', 'return']
    token: str
        User session token
    email: str
        User email
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
       codes.SUCCESS if clocking has been successful
       codes.codes.UNAUTHORIZED if bad token authentication
       codes.INTRATIME_API_CONNECTION_ERROR if there is a Intratime API connection error
       codes.NO_VALID_RESPONSE if intratime API response is not valid
    """

    date_time = time_utils.get_current_date_time()

    api_action = get_action_id(action)

    # Add user token to intratime header request
    INTRATIME_API_HEADER.update({'token': token})

    payload = f"user_action={api_action}&user_use_server_time={False}&user_timestamp={date_time}"

    try:
        request = requests.post(url=INTRATIME_API_CLOCKING_PATH, data=payload, headers=INTRATIME_API_HEADER)

        if request.status_code == HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.DEBUG, message_id=1001)
            return codes.UNAUTHORIZED

        if request.status_code == HTTPStatus.CREATED:
            user_info_message = f"- user: {email}, action: {action}"
            logger.log(file=log_file, level=logger.INFO, custom_message=messages.make_message(2000, user_info_message))
            user.update_last_registration_datetime(user.get_user_id(email, log_file), log_file)
            return codes.SUCCESS

        return codes.NO_VALID_RESPONSE

    except ConnectionError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3002)
        return codes.INTRATIME_API_CONNECTION_ERROR

# ----------------------------------------------------------------------------------------------------------------------


def get_last_clock(token, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the last user clock action

    Parameters
    ----------
    token: str
        Authentication token
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    dict:
        Last user clock info
    """

    datetime_from = time_utils.get_past_datetime_from_current_datetime(2592000)  # 1 month
    datetime_to = time_utils.get_current_date_time()
    return get_user_clocks(token, datetime_from, datetime_to, None, log_file)[0]

# ----------------------------------------------------------------------------------------------------------------------


def get_last_clock_type(token, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to get the last user clock action type. e.g: PAUSE

    Parameters
    ----------
    token: str
        Authentication token
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    str:
        Last user clock type
    """

    return get_action_name(get_last_clock(token, log_file)['INOUT_TYPE'])

# ----------------------------------------------------------------------------------------------------------------------


def user_can_clock_this_action(token, action):
    """
    Function to check if the user can clock an action

    Parameters
    ----------
    token: str
        Authentication token
    action: str
        Action to check: [in, pause, return, out]

    Returns
    -------
    boolean:
        True if the user can clock that action (action compatible with the previous one), False otherwise
    """

    last_user_clock_action = get_last_clock_type(token)

    clock_data = {
        IN_ACTION: {
            "white_list": [PAUSE_ACTION.upper(), OUT_ACTION.upper()],
            "black_list": [IN_ACTION, RETURN_ACTION],
            "message": f"Your last clock action was `{last_user_clock_action.upper()}`, so you can not clock "
                       f"`{action.upper()}` action."
        },
        PAUSE_ACTION: {
            "white_list": [RETURN_ACTION.upper()],
            "black_list": [IN_ACTION, PAUSE_ACTION, OUT_ACTION],
            "message": f"Your last clock action was `{last_user_clock_action.upper()}`, so you can not clock "
                       f"`{action.upper()}` action."
        },
        RETURN_ACTION: {
            "white_list": [PAUSE_ACTION.upper(), OUT_ACTION.upper()],
            "black_list": [IN_ACTION, RETURN_ACTION],
            "message": f"Your last clock action was `{last_user_clock_action.upper()}`, so you can not clock "
                       f"`{action.upper()}` action."
        },
        OUT_ACTION: {
            "white_list": [IN_ACTION.upper()],
            "black_list": [PAUSE_ACTION, RETURN_ACTION, OUT_ACTION],
            "message": f"Your last clock action was `{last_user_clock_action.upper()}`, so you can not clock "
                       f"`{action.upper()}` action."
        }
    }

    if action in clock_data[last_user_clock_action]['black_list']:
        clock_data[last_user_clock_action]['message'] += f" Available actions: " \
                                                         f"`{clock_data[last_user_clock_action]['white_list']}`"
        return (False, clock_data[last_user_clock_action]['message'])
    else:
        return (True, None)

# ----------------------------------------------------------------------------------------------------------------------


def get_parsed_clock_data(token, datetime_from, datetime_to):
    """
    Function to get the action and datetime info from user clock data returned by the intratime API

    Parameters
    ----------
    token: str
        Authentication token
    datetime_from: str
        Lower datetime limit
    datetime_to: str
        Upper datetime limit

    Returns
    -------
    list:
        List with parsed clock user data
    """

    user_clocks = get_user_clocks(token, datetime_from, datetime_to)

    data = [{"action": get_action_name(item['INOUT_TYPE']), "datetime": item['INOUT_DATE']} for item in user_clocks]

    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_clock_data_in_time_range(token, time_range):
    """
    Function to get clock data parsed for a time range

    Parameters
    ----------
    token: str
        Intratime authentication token
    time_range: str
        String enum: today, week or month

    Returns
    -------
    list:
        List with parsed data in the specific time range.
    """

    lower_limit_datetime = ''

    if time_range == 'today':
        lower_limit_datetime = f"{time_utils.get_current_date()} 00:00:00"
    elif time_range == 'week':
        lower_limit_datetime = time_utils.get_first_week_day()
    elif time_range == 'month':
        lower_limit_datetime = time_utils.get_first_month_day()
    else:
        return codes.INVALID_HISTORY_ACTION

    data = get_parsed_clock_data(token, lower_limit_datetime, time_utils.get_current_date_time())

    return data

# ----------------------------------------------------------------------------------------------------------------------


def get_worked_time(data):
    """
    Function to get the worked time in a specified range time

    Parameters
    ----------
    data: list
        Parsed clock data list (data returned from get_parsed_clock_data function)

    Returns
    -------
    str:
        Time worked in the specified range. Format: [x]h [y]m [z]s
    """

    num_seconds = 0
    before_action = ''

    datetimes = {
        IN_ACTION: "",
        PAUSE_ACTION:  "",
        RETURN_ACTION: "",
        OUT_ACTION: ""
    }

    invalid_actions = {
        IN_ACTION: [IN_ACTION, RETURN_ACTION, PAUSE_ACTION],
        RETURN_ACTION: [RETURN_ACTION, IN_ACTION, OUT_ACTION],
        PAUSE_ACTION: [PAUSE_ACTION, OUT_ACTION],
        OUT_ACTION: [OUT_ACTION, PAUSE_ACTION]
    }

    for item in data:
        if before_action in invalid_actions[item['action']]:
            return codes.INVALID_CLOCK_HISTORY

        datetimes[item['action']] = item['datetime']

        if item['action'] == PAUSE_ACTION and before_action == IN_ACTION:
            num_seconds += time_utils.get_time_difference(datetimes[IN_ACTION], datetimes[PAUSE_ACTION],
                                                          time_utils.SECONDS)
        elif item['action'] == OUT_ACTION and before_action == IN_ACTION:
            num_seconds += time_utils.get_time_difference(datetimes[IN_ACTION], datetimes[OUT_ACTION],
                                                          time_utils.SECONDS)
        elif item['action'] == OUT_ACTION and before_action == RETURN_ACTION:
            num_seconds += time_utils.get_time_difference(datetimes[RETURN_ACTION], datetimes[OUT_ACTION],
                                                          time_utils.SECONDS)
        elif item['action'] == PAUSE_ACTION and before_action == RETURN_ACTION:
            num_seconds += time_utils.get_time_difference(datetimes[RETURN_ACTION], datetimes[PAUSE_ACTION],
                                                          time_utils.SECONDS)

        before_action = item['action']

    worked_time = time_utils.get_time_string_from_seconds(num_seconds)

    return worked_time
