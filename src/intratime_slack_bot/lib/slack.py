import requests
import time
import json

from http import HTTPStatus

from intratime_slack_bot.lib import codes, warehouse, logger, slack_ui, intratime, crypt, time_utils, messages
from intratime_slack_bot.lib.messages import make_message
from intratime_slack_bot.lib.db import user
from intratime_slack_bot.config import settings

# ----------------------------------------------------------------------------------------------------------------------

# API CALLBACKS
ADD_USER_CALLBACK = 'sign_up'
UPDATE_USER_CALLBACK = 'update_user'
DELETE_USER_CALLBACK = 'delete_user'
CLOCK_CALLBACK = 'clock'
CLOCK_HISTORY_CALLBACK = 'user_clock_history'
TIME_HISTORY_CALLBACK = 'user_time_history'
WORKED_TIME_CALLBACK = 'user_worked_time'
TODAY_INFO_CALLBACK = 'today_info'
COMMAND_HELP_CALLBACK = 'command_help'


# UI ERRORS
USER_ALREADY_REGISTERED_MESSAGE = {'errors': [{'name': 'email', 'error': messages.USER_ALREADY_REGISTERED}]}
BAD_CREDENTIALS = {'errors': [
                        {'name': 'email', 'error': messages.BAD_CREDENTIALS},
                        {'name': 'password', 'error': messages.BAD_CREDENTIALS}
                    ]}
DELETE_USER_NOT_FOUND = {'errors': [{'name': 'delete', 'error': messages.USER_NOT_FOUND}]}
UPDATE_USER_NOT_FOUND = {'errors': [{'name': 'email', 'error': messages.USER_NOT_FOUND}]}
CLOCKING_USER_NOT_FOUND = {'errors': [{'name': 'action', 'error': messages.USER_NOT_FOUND}]}
CLOCKING_BAD_USER_CREDENTIALS = {'errors': [{'name': 'action', 'error': messages.USER_NOT_FOUND}]}

# ----------------------------------------------------------------------------------------------------------------------


def validate_message(message):
    """
    Function to validate a slack message to send

    Parameters
    ----------
    message: str
        Message to post

    Returns
    -------
    boolean:
        True if message format is valid, False otherwise
    """
    if isinstance(message, str):
        return True
    elif isinstance(message, list) and len(message) > 0 and isinstance(message[0], dict):
        return True

    return False

# ----------------------------------------------------------------------------------------------------------------------


