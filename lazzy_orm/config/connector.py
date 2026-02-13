# ------------------------------------------------------------------------------
# IMPORTS
# ------------------------------------------------------------------------------
# Import necessary libraries
import logging
from typing import Optional
import mysql.connector
import requests
from mysql.connector import Error, pooling

from lazzy_orm.logger import Logger
from lazzy_orm.exceptions import ConnectionError as LazzyConnectionError, ConfigurationError

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
    
    Args:
        host: The hostname or IP address of the MySQL server.
        user: The username for MySQL authentication.
        database: The name of the database to connect to.
        port: The port number on which the MySQL server is listening.
        is_azure_server: True if connecting to an Azure MySQL server.
        password: The password for MySQL authentication (not required for Azure servers).
        client_id: The client ID for Azure authentication.
        pool_size: Connection pool size (default: 10).
        pool_name: Connection pool name (default: "Lazy_ORM_Pool").
    """

    def __init__(
        self, 
        host: str, 
        user: str, 
        database: str, 
        port: int,
        is_azure_server: bool = False, 
        password: str = "", 
        client_id: str = "",
        pool_size: int = 10,
        pool_name: str = "Lazy_ORM_Pool"
    ):
        """Initializes the Connector object with connection parameters."""
        # Validate required parameters
        if not host:
            raise ConfigurationError("Host is required")
        if not user:
            raise ConfigurationError("User is required")
        if not database:
            raise ConfigurationError("Database is required")
        if not isinstance(port, int) or port <= 0:
            raise ConfigurationError("Port must be a positive integer")
        if pool_size <= 0:
            raise ConfigurationError("Pool size must be positive")
            
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.is_azure_server = is_azure_server
        self.port = port
        self.client_id = client_id
        self.pool_size = pool_size
        self.pool_name = pool_name
        self._connection_pool = None

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

    def _get_azure_token(self) -> str:
        """Retrieve Azure authentication token.
        
        Returns:
            Access token string
            
        Raises:
            LazzyConnectionError: If token retrieval fails
        """
        url = (
            "http://169.254.169.254/metadata/identity/oauth2/token?"
            "api-version=2018-02-01&resource=https%3A%2F%2Fossrdbms-aad.database.windows.net"
            f"&client_id={self.client_id}"
        )

        headers = {'Metadata': 'true'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            json_response = response.json()
            access_token = json_response.get('access_token')
            
            if not access_token:
                raise LazzyConnectionError("Access token not found in Azure response")
                
            return access_token
            
        except requests.RequestException as e:
            connector_logger.error(f"Failed to retrieve Azure token: {e}")
            raise LazzyConnectionError(f"Failed to retrieve Azure authentication token: {e}")

    def get_connection_pool(self) -> Optional[pooling.MySQLConnectionPool]:
        """
        Creates or returns existing connection pool for efficient reusability of MySQL connections.

        Returns:
            pooling.MySQLConnectionPool: A connection pool object
            
        Raises:
            LazzyConnectionError: If pool creation fails
        """
        # Return existing pool if available
        if self._connection_pool is not None:
            return self._connection_pool
            
        if self.is_azure_server:
            # Handle Azure-specific authentication using a token
            try:
                self.password = self._get_azure_token()
            except LazzyConnectionError as e:
                connector_logger.error(f"Azure authentication failed: {e}")
                raise

        try:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name=self.pool_name,
                pool_size=self.pool_size,
                auth_plugin='mysql_native_password',
                pool_reset_session=True,
                **self.get_connection_config()
            )
            connector_logger.info(f"Connection pool '{self.pool_name}' created successfully with size {self.pool_size}")
            return self._connection_pool
            
        except Error as e:
            connector_logger.error(f"Error creating connection pool: {e}")
            raise LazzyConnectionError(f"Failed to create connection pool: {e}")

    def create_connection(self):
        """Create a single database connection (not from pool).
        
        Returns:
            MySQL connection object or None
            
        Note:
            Prefer using get_connection_pool() for better connection management.
        """
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if connection.is_connected():
                db_info = connection.get_server_info()
                connector_logger.info(f"Connected to MySQL database '{self.database}' (Server version: {db_info})")
                return connection
            else:
                connector_logger.error("Connection failed - is_connected() returned False")
                return None
                
        except Error as e:
            connector_logger.error(f"Error connecting to database: {e}")
            raise LazzyConnectionError(f"Failed to connect to database: {e}")

    def test_connection(self) -> bool:
        """Test database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            connection = self.create_connection()
            if connection:
                connection.close()
                connector_logger.info("Connection test successful")
                return True
            return False
        except Exception as e:
            connector_logger.error(f"Connection test failed: {e}")
            return False

    def show_process_list(self):
        """
        Retrieves the list of running processes from the MySQL server.

        Returns:
            list: A list of process information
            
        Raises:
            LazzyConnectionError: If query fails
        """
        connection = None
        cursor = None
        try:
            pool = self.get_connection_pool()
            connection = pool.get_connection()
            cursor = connection.cursor()
            cursor.execute("SHOW FULL PROCESSLIST;")
            result = cursor.fetchall()
            connector_logger.info(f"Retrieved {len(result)} processes")
            return result
            
        except Error as e:
            connector_logger.error(f"Error retrieving process list: {e}")
            raise LazzyConnectionError(f"Failed to retrieve process list: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def close_pool(self):
        """Close all connections in the pool.
        
        Note: After calling this, you'll need to call get_connection_pool() again
        to create a new pool.
        """
        if self._connection_pool:
            try:
                # Close is not directly available, but we can set to None
                # The pool will be garbage collected
                self._connection_pool = None
                connector_logger.info(f"Connection pool '{self.pool_name}' closed")
            except Exception as e:
                connector_logger.error(f"Error closing connection pool: {e}")
                
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_pool()
