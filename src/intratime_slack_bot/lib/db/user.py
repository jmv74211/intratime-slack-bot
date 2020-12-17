from intratime_slack_bot.config import settings
from intratime_slack_bot.lib.db.database import validate_data, USER_COLLECTION, USER_MODEL, LOGGER
from intratime_slack_bot.lib import warehouse, codes, messages, time_utils, logger

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

    if USER_COLLECTION.count_documents({'user_id': user_id}) <= 0:
        return False

    return True

# ----------------------------------------------------------------------------------------------------------------------


def add_user(data):
    """
    Function to add a user in the database

    Parameters
    ----------
    data: dict
        User data

    Returns
    -------
    int:
        codes.BAD_USER_DATA if the data structure is no correct (Missing fields...)
        codes.USER_ALREADY_EXIST if the user is already registered in the database
        codes.USER_CREATION_ERROR if the user could not be inserted to the database due to db error
        codes.SUCCESS if the user has been inserted successfully
    """

    if not validate_data(data, USER_MODEL):
        LOGGER.error(messages.get(3028))
        return codes.BAD_USER_DATA

    if user_exist(data['user_id']):
        LOGGER.error(messages.get(3010))
        return codes.USER_ALREADY_EXIST

    insert_request = USER_COLLECTION.insert_one(data)

    if insert_request.inserted_id is None:
        LOGGER.error(messages.get(3006))
        return codes.USER_CREATION_ERROR

    LOGGER.info(messages.get(2001, data['user_id']))

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def delete_user(user_id):
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
        LOGGER.error(messages.get(3008, "user not exists"))
        return codes.USER_NOT_FOUND

    delete_request = USER_COLLECTION.delete_one({'user_id': user_id})

    if delete_request.deleted_count <= 0:
        LOGGER.error(messages.get(3008))
        return codes.USER_DELETE_ERROR

    LOGGER.info(messages.get(2002, user_id))

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def update_user(user_id, new_data):
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
        LOGGER.error(messages.get(3009, "user not exists"))
        return codes.USER_NOT_FOUND

    if not validate_data(new_data, USER_MODEL):
        LOGGER.error(messages.get(3028))
        return codes.BAD_USER_DATA

    update_request = USER_COLLECTION.update_one({'user_id': user_id}, {'$set': new_data})

    if update_request.modified_count <= 0:
        LOGGER.error(messages.get(3009))
        return codes.USER_UPDATE_ERROR

    LOGGER.info(messages.get(2004, f"user_id = {user_id}"))

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def get_user_data(user_id):
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
        LOGGER.error(messages.get(3009, "user not exists"))
        return codes.USER_NOT_FOUND

    user_data = USER_COLLECTION.find_one({'user_id': user_id})

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

    return [user for user in USER_COLLECTION.find()]


# ----------------------------------------------------------------------------------------------------------------------

def update_last_registration_datetime(user_id):
    """
    Function to update the last registration user info

    Parameters
    ----------
    user_id: str
        User identifier

    Returns
    -------
    int:
        codes.USER_NOT_FOUND if the user_id does not correspond with a registered user
        codes.USER_UPDATE_ERROR if the info could not be update in the database due to db error
        codes.SUCCESS if the data has been updated successfully
    """

    if not user_exist(user_id):
        LOGGER.error(messages.get(3009, "user not exists"))
        return codes.USER_NOT_FOUND

    user_data = get_user_data(user_id)

    try:
        user_data['last_registration_date'] = time_utils.get_current_date_time()
    except KeyError:
        LOGGER.error(messages.get(3012))

    update_request = USER_COLLECTION.update_one({'user_id': user_id}, {'$set': user_data})

    if update_request.modified_count <= 0:
        LOGGER.error(messages.get(3009))
        return codes.USER_UPDATE_ERROR

    return codes.SUCCESS

# ----------------------------------------------------------------------------------------------------------------------


def get_user_id(email):
    """
    Function to update the last registration user info

    Parameters
    ----------
    email: str
        User email

    Returns
    -------
    str:
        user_id if the email is correct
    int:
        codes.BAD_USER_EMAIL if the email does not correspond with a registered user
    """

    user_data = USER_COLLECTION.find_one({"intratime_mail": email})

    if user_data is None:
        return codes.BAD_USER_EMAIL

    return user_data['user_id']
