import requests
import json
from datetime import datetime

from http import HTTPStatus
from intratime_slack_bot.lib import logger, codes, messages
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


def get_action(action, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
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


def check_user_credentials(email, password, log_file=settings.INTRATIME_SERVICE_LOG_FILE):
    """
    Function to check if user authentication is successfull

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
        Log file when the action will be logged in case of failur

    Returns
    -------
    int:
       codes.SUCCESS if clocking has been successful
       codes.INTRATIME_NO_RESPONSE if intratime can not response the request.
       codes.INTRATIME_API_CONNECTION_ERROR if there is a Intratime API connection error
    """

    # Add user token to intratime header request
    INTRATIME_API_HEADER.update({'token': token})
    filtered_data = []

    try:
        request = requests.get(url=INTRATIME_API_USER_CLOCKINGS_PATH, headers=INTRATIME_API_HEADER)

        try:
            data = request.json()

            start_date = datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S')
            end_date = datetime.strptime(datetime_to, '%Y-%m-%d %H:%M:%S')

            for item in data:
                date = datetime.strptime(item['INOUT_DATE'], '%Y-%m-%d %H:%M:%S')

                # If date is between datetime_from and datetime_to
                if start_date <= date <= end_date:
                    if action is None or (action is not None and get_action(action) == item['INOUT_TYPE']):
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
        Log file when the action will be logged in case of failur

    Returns
    -------
    int:
       codes.SUCCESS if clocking has been successful
       codes.INTRATIME_AUTH_ERROR if user authentication has failed
       codes.INTRATIME_API_CONNECTION_ERROR if there is a Intratime API connection error
    """

    date_time = logger.get_current_date_time()

    api_action = get_action(action)

    # Add user token to intratime header request
    INTRATIME_API_HEADER.update({'token': token})

    payload = f"user_action={api_action}&user_use_server_time={False}&user_timestamp={date_time}"

    try:
        request = requests.post(url=INTRATIME_API_CLOCKING_PATH, data=payload, headers=INTRATIME_API_HEADER)
        if request.status_code == HTTPStatus.CREATED:
            user_info_message = f"- user: {email}, action: {action}"
            logger.log(file=log_file, level=logger.INFO, custom_message=messages.make_message(2000, user_info_message))
            user.update_last_registration_datetime(user.get_user_id(email, log_file), log_file)
            return codes.SUCCESS
        else:
            logger.log(file=log_file, level=logger.ERROR, message_id=3004)
            return codes.INTRATIME_AUTH_ERROR
    except ConnectionError:
        logger.log(file=log_file, level=logger.ERROR, message_id=3002)
        return codes.INTRATIME_API_CONNECTION_ERROR

# ----------------------------------------------------------------------------------------------------------------------
