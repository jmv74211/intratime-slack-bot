import pymongo

from intratime_slack_bot.lib import warehouse

# ----------------------------------------------------------------------------------------------------------------------

MONGO_CLIENT = pymongo.MongoClient(warehouse.MONGO_DB_SERVER)
DB = MONGO_CLIENT['intratime_slack_bot']
USER_COLLECTION = DB['user']
REGISTRATION_COLLECTION = DB['registration']
HISTORY_COLLECTION = DB['history']

USER_MODEL = ['user_id', 'username', 'password', 'intratime_mail', 'registration_date', 'last_registration_date']
HISTORY_MODEL = ['date_time', 'username', 'user_id', 'command', 'parameters']

# ----------------------------------------------------------------------------------------------------------------------


def validate_data(data, model):
    """
    Function verify the data structure according to a model

    Parameters
    ----------
    data: dict
        Input data

    model: list
        List of required fields

    Returns
    -------
    boolean:
        True if data structure is OK, False otherwise
    """

    if data is None:
        return False

    for required_field in model:
        if required_field not in data:
            return False

    return True
