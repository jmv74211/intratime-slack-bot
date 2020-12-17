from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db.database import validate_data, HISTORY_COLLECTION, HISTORY_MODEL, LOGGER
from intratime_slack_bot.lib import time_utils, codes, logger


# ----------------------------------------------------------------------------------------------------------------------


MONITORING_LOGGER = logger.get_logger('monitoring', settings.LOGS_LEVEL)
CLOCKING_LOGGER = logger.get_logger('clocking', settings.LOGS_LEVEL)

# ----------------------------------------------------------------------------------------------------------------------


def add_history_register(data):
    """
    Function to register a user command action

    Parameters
    ----------
    data: dict
        User data

    Returns
    -------
    int:
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.ADD_HISTORY_ERROR if the command action could not be inserted to the database due to db error
        codes.SUCCESS if the user command action has been registered successfully
    """

    date_time = time_utils.get_current_date_time()

    data['date_time'] = date_time

    if not validate_data(data, HISTORY_MODEL):
        LOGGER.error(messages.get(3028))
        return codes.BAD_USER_DATA

    insert_request = HISTORY_COLLECTION.insert_one(data)

    if insert_request.inserted_id is None:
        LOGGER.error(messages.get(3029))
        return codes.ADD_HISTORY_ERROR

    MONITORING_LOGGER.info(data)

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def clock_user_action(user_id, user_name, action):
    """
    Function to register a user clock action

    Parameters
    ----------
    user_id: str
        User id
    user_name: str
        User name
    action: str
        Clock action

    Returns
    -------
    int:
        codes.SUCCESS if the user command action has been registered successfully
    """
    CLOCKING_LOGGER.info(f'The user {user_id} ({user_name}) has clocked {action}')

    return codes.SUCCESS
