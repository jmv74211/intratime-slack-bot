"""
Script to initialize the Clockzy database and tables environment
"""

from clockzy.lib.db.database import Database
from clockzy.config.settings import DB_NAME
from clockzy.lib.db import db_schema as dbs

TABLES = [dbs.USER_TABLE, dbs.CLOCK_TABLE, dbs.COMMANDS_HISTORY_TABLE, dbs.CONFIG_TABLE, dbs.ALIAS_TABLE]


if __name__ == '__main__':
    database = Database()

    # Create database if not exist
    database.create_database(DB_NAME)

    # Create the tables if not exist
    for table in TABLES:
        database.run_query(table)

    database.close()
