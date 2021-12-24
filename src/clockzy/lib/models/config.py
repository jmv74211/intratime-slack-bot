from clockzy.lib.db.db_schema import CONFIG_TABLE
from clockzy.lib.db.database_interface import run_query


class Config:
    """Config ORM (Object–relational mapping)

    Args:
        user_id (str): User id belonging to the indicated configuration
        intratime_integration (boolean): True if the clocks are also registered in the intratime app, False otherwise.

    Attributes:
        user_id (str): User id belonging to the indicated configuration
        intratime_integration (boolean): True if the clocks are also registered in the intratime app, False otherwise.
    """
    def __init__(self, user_id, intratime_integration):
        self.user_id = user_id
        self.intratime_integration = intratime_integration

    def __str__(self):
        """Define how the class object will be displayed."""
        return f"user_id: {self.user_id}, intratime_integration: {self.intratime_integration}"

    def save(self):
        """Save the config information in the database."""
        add_config_query = f"INSERT INTO {CONFIG_TABLE} VALUES ('{self.user_id}', {self.intratime_integration});"
        run_query(add_config_query)

    def delete(self):
        """Delete the config data from the database."""
        delete_config_query = f"DELETE FROM {CONFIG_TABLE} WHERE user_id='{self.user_id}'"
        run_query(delete_config_query)

    def update(self):
        """Update the config information from the database."""
        update_config_query = f"UPDATE {CONFIG_TABLE} SET user_id='{self.user_id}', " \
                              f"intratime_integration={self.intratime_integration} WHERE user_id='{self.user_id}'"
        run_query(update_config_query)
