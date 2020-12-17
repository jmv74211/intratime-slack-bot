from intratime_slack_bot.lib.db.database import validate_data, HISTORY_COLLECTION, HISTORY_MODEL
from intratime_slack_bot.lib import time_utils, codes

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
        return codes.BAD_USER_DATA

    insert_request = HISTORY_COLLECTION.insert_one(data)

    if insert_request.inserted_id is None:
        return codes.ADD_HISTORY_ERROR

    return codes.SUCCESS
