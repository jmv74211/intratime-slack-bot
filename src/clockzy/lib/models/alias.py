from clockzy.lib.db.db_schema import ALIAS_TABLE
from clockzy.lib.db.database_interface import run_query


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
        """Save the alias information in the database."""
        add_alias_query = f"INSERT INTO {ALIAS_TABLE} VALUES ('{self.user_name}', '{self.alias}');"
        run_query(add_alias_query)

    def delete(self):
        """Delete the alias data from the database."""
        delete_alias_query = f"DELETE FROM {ALIAS_TABLE} WHERE user_name='{self.user_name}'"
        run_query(delete_alias_query)

    def update(self):
        """Update the alias information from the database."""
        update_alias_query = f"UPDATE {ALIAS_TABLE} SET user_name='{self.user_name}', " \
                             f"alias='{self.alias}' WHERE user_name='{self.user_name}'"
        run_query(update_alias_query)
