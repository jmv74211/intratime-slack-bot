import pymongo

from intratime_slack_bot.config import settings
from intratime_slack_bot.lib import warehouse, logger, codes, messages

# ----------------------------------------------------------------------------------------------------------------------


MONGO_CLIENT = pymongo.MongoClient(warehouse.MONGO_DB_SERVER)
db = MONGO_CLIENT['intratime_slack_bot']
user_collection = db['user']

USER_MODEL = ['user_id', 'username', 'password', 'intratime_mail', 'registration_date', 'last_registration_date']

# ----------------------------------------------------------------------------------------------------------------------


def user_exist(user_id):
    """
    Function to check if an user is already registered

    Parameters
    ----------
    user_id: str
        user identifier

    Returns
    -------
    boolean:
        True if the user exists, False otherwise
    """

    if user_collection.count_documents({'user_id': user_id}) <= 0:
        return False

    return True

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

# ----------------------------------------------------------------------------------------------------------------------


def add_user(data, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to add a user in the database

    Parameters
    ----------
    data: dict
        User data
    log_file: str
        Log file when the action will be logged in case of failure

    Returns
    -------
    int:
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.USER_ALREADY_EXIST if the user is already registered in the database
        codes.USER_CREATION_ERROR if the user could not be inserted to the database due to db error
        codes.SUCCESS if the user has been inserted successfully
    """

    if not validate_data(data, USER_MODEL):
        logger.log(file=log_file, level=logger.ERROR,
                   custom_message=messages.make_message(3005, f"Expected model {USER_MODEL} and got this data: {data}"))
        return codes.BAD_USER_DATA

    if user_exist(data['user_id']):
        logger.log(file=log_file, level=logger.ERROR, message_id=3010)
        return codes.USER_ALREADY_EXIST

    insert_request = user_collection.insert_one(data)

    if insert_request.inserted_id is None:
        logger.log(file=log_file, level=logger.ERROR, message_id=3006)
        return codes.USER_CREATION_ERROR

    logger.log(file=log_file, level=logger.INFO, custom_message=messages.make_message(2001, f"Data = {data}"))
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def delete_user(user_id, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to delete a user from the database

    Parameters
    ----------
    user_id: str
        User identifier

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.USER_DELETE_ERROR if the user could not be deleted from the database due to db error
        codes.SUCCESS if the user has been deleted successfully
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    delete_request = user_collection.delete_one({'user_id': user_id})

    if delete_request.deleted_count <= 0:
        logger.log(file=log_file, level=logger.ERROR, message_id=3008)
        return codes.USER_DELETE_ERROR

    logger.log(file=log_file, level=logger.INFO, message_id=2002)
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def update_user(user_id, new_data, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to update the user information in the database

    Parameters
    ----------
    user_id: str
        User identifier
    new_data: dict
        New user data

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.USER_UPDATE_ERROR if the user could not be update in the database due to db error
        codes.SUCCESS if the user has been updated successfully
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    if not validate_data(new_data, USER_MODEL):
        logger.log(file=log_file, level=logger.ERROR,
                   custom_message=messages.make_message(3005,
                                                        f"Expected model {USER_MODEL} and got this data: {new_data}"))
        return codes.BAD_USER_DATA

    update_request = user_collection.update_one({'user_id': user_id}, {'$set': new_data})

    if update_request.modified_count <= 0:
        logger.log(file=log_file, level=logger.ERROR, message_id=3009)
        return codes.USER_UPDATE_ERROR

    logger.log(file=log_file, level=logger.INFO, message_id=2003)
    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def get_user_data(user_id, log_file=settings.USER_SERVICE_LOG_FILE):
    """
    Function to get the user information from the database

    Parameters
    ----------
    user_id: str
        User identifier

    Returns
    -------
    dict:
        User information
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
    """

    if not user_exist(user_id):
        logger.log(file=log_file, level=logger.ERROR, message_id=3007)
        return codes.USER_NOT_FOUND

    user_data = user_collection.find_one({'user_id': user_id})

    return user_data

# ----------------------------------------------------------------------------------------------------------------------


def get_all_users_data():
    """
    Function to get all users information from the database

    Returns
    -------
    list:
        List with user information
    """

    return [user for user in user_collection.find()]
