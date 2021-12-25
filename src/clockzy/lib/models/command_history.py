from clockzy.lib.db.db_schema import COMMANDS_HISTORY_TABLE
from clockzy.lib.handlers.codes import ITEM_ALREADY_EXISTS, ITEM_NOT_EXISTS
from clockzy.lib.db.database_interface import run_query_getting_status, get_last_insert_id, item_exists


class CommandHistory:
    """CommandHistory ORM (Object–relational mapping)

    Args:
        user_id (str): User id that has executed the command.
        command (str): Command executed.
        parameters (str): Command parameters.
        date_time (str): Datetime when the command has been executed.

    Attributes:
        id (int): Command history identifier.
        user_id (str): User id that has executed the command.
        command (str): Command executed.
        parameters (str): Command parameters.
        date_time (str): Datetime when the command has been executed.
    """
    def __init__(self, user_id, command, parameters, date_time):
        self.id = None
        self.user_id = user_id
        self.command = command
        self.parameters = parameters
        self.date_time = date_time

    def __str__(self):
        """Define how the class object will be displayed."""
        return f"id: {self.id}, user_id: {self.user_id}, command: {self.command}, parameters: {self.parameters}, " \
               f"date_time: {self.date_time}"

    def save(self):
        """Save the command history information in the database.

        Returns:
            int: Operation status code.
        """
        add_command_query = f"INSERT INTO {COMMANDS_HISTORY_TABLE} VALUES (null, '{self.user_id}', '{self.command}', " \
                            f"'{self.parameters}', '{self.date_time}');"

        if self.id and item_exists({'id': self.id}, COMMANDS_HISTORY_TABLE):
            return ITEM_ALREADY_EXISTS

        query_status_code = run_query_getting_status(add_command_query)
        self.id = get_last_insert_id(COMMANDS_HISTORY_TABLE)

        return query_status_code

    def delete(self):
        """Delete the command history data from the database.

        Returns:
            int: Operation status code.
        """
        delete_command_query = f"DELETE FROM {COMMANDS_HISTORY_TABLE} WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, COMMANDS_HISTORY_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(delete_command_query)

    def update(self):
        """Update the command history information from the database.

        Returns:
            int: Operation status code.
        """
        update_command_query = f"UPDATE {COMMANDS_HISTORY_TABLE} SET id='{self.id}', user_id='{self.user_id}', " \
                               f"command='{self.command}', parameters='{self.parameters}', " \
                               f"date_time='{self.date_time}' WHERE id='{self.id}'"

        if not item_exists({'id': self.id}, COMMANDS_HISTORY_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(update_command_query)