def post_private_message(message, channel,  mgs_type='text', log_file=settings.SLACK_SERVICE_LOG_FILE,
                         token=settings.SLACK_API_USER_TOKEN, as_bot_user=False):
    """
    Function to post a private message in a slack channel

    Parameters
    ----------
    message: str
        Message to post
    channel: str
        Channel ID
    mgs_type: str
        enum: 'text', 'attachments' or 'blocks' depending on message type
    log_file: str
        Log file when the action will be logged in case of failure or success
    token: str
        Slack API user token
    as_bot_user: boolean
        Specifies whether the message is sent as a bot user or a normal user

    Returns
    -------
    int:
        codes.INVALID_VALUE if the message_type parameter has invalid value
        codes.BAD_SLACK_API_AUTH_CREDENTIALS if the API request could not be resolved due to credentials issue
        codes.BAD_REQUEST_DATA if data sent is not correct
        codes.INTERNAL_SERVER_ERROR if there is some server error
        codes.UNDEFINED_ERROR if the error is unknown
        codes.SUCCESS if the message has ben posted successfully
    """

    if not validate_message(message):
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3018, f"of message parameter"))
        return codes.INVALID_VALUE

    time.sleep(1)  # Wait one second to send the API request due to rate limit (1/sec)

    headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf8'}

    if as_bot_user:
        token = settings.SLACK_API_BOT_TOKEN

    request = requests.post(f"{warehouse.SLACK_POST_MESSAGE_URL}?token={token}&channel={channel}&"
                            f"{mgs_type}={message}", headers=headers)

    if request.status_code != HTTPStatus.OK:
        if(request.status_code == HTTPStatus.REQUEST_URI_TOO_LONG):
            post_private_message(messages.write_slack_message_too_long(), channel, mgs_type='blocks', token=token,
                                 as_bot_user=True)
            return codes.MESSAGE_TOO_LONG
        elif request.status_code != HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.ERROR, message_id=3014)
            return codes.BAD_SLACK_API_AUTH_CREDENTIALS
        elif request.status_code != HTTPStatus.BAD_REQUEST:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"Payload = {payload}"))
            return codes.BAD_REQUEST_DATA
        elif request.status_code != HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3016, f"when posting a message"))
            return codes.INTERNAL_SERVER_ERROR
        else:
            logger.log(file=log_file, level=logger.ERROR,
                       custom_message=make_message(3017, f"Status code = {request.status_code}"))
            return codes.UNDEFINED_ERROR

    if request.text != 'ok':
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"{request.text}"))
        return codes.BAD_REQUEST_DATA

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def post_ephemeral_message(message, channel, user_id, log_file=settings.SLACK_SERVICE_LOG_FILE,
                           token=settings.SLACK_API_USER_TOKEN, as_bot_user=False):
    """
    Function to post a ephemeral message in a slack channel

    Parameters
    ----------
    message: str
        Message to post
    channel: str
        Channel ID
    user_id: str
        Destination user_id
    log_file: str
        Log file when the action will be logged in case of failure or success
    token: str
        Slack API user token
    as_bot_user: boolean
        Specifies whether the message is sent as a bot user or a normal user

    Returns
    -------
    int:
        codes.INVALID_VALUE if the message_type parameter has invalid value
        codes.BAD_SLACK_API_AUTH_CREDENTIALS if the API request could not be resolved due to credentials issue
        codes.BAD_REQUEST_DATA if data sent is not correct
        codes.INTERNAL_SERVER_ERROR if there is some server error
        codes.UNDEFINED_ERROR if the error is unknown
        codes.SUCCESS if the message has ben posted successfully
    """

    if not validate_message(message):
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3018, f"of message parameter"))
        return codes.INVALID_VALUE

    time.sleep(1)  # Wait one second to send the API request due to rate limit (1/sec)

    headers = {'content-type': 'application/x-www-form-urlencoded', 'charset': 'utf8'}

    if isinstance(message, str):
        message_parameter = 'text'
    else:
        message_parameter = 'attachments'

    if as_bot_user:
        token = settings.SLACK_API_BOT_TOKEN

    request = requests.post(f"{warehouse.SLACK_POST_EPHEMERAL_MESSAGE_URL}?token={token}&channel={channel}&"
                            f"{message_parameter}={message}&user={user_id}", headers=headers)

    if request.status_code != HTTPStatus.OK:
        if request.status_code != HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.ERROR, message_id=3014)
            return codes.BAD_SLACK_API_AUTH_CREDENTIALS
        elif request.status_code != HTTPStatus.BAD_REQUEST:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"Payload = {payload}"))
            return codes.BAD_REQUEST_DATA
        elif request.status_code != HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3016, f"when posting a message"))
            return codes.INTERNAL_SERVER_ERROR
        else:
            logger.log(file=log_file, level=logger.ERROR,
                       custom_message=make_message(3017, f"Status code = {request.status_code}"))
            return codes.UNDEFINED_ERROR

    if request.text != 'ok':
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"{request.text}"))
        return codes.BAD_REQUEST_DATA

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def post_ephemeral_response_message(message, response_url, mgs_type='text', log_file=settings.SLACK_SERVICE_LOG_FILE):
    """
    Function to post a ephemeral message in a slack channel given a response_url

    Parameters
    ----------
    message: str
        Message to post
    response_url: str
        Response url from user conversation
    mgs_type: str
        enum: 'text', 'attachments' or 'blocks' depending on message type
    log_file: str
        Log file when the action will be logged in case of failure or success

    Returns
    -------
    int:
        codes.INVALID_VALUE if the message_type parameter has invalid value
        codes.BAD_SLACK_API_AUTH_CREDENTIALS if the API request could not be resolved due to credentials issue
        codes.BAD_REQUEST_DATA if data sent is not correct
        codes.INTERNAL_SERVER_ERROR if there is some server error
        codes.UNDEFINED_ERROR if the error is unknown
        codes.SUCCESS if the message has ben posted successfully
    """
    if not validate_message(message):
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3018, f"of message parameter"))
        return codes.INVALID_VALUE
    payload = {mgs_type: message, 'response_type': 'ephemeral'}
    headers = {'content-type': 'application/json'}

    request = requests.post(response_url, json=payload, headers=headers)

    if request.status_code != HTTPStatus.OK:
        if request.status_code != HTTPStatus.UNAUTHORIZED:
            logger.log(file=log_file, level=logger.ERROR, message_id=3014)
            return codes.BAD_SLACK_API_AUTH_CREDENTIALS
        elif request.status_code != HTTPStatus.BAD_REQUEST:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"Payload = {payload}"))
            return codes.BAD_REQUEST_DATA
        elif request.status_code != HTTPStatus.INTERNAL_SERVER_ERROR:
            logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3016, f"when posting a message"))
            return codes.INTERNAL_SERVER_ERROR
        else:
            logger.log(file=log_file, level=logger.ERROR,
                       custom_message=make_message(3017, f"Status code = {request.status_code}"))
            return codes.UNDEFINED_ERROR

    if request.text != 'ok':
        logger.log(file=log_file, level=logger.ERROR, custom_message=make_message(3015, f"{request.text}"))
        return codes.BAD_REQUEST_DATA

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def decode_slack_args(data):
    """
    Function to decode slack response args from x=1&y=2&z=3 format to {x:1,y:2,z:3}

    Parameters
    ----------
    data: str
        Slack string args to decode

    Returns
    ------
    dict:
        Slack args in dict format
    """

    elements = [pair_value for item in data.split('&') for pair_value in item.split('=')]
    return dict(zip(elements[0::2], elements[1::2]))

