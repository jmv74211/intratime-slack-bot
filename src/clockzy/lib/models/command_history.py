from clockzy.lib.db.db_schema import COMMANDS_HISTORY_TABLE
from clockzy.lib.db.database_interface import run_query, run_query, get_last_insert_id


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
        """Save the command history information in the database."""
        add_command_query = f"INSERT INTO {COMMANDS_HISTORY_TABLE} VALUES (null, '{self.user_id}', '{self.command}', " \
                            f"'{self.parameters}', '{self.date_time}');"
        run_query(add_command_query)
        self.id = get_last_insert_id(COMMANDS_HISTORY_TABLE)

    def delete(self):
        """Delete the command history data from the database."""
        delete_command_query = f"DELETE FROM {COMMANDS_HISTORY_TABLE} WHERE id='{self.id}'"
        run_query(delete_command_query)

    def update(self):
        """Update the command history information from the database."""
        update_command_query = f"UPDATE {COMMANDS_HISTORY_TABLE} SET id='{self.id}', user_id='{self.user_id}', " \
                               f"command='{self.command}', parameters='{self.parameters}', " \
                               f"date_time='{self.date_time}' WHERE id='{self.id}'"
        run_query(update_command_query)
