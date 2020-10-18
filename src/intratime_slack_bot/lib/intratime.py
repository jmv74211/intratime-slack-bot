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
    datetime_from = time_utils.get_past_datetime_from_current_datetime(2592000)  # 1 month
    datetime_to = time_utils.get_current_date_time()
    return get_user_clocks(token, datetime_from, datetime_to, None, log_file)[0]

# ----------------------------------------------------------------------------------------------------------------------


def get_last_clock_type(token, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    return get_action_name(get_last_clock(token, log_file)['INOUT_TYPE'])

# ----------------------------------------------------------------------------------------------------------------------


def user_can_clock_this_action(token, action):
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
