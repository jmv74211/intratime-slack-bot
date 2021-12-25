from clockzy.lib.db.db_schema import ALIAS_TABLE
from clockzy.lib.handlers.codes import ITEM_ALREADY_EXISTS, ITEM_NOT_EXISTS
from clockzy.lib.db.database_interface import run_query_getting_status, item_exists


class Alias:
    """Alias ORM (Object–relational mapping)

    Args:
        user_name (str): User name.
        alias (str): Aliases to add a second name to the specified user.

    Attributes:
        user_name (str): User name.
        alias (str): Aliases to add a second name to the specified user.
    """
    def __init__(self, user_name, alias):
        self.user_name = user_name
        self.alias = alias

    def __str__(self):
        """Define how the class object will be displayed."""
        return f"user_name: {self.user_name}, alias: {self.alias}"

    def save(self):
        """Save the alias information in the database.

        Returns:
            int: Operation status code.
        """
        add_alias_query = f"INSERT INTO {ALIAS_TABLE} VALUES ('{self.user_name}', '{self.alias}');"

        if item_exists({'alias': self.alias}, ALIAS_TABLE):
            return ITEM_ALREADY_EXISTS

        return run_query_getting_status(add_alias_query)

    def delete(self):
        """Delete the alias data from the database.

        Returns:
            int: Operation status code.
        """
        delete_alias_query = f"DELETE FROM {ALIAS_TABLE} WHERE user_name='{self.user_name}'"

        if not item_exists({'alias': self.alias}, ALIAS_TABLE):
            return ITEM_NOT_EXISTS

        return run_query_getting_status(delete_alias_query)

    def update(self):
        """Update the alias information from the database.

        Returns:
            int: Operation status code.
        """
        update_alias_query = f"UPDATE {ALIAS_TABLE} SET user_name='{self.user_name}', " \
                             f"alias='{self.alias}' WHERE user_name='{self.user_name}'"

        query_status_code = run_query_getting_status(update_alias_query)

        if not item_exists({'alias': self.alias}, ALIAS_TABLE):
            return ITEM_NOT_EXISTS

        return query_status_code
