# ------------------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------------
# Import necessary libraries
import logging
import mysql.connector
import requests
from mysql.connector import Error, pooling

from lazzy_orm.logger import Logger  # Assuming Logger is a custom logging class

# ------------------------------------------------------------------------------
# LOGGER SETUP
# ------------------------------------------------------------------------------
# Configure logging for the connector module
connector_logger = Logger(log_file="connector.log", logger_name="connector_logger", level=logging.INFO).logger

# ------------------------------------------------------------------------------
# CONNECTOR CLASS
# ------------------------------------------------------------------------------
class Connector:
    """
    Encapsulates logic for connecting to MySQL databases, handling Azure-specific authentication if needed.
    """

    def __init__(self, host: str, user: str, database: str, port, is_azure_server: bool = False, password: str = "", client_id: str = ""):
        """
        Initializes the Connector object with connection parameters.

        Args:
            host (str): The hostname or IP address of the MySQL server.
            user (str): The username for MySQL authentication.
            database (str): The name of the database to connect to.
            port (int): The port number on which the MySQL server is listening.
            is_azure_server (bool, optional): True if connecting to an Azure MySQL server. Defaults to False.
            password (str, optional): The password for MySQL authentication (not required for Azure servers).
            client_id (str, optional): The client ID for Azure authentication.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.is_azure_server = is_azure_server
        self.port = port
        self.client_id = client_id

    def get_connection_config(self) -> dict:
        """
        Returns a dictionary containing MySQL connection parameters.

        Returns:
            dict: A dictionary with keys for 'host', 'user', 'password', 'database', and 'port'.
        """
        return {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'port': self.port,
        }

    def get_connection_pool(self) -> pooling.MySQLConnectionPool or None:
        """
        Creates a connection pool for efficient reusability of MySQL connections.

        Returns:
            pooling.MySQLConnectionPool: A connection pool object, or None if creation fails.
        """
        if self.is_azure_server:
            # Handle Azure-specific authentication using a token
            url = ("http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https%3A%2F"
                   "%2Fossrdbms-aad.database.windows.net&client_id=" + self.client_id)

            payload = {}
            headers = {
                'Metadata': 'true'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            json_response = response.json()
            access_token = json_response['access_token']
            self.password = access_token  # Set password to the access token

        try:
            connection_pool = pooling.MySQLConnectionPool(
                pool_name="Lazy_ORM_Pool",
                pool_size=10,  # Number of connections in the pool
                auth_plugin='mysql_native_password',
                pool_reset_session=True,  # Reset session variables for each connection
                **self.get_connection_config()
            )
            connector_logger.info(f"Connection pool created")
            return connection_pool
        except Error as e:
            connector_logger.error(f"Error creating connection pool: {e}")
            return None

    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            if connection.is_connected():
                connector_logger.info(f"Connected to MySQL database '{self.database}'")
                return connection
            else:
                connector_logger.error("Connection failed")
                return None
        except Error as e:
            connector_logger.error(f"Error: {e}")
            return None

    # show processlist;
    def show_process_list(self):
        """
        Retrieves the list of running processes from the MySQL server.

        Returns:
            list: A list of process information, or None if an error occurs.
        """
        try:
            pool = self.get_connection_pool()
            connection = pool.get_connection()
            cursor = connection.cursor()
            cursor.execute("SHOW FULL PROCESSLIST;")
            result = cursor.fetchall()
            connector_logger.info(f"Process List: {result}")
        except Error as e:
            connector_logger.error(f"Error: {e}")