# ----------------------------------------------------------------------------------------------------------------------


def get_api_data(data, callback_id):
    """
    Function get the API data needed to create a modal dialog

    Parameters
    ----------
    data: str
        Slack response data

    callback_id: string
        Identifier to know which dialog to show

    Returns
    ------
    dict:
        Slack API data to open a new modal dialog
    """
    data = decode_slack_args(data)

    if callback_id == CLOCK_CALLBACK:
        dialog = slack_ui.get_clock_ui()
    elif callback_id == WORKED_TIME_CALLBACK:
        dialog = slack_ui.get_user_worked_time_ui()
    elif callback_id == CLOCK_HISTORY_CALLBACK or callback_id == TIME_HISTORY_CALLBACK:
        dialog = slack_ui.get_user_history_ui(callback_id)
    elif callback_id == ADD_USER_CALLBACK:
        dialog = slack_ui.get_sign_up_ui()
    elif callback_id == UPDATE_USER_CALLBACK:
        dialog = slack_ui.get_update_user_ui()
    elif callback_id == DELETE_USER_CALLBACK:
        dialog = slack_ui.get_delete_user_ui()
    else:
        return None

    api_data = {
        'token': settings.SLACK_API_USER_TOKEN,
        'trigger_id': data['trigger_id'],
        'dialog': json.dumps(dialog)
    }

    return api_data

# ----------------------------------------------------------------------------------------------------------------------


def generate_clock_message(data):
    """
    Function to generate a custom message when a user clocks an action

    Parameters
    ----------
    data: dict
        Message data

    Returns
    ------
    list:
        Block list with a custom message to show in slack client
    """

    if 'intratime_mail' not in data or 'datetime' not in data or 'action' not in data:
        return codes.BAD_REQUEST_DATA

    IMAGE_BASE_URL = 'https://raw.githubusercontent.com/jmv74211/tools/master/images/repository/intratime-slack-app/ui/'

    if data['action'] != intratime.IN_ACTION and data['action'] != intratime.PAUSE_ACTION and \
       data['action'] != intratime.RETURN_ACTION and data['action'] != intratime.OUT_ACTION:
        return codes.BAD_REQUEST_DATA

    block_message = [
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{messages.CLOCKING_ACTION_SUCCESS}\n *Email*: {data['intratime_mail']}\n *Action*: "
                        f"{data['action'].upper()}\n *Datetime*: {data['datetime']}"
            },
            "accessory": {
                "type": "image",
                "image_url": f"{IMAGE_BASE_URL}{data['action']}_5.png",
                "alt_text": "Clocking action image"
            }
        },
        {
            "type": "divider"
        },

    ]

    return block_message

# ----------------------------------------------------------------------------------------------------------------------


def process_clock_history_action(token, action):
    """
    Function to process clock history action and returns user selected data

    Parameters
    ----------
    token: str
        Intratime user token authentication
    action: str
        Callback action

    Returns
    -------
    tuple: (string)(list)
        (worked_hours)(history_data)
    int:
        codes.INVALID_HISTORY_ACTION if action is not supported
    """

    time_range = action.replace('_hours', '').replace('_history', '')

    data = intratime.get_clock_data_in_time_range(token, time_range)

    data.reverse()  # It is necessary to reverse the list to check and calculate the history hours

    worked_hours = intratime.get_worked_time(data)

    if 'hours' in action:
        return (worked_hours, [])

    return (worked_hours, data)

# ----------------------------------------------------------------------------------------------------------------------


def filter_clock_history_data(data, datetime_from, datetime_to):
    """
    Function to get the clock history data in a time range. e.g

    { datetime_1: [item_1, item_2], datetime_2: [item_3, item_4, item_5] }

    Parameters
    ----------
    data: dict
        Parsed clock data
    datetime_from: str
        Lower limit datetime in format %Y-%m-%d %H:%M:%S
    datetime_to: str
        Upper limit datetime in format %Y-%m-%d %H:%M:%S

    Returns
    -------
    dict:
        Filtered clock history data dictionary.
    """

    filter_data = [item for item in data if time_utils.date_included_in_range(datetime_from, datetime_to,
                   item['datetime'])]
    group_data = {}

    for item in filter_data:
        date = time_utils.convert_datetime_string_to_date_string(item['datetime'])
        if date in group_data:
            group_data[date].append(item)
        else:
            group_data[date] = [item]

    return group_data

