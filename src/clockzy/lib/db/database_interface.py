"""
Module to group calls to the database.
"""

from clockzy.lib.db.database import Database
from pymysql import MySQLError


def run_query(query):
    """Run a non-commit query in the database.

    Args:
        query (String): Raw query to execute.

    Returns:
        - List(tuple): If SELECT query, returns the query results.
        - int: If non SELECT query, return the number of affected rows.
    """
    db = Database()
    results = db.run_query(query)

    if not query.startswith('SELECT') and not query.startswith('select') and results == 0:
        raise MySQLError(f"The {query} query has not affected any row")

    return results


def get_last_insert_id(table_name, identifier='id'):
    """Get the last

    Precondition:
        - Table identifier must be AUTO_INCREMENT

    Note:
     - LAST_INSERT_ID() does not work for this case due to the mysql connections.

    Args:
        table_name (str): Table name to get the last inserted id.
        identifier (str): Identifier field name (usually will be called: id)

    Returns:
        int: Last inserted ID.
    """
    results = run_query(f"SELECT {identifier} from {table_name} ORDER BY id desc LIMIT 1")

    return results[0][0] if len(results) > 0 else 0
