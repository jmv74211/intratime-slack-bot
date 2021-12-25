from clockzy.lib.db.db_schema import CLOCK_TABLE
from clockzy.lib.handlers.codes import ITEM_ALREADY_EXISTS, ITEM_NOT_EXISTS
from clockzy.lib.db.database_interface import run_query_getting_status, get_last_insert_id, item_exists


class Clock:
    """Clock ORM (Object–relational mapping)

    Args:
        user_id (str): User id that has clocked the action.
        action (str): Action to clock [IN, PAUSE, RETURN, OUT].
        date_time (str): Datetime when the action has been registered.

    Attributes:
        id (int): Clock identifier.
        user_id (str): User id that has clocked the action.
        action (str): Action to clock [IN, PAUSE, RETURN, OUT].
        date_time (str): Datetime when the action has been registered.
    """
    def __init__(self, user_id, action, date_time):
        self.id = None
        self.user_id = user_id
        self.action = action
        self.date_time = date_time

    def __str__(self):
        """Define how the class object will be displayed."""
        return f"id: {self.id}, user_id: {self.user_id}, action: {self.action}, date_time: {self.date_time}"

    def save(self):
        """Save the clock information in the database.

        Returns:
            int: Operation status code..
        """
        add_clock_query = f"INSERT INTO {CLOCK_TABLE} VALUES (null, '{self.user_id}', '{self.action}', " \
                          f"'{self.date_time}');"

        if self.id and item_exists({'id': self.id}, CLOCK_TABLE):
            return ITEM_ALREADY_EXISTS

        query_status_code = run_query_getting_status(add_clock_query)
        self.id = get_last_insert_id(CLOCK_TABLE)

        return query_status_code

    def delete(self):
        """Delete the clock data from the database.

        Returns:
            int: Operation status code..
        """
        delete_clock_query = f"DELETE FROM {CLOCK_TABLE} WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, CLOCK_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(delete_clock_query)

    def update(self):
        """Update the clock information from the database.

        Returns:
            int: Operation status code..
        """
        update_clock_query = f"UPDATE {CLOCK_TABLE} SET id='{self.id}', user_id='{self.user_id}', " \
                             f"action='{self.action}', date_time='{self.date_time}' WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, CLOCK_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(update_clock_query)
