import pymysql

from clockzy.config.settings import DB_ROOT_USER, DB_ROOT_PASSWORD, DB_PORT, DB_HOST, DB_NAME


class Database:
    """Class to map the MYSQL database connection.

    Args:
        host (str): Database host DNS or IP.
        user (str): Database user to establish the connection.
        password (str): Database user password to establish the connection.
        database_name (str): Database name to connect.
        port (int): Database port to establish the connection.

    Attributes:
        host (str): Database host DNS or IP.
        user (str): Database user to establish the connection.
        password (str): Database user password to establish the connection.
        database_name (str): Database name to connect.
        port (int): Database port to establish the connection.
        database_connection (pymysql.connections.Connection): Database connection object.
    """
    def __init__(self, host=DB_HOST, user=DB_ROOT_USER, password=DB_ROOT_PASSWORD, database_name=DB_NAME, port=DB_PORT):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self.port = port

        self.database_connection = self.connect()

    def run_query(self, query, connection=None):
        """Run a query string in the database

        Args:
            query (str): Raw query to execute.
            connection (pymysql.connections.Connection): Database connection to use.

        Returns:
            pymysql.cursors.Cursor: Cursor object with the query results.
        """
        connection = connection if connection else self.database_connection
        db_cursor = connection.cursor()
        db_cursor.execute(query)

        return db_cursor

    def create_database(self, database_name):
        """Create the specified database

        args:
            database_name (str): Name of the database to create.
        """
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port)
        self.run_query(f"CREATE DATABASE IF NOT EXISTS {database_name};", connection=connection)

    def connect(self):
        """Create the connection to the database.

        Returns:
            connection (pymysql.connections.Connection): Database connection object.
        """
        return pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database_name,
                               port=self.port)

    def update(self, query):
        """Run an operation involving a modification to the database. For example, INSERT, UPDATE, DELETE... queries.

        In the event of an error, the operation will be rolled back.

        Args:
            query (str): Raw query to execute.
        """
        try:
            self.run_query(query)
            self.database_connection.commit()
        except:
            self.database_connection.rollback()

    def get_one(self, query):
        """Run a query and returns the first result obtained.

        Args:
            query (str): Raw query to execute.

        Returns:
            Array: Array with the results. Each element corresponds to the value of a field.
        """
        return self.run_query(query).fetchone()

    def get_all(self, query):
        """Run a query and returns the results obtained.

        Args:
            query (str): Raw query to execute.

        Returns:
            Array: Query results. Each element corresponds to the value of a field.
        """
        return self.run_query(query).fetchall()

    def get_row_count(self, query):
        """Run a query and returns the number of involved rows.

        Args:
            query (str): Raw query to execute.

        Returns:
            int: Number of involved rows.
        """
        return self.run_query(query).rowcount()

    def close(self):
        """Close the database connection"""
        self.database_connection.close()
