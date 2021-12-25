from clockzy.lib.utils.time import get_current_date_time
from clockzy.lib.db.db_schema import USER_TABLE
from clockzy.lib.handlers.codes import ITEM_ALREADY_EXISTS, ITEM_NOT_EXISTS
from clockzy.lib.db.database_interface import run_query_getting_status, item_exists


class User:
    """User ORM (Object–relational mapping)

    Args:
        id (str): User identifier.
        user_name (str): User name.
        password (str): User password.
        email (str): User email.

    Attributes:
        id (str): User identifier.
        user_name (str): User name.
        password (str): User password.
        email (str): User email.
        entry_data (str): User creation datetime.
        last_registration_date (str): Datetime of the user's last clock.
    """
    def __init__(self, id, user_name, password=None, email=None):
        self.id = id
        self.user_name = user_name
        self.password = password
        self.email = email

        current_date_time = get_current_date_time()

        self.entry_data = current_date_time
        self.last_registration_date = current_date_time

    def __str__(self):
        """Define how the class object will be displayed."""
        return f"id: {self.id}, user_name: {self.user_name}, password: {self.password}, email: {self.email}, " \
               f"entry_data: {self.entry_data}, last_registration_date: {self.last_registration_date}"

    def save(self):
        """Save the user information in the database.

        Returns:
            int: Operation status code..
        """
        add_user_query = f"INSERT INTO {USER_TABLE} VALUES ('{self.id}', '{self.user_name}', '{self.password}', " \
                         f"'{self.email}', '{self.entry_data}', '{self.last_registration_date}');"

        if item_exists({'id': self.id}, USER_TABLE):
            return ITEM_ALREADY_EXISTS

        return run_query_getting_status(add_user_query)

    def delete(self):
        """Delete the user from the database.

        Returns:
            int: Operation status code..
        """
        delete_user_query = f"DELETE FROM {USER_TABLE} WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, USER_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(delete_user_query)

    def update(self):
        """Update the current user information from the database.

        Returns:
            int: Operation status code..
        """
        update_user_query = f"UPDATE {USER_TABLE} SET id='{self.id}', user_name='{self.user_name}', " \
                            f"password='{self.password}', email='{self.email}', entry_data='{self.entry_data}', " \
                            f"last_registration_date='{self.last_registration_date}' WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, USER_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(update_user_query)