# ----------------------------------------------------------------------------------------------------------------------


def process_interactive_data(data):
    """
    Function to process interactive data from slack service

    Parameters
    ----------
    data: dict
        Slack request data
    """

    if data['callback_id'] == CLOCK_CALLBACK:
        user_data = user.get_user_data(data['user']['id'])
        token = intratime.get_auth_token(user_data['intratime_mail'], crypt.decrypt(user_data['password']))
        user_can_clock_this_action = intratime.user_can_clock_this_action(token, data['submission']['action'])

        if not user_can_clock_this_action[0]:
            post_ephemeral_response_message(messages.set_custom_message('INVALID_CLOCKING_ACTION',
                                            [user_can_clock_this_action[1]]), data['response_url'], 'blocks')

        # Clock the action
        request_status = intratime.clocking(data['submission']['action'], token, user_data['intratime_mail'])

        if request_status != codes.SUCCESS:
            post_ephemeral_response_message(messages.set_custom_message('CLOCKING_ERROR', [request_status]),
                                            data['response_url'])
        # Check the clock action in user history
        clocking_check = intratime.get_user_clocks(token, time_utils.get_past_datetime_from_current_datetime(10),
                                                   time_utils.get_current_date_time(), data['submission']['action'])
        if len(clocking_check) == 0:
            post_ephemeral_response_message(messages.set_custom_message('CLOCKING_CHECK_ERROR', [request_status]),
                                            data['response_url'])

        clock_message = generate_clock_message({'intratime_mail': user_data['intratime_mail'],
                                                'datetime': time_utils.get_current_date_time(),
                                                'action': data['submission']['action']})

        post_ephemeral_response_message(clock_message, data['response_url'], 'blocks')

    elif data['callback_id'] == TODAY_INFO_CALLBACK:
        print("TODAY INFO")

    elif (data['callback_id'] == WORKED_TIME_CALLBACK or data['callback_id'] == CLOCK_HISTORY_CALLBACK or
          data['callback_id'] == TIME_HISTORY_CALLBACK):

        user_data = user.get_user_data(data['user']['id'])
        user_query_action = data['submission']['action']

        token = intratime.get_auth_token(user_data['intratime_mail'], crypt.decrypt(user_data['password']))
        worked_time, history = process_clock_history_action(token, user_query_action)

        custom_message = {
            'today_hours': 'on today',
            'week_hours': 'on this week',
            'month_hours': 'on this month'
        }

        if data['callback_id'] == WORKED_TIME_CALLBACK:
            message = messages.set_custom_message('WORKED_TIME', [custom_message[user_query_action], worked_time])
            post_ephemeral_response_message(message, data['response_url'])
        else:
            message_blocks = messages.generate_slack_history_report(token, user_query_action, history,
                                                                    worked_time, data['callback_id'])
            for block in message_blocks:
                post_private_message(block, data['user']['id'], mgs_type='blocks', as_bot_user=True)

    elif data['callback_id'] == ADD_USER_CALLBACK:
        cyphered_password = crypt.encrypt(data['submission']['password'])

        # Create new user in user service
        request_status = user.add_user({"user_id": data['user']['id'], "username": data['user']['name'],
                                        "password": cyphered_password,
                                        "intratime_mail": data['submission']['email'],
                                        "registration_date": time_utils.get_current_date_time(),
                                        "last_registration_date": time_utils.get_current_date_time()
                                        })

        if request_status != codes.SUCCESS:
            post_ephemeral_response_message(messages.set_custom_message('ADD_USER_ERROR', [request_status]),
                                            data['response_url'])

        post_ephemeral_response_message(messages.ADD_USER_SUCCESS, data['response_url'])

    elif data['callback_id'] == UPDATE_USER_CALLBACK:
        user_data = user.get_user_data(data['user']['id'])
        user_data['intratime_mail'] = data['submission']['email']
        user_data['password'] = crypt.encrypt(data['submission']['password'])

        # Update user info
        request_status = user.update_user(data['user']['id'], user_data)

        if request_status != codes.SUCCESS:
            post_ephemeral_response_message(messages.set_custom_message('UPDATE_USER_ERROR', [request_status]),
                                            data['response_url'])

        post_ephemeral_response_message(messages.UPDATE_USER_SUCCESS, data['response_url'])

    elif data['callback_id'] == DELETE_USER_CALLBACK:
        # Delete an user
        request_status = user.delete_user(data['user']['id'])

        if request_status != codes.SUCCESS:
            post_ephemeral_response_message(messages.set_custom_message('DELETE_USER_ERROR', [request_status]),
                                            data['response_url'])

        post_ephemeral_response_message(messages.DELETE_USER_SUCCESS, data['response_url'])

    elif data['callback_id'] == COMMAND_HELP_CALLBACK:
        print("COMMAND HELP")
