import logging
from typing import TypeVar, Generic, List, Optional
import os

import pandas as pd
from mysql.connector import pooling, Error

from lazzy_orm.logger.logger import Logger
from lazzy_orm.exceptions import QueryError, ValidationError

T = TypeVar('T')
lazy_insert_logger = Logger(log_file="lazy_insert.log", logger_name="lazy_insert_logger", level=logging.INFO).logger


class LazyInsert(Generic[T]):
    """
        A class for lazily inserting data from a CSV file into a MySQL database table.

        Example:
        ```python
        lazy_insert = LazyInsert(
            table_name="my_table",
            path_to_csv="data.csv",
            _connection_pool=connection_pool,
            auto_increment=True,
            drop_if_exists=True,
            create_if_not_exists=True,
            log_create_table_query=True,
            log_insert_query=True,
            chunk_size=1000
        )
        lazy_insert.perform_staging_insert()
        ```

        Attributes:
        - table_name (str): The name of the table in the database.
        - path_to_csv (str): The file path to the CSV file containing data.
        - _connection_pool (pooling.MySQLConnectionPool or None): The connection pool to the MySQL database.
        - auto_increment (bool): Flag indicating whether to use auto-increment for primary key (default: False).
        - drop_if_exists (bool): Flag indicating whether to drop table if it already exists (default: False).
        - create_if_not_exists (bool): Flag indicating whether to create table if it doesn't exist (default: True).
        - log_create_table_query (bool): Flag indicating whether to log create table query execution (default: False).
        - log_insert_query (bool): Flag indicating whether to log insert query execution (default: False).
        - chunk_size (int): Size of data chunks to be inserted at once (default: 1000).
    """

    def __init__(
            self,
            table_name: str,
            connection_pool: Optional[pooling.MySQLConnectionPool] = None,
            path_to_csv: Optional[str] = None,
            auto_increment: bool = False,
            drop_if_exists: bool = False,
            create_if_not_exists: bool = True,
            log_create_table_query: bool = False,
            log_insert_query: bool = False,
            chunk_size: int = 1000,
            data: Optional[List[T]] = None,
            query: Optional[str] = None
    ):
        """Initialize LazyInsert instance.
        
        Args:
            table_name: The name of the table in the database
            connection_pool: MySQL connection pool (required)
            path_to_csv: File path to the CSV file containing data
            auto_increment: Whether to use auto-increment for primary key
            drop_if_exists: Whether to drop table if it already exists
            create_if_not_exists: Whether to create table if it doesn't exist
            log_create_table_query: Whether to log create table query execution
            log_insert_query: Whether to log insert query execution
            chunk_size: Size of data chunks to be inserted at once
            data: List of data objects to insert
            query: SQL query for inserting data
            
        Raises:
            ValidationError: If required parameters are missing or invalid
        """
        # Validate required parameters
        if not table_name or not isinstance(table_name, str):
            raise ValidationError("Table name is required and must be a string")
        if connection_pool is None:
            raise ValidationError("Connection pool is required")
        if chunk_size <= 0:
            raise ValidationError("Chunk size must be positive")
        
        # Validate table name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValidationError(f"Invalid table name: {table_name}. Use only alphanumeric characters and underscores")
            
        self.table_name = table_name
        self.path_to_csv = path_to_csv
        self._connection_pool = connection_pool
        self._connection = None
        self.auto_increment = auto_increment
        self.drop_if_exists = drop_if_exists
        self.create_if_not_exists = create_if_not_exists
        self.log_create_table_query = log_create_table_query
        self.log_insert_query = log_insert_query
        self.chunk_size = chunk_size
        self.data = data
        self.query = query

    def extract_row(self, data: List[T]) -> tuple:
        """
        Extracts a row model from the data.

        where T is the type of the data to be extracted.

        @dataclass
        class Model:
            name: str
            age: int

        Parameters:
        - data: The data to be extracted.

        Returns:
        - The row model extracted from the data in the form of a tuple.
        """
        try:
            return tuple(tuple(getattr(row, field.name) for field in row.__dataclass_fields__.values()) for row in data)
        except Exception as e:
            lazy_insert_logger.error(f"Error while extracting row: {e}")
            raise e

    def insert(self) -> int:
        """
        Inserts data into the table in the database.

        Returns:
            The number of rows inserted into the table
            
        Raises:
            ValidationError: If data or query is missing
            QueryError: If insert operation fails
        """
        if not self.data:
            raise ValidationError("Data is required for insert operation")
        if not self.query:
            raise ValidationError("Query is required for insert operation")
        
        cursor = None
        try:
            self._connection = self._connection_pool.get_connection()
            cursor = self._connection.cursor()
            data_inserted = 0
            
            for i in range(0, len(self.data), self.chunk_size):
                chunk = self.data[i:i + self.chunk_size]
                values = self.extract_row(chunk)

                if self.log_insert_query:
                    lazy_insert_logger.info(f"Executing query: {self.query} with {len(values)} rows")
                    
                data_inserted += len(values)
                cursor.executemany(self.query, values)
                self._connection.commit()
                
            lazy_insert_logger.info(f"{data_inserted} rows inserted successfully into table {self.table_name}")
            return data_inserted
            
        except Error as e:
            if self._connection:
                self._connection.rollback()
            lazy_insert_logger.error(f"Error while inserting data: {e}")
            raise QueryError(f"Failed to insert data into {self.table_name}: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._connection:
                self._connection.close()
                self._connection = None

    def create_table(self, cursor, columns):
        """
        Creates a table in the database if it does not already exist.

        Parameters:
        - cursor: The cursor object used to execute SQL queries.
        - columns: A string representing the column definitions for the table.
        """
        # create table
        lazy_insert_logger.info(f"Table {self.table_name} does not exist in the database.")

        # create table if it does not exist
        lazy_insert_logger.info(f"Creating table {self.table_name} in the database.")

        if self.auto_increment:
            columns = f"{self.table_name}_id INT AUTO_INCREMENT PRIMARY KEY, {columns}"

        create_table_query = f"CREATE TABLE {self.table_name} ({columns})"

        if self.log_create_table_query:
            lazy_insert_logger.info(f"Executing query: {create_table_query}")

        cursor.execute(create_table_query)
        self._connection.commit()
        lazy_insert_logger.info(f"Table {self.table_name} created successfully.")

    def insert_data(self, cursor, df) -> int:
        """
        Inserts data from a DataFrame into the table in the database.

        Parameters:
        - cursor: The cursor object used to execute SQL queries.
        - df: A pandas DataFrame containing the data to be inserted.
        
        Returns:
            Number of rows inserted
        """
        lazy_insert_logger.info(f"Inserting {len(df)} rows into table {self.table_name}")

        # Prepare column names
        column_names = ', '.join([str(column).replace(' ', '_').lower() for column in df.columns])
        placeholders = ', '.join(['%s' for _ in df.columns])
        insert_query = f"INSERT INTO {self.table_name} ({column_names}) VALUES ({placeholders})"
        
        total_inserted = 0
        
        # Bulk insert data into the table in chunks
        for i in range(0, df.shape[0], self.chunk_size):
            chunk = df.iloc[i:i + self.chunk_size]
            values = [tuple(row) for row in chunk.values]

            if self.log_insert_query:
                lazy_insert_logger.info(f"Executing query: {insert_query} with {len(values)} rows")

            cursor.executemany(insert_query, values)
            total_inserted += len(values)

        self._connection.commit()
        lazy_insert_logger.info(f"{total_inserted} rows inserted successfully into table {self.table_name}")
        return total_inserted

    def perform_staging_insert(self) -> int:
        """
        Performs the staging insert operation by reading the CSV file,
        creating or dropping the table as required, and inserting data into the table.
        
        Returns:
            Number of rows inserted
            
        Raises:
            ValidationError: If CSV path is not provided or file doesn't exist
            QueryError: If database operations fail
        """
        if not self.path_to_csv:
            raise ValidationError("CSV file path is required for staging insert")
        
        if not os.path.exists(self.path_to_csv):
            raise ValidationError(f"CSV file not found: {self.path_to_csv}")
        
        cursor = None
        try:
            # Read CSV file
            try:
                df = pd.read_csv(self.path_to_csv)
            except Exception as e:
                lazy_insert_logger.error(f"Error reading CSV file: {e}")
                raise ValidationError(f"Failed to read CSV file: {e}")
            
            if df.empty:
                lazy_insert_logger.warning("CSV file is empty, no data to insert")
                return 0
            
            self._connection = self._connection_pool.get_connection()
            cursor = self._connection.cursor()
            
            # Sanitize column names
            columns = ', '.join([f'{str(column).replace(" ", "_").lower()} TEXT' for column in df.columns])

            # Check if table exists in database
            cursor.execute(f"SHOW TABLES LIKE %s", (self.table_name,))
            result = cursor.fetchone()
            
            if result:
                lazy_insert_logger.info(f"Table {self.table_name} exists in the database")

                if self.drop_if_exists:
                    lazy_insert_logger.info(f"Dropping table {self.table_name} from the database")
                    cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
                    self._connection.commit()
                    lazy_insert_logger.info(f"Table {self.table_name} dropped successfully")
                    self.create_table(cursor, columns)
                else:
                    lazy_insert_logger.info(f"Using existing table {self.table_name}")
            else:
                if self.create_if_not_exists:
                    self.create_table(cursor, columns)
                else:
                    raise QueryError(f"Table {self.table_name} does not exist and create_if_not_exists is False")

            # Insert data into the table
            rows_inserted = self.insert_data(cursor, df)
            return rows_inserted
            
        except pd.errors.EmptyDataError:
            lazy_insert_logger.error("CSV file is empty")
            raise ValidationError("CSV file is empty")
        except Error as e:
            if self._connection:
                self._connection.rollback()
            lazy_insert_logger.error(f"Error during staging insert: {e}")
            raise QueryError(f"Failed to perform staging insert: {e}")
        finally:
            if cursor:
                cursor.close()
            if self._connection:
                self._connection.close()
                self._connection = None
