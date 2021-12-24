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
        self.database_connection = None

    def connect(self):
        """Create the connection to the database."""
        try:
            if self.database_connection is None:
                self.database_connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                                           database=self.database_name, port=self.port)
        except pymysql.MySQLError:
            print(f"Could not connect to the {self.host}:{self.port} {self.database_name} database")

    def run_query(self, query):
        """Run a query string in the database

        Args:
            query (str): Raw query to execute.

        Returns:
            - List(tuple): If SELECT query, returns the query results.
            - int: If non SELECT query, return the number of affected rows.
        """
        try:
            self.connect()
            with self.database_connection.cursor() as cursor:
                # If SELECT query, then execute the query and return the results
                if query.startswith('SELECT') or query.startswith('select'):
                    query_results = []

                    cursor.execute(query)
                    result = cursor.fetchall()

                    for row in result:
                        query_results.append(row)

                    return query_results

                # If no SELECT query, then execute the query and return the number of affected rows
                else:
                    try:
                        cursor.execute(query)
                        self.database_connection.commit()

                        return cursor.rowcount

                    except pymysql.MySQLError as e:
                        self.database_connection.rollback()
                        print(f"Error when executing query: {query}. Reason {e}")
                        return 0
        finally:
            self.close_connection()

    def create_database(self, database_name):
        """Create the specified database

        args:
            database_name (str): Name of the database to create.
        """
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port)
        with connection as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name};")
            connection.commit()
        connection.close()

    def close_connection(self):
        """Close the database connection"""
        if self.database_connection:
            self.database_connection.close()
            self.database_connection = None
