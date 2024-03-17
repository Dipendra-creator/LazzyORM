import logging
from typing import TypeVar, Generic, List

import pandas as pd
from mysql.connector import pooling

from lazzy_orm.logger.logger import Logger

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
            _connection_pool: pooling.MySQLConnectionPool or None,
            path_to_csv: str = None,
            auto_increment: bool = False,
            drop_if_exists: bool = False,
            create_if_not_exists: bool = True,
            log_create_table_query: bool = False,
            log_insert_query: bool = False,
            chunk_size: int = 1000,
            data: List[T] = None,
            query: str = None
    ):
        self.table_name = table_name
        self.path_to_csv = path_to_csv
        self._connection_pool = _connection_pool
        self._connection = self._connection_pool.get_connection()
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

    def insert(
            self
    ) -> int:
        """
        Inserts data into the table in the database.

        where T is the type of the data to be inserted.

        @dataclass
        class Model:
            name: str
            age: int

        Parameters:
        - model: The structure of the data to be inserted.
        - data: The data to be inserted into the table.
        - query: The SQL query to be executed.
        - _connection_pool: The connection pool to the MySQL database.

        Returns:
        - The number of rows inserted into the table.
        """
        try:
            cursor = self._connection.cursor()
            data_inserted = 0
            for i in range(0, len(self.data), self.chunk_size):
                chunk = self.data[i:i + self.chunk_size]
                values = self.extract_row(chunk)

                if self.log_insert_query:
                    lazy_insert_logger.info(f"Executing query: {self.query} with values: {len(values)}")
                data_inserted += len(values)
                cursor.executemany(self.query, values)
                self._connection.commit()
            lazy_insert_logger.info(f"Data inserted successfully into table {self.table_name}.")
            cursor.close()
            return data_inserted
        except Exception as e:
            lazy_insert_logger.error(f"Error while inserting data: {e}")
            raise e

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

    def insert_data(self, cursor, df):
        """
        Inserts data from a DataFrame into the table in the database.

        Parameters:
        - cursor: The cursor object used to execute SQL queries.
        - df: A pandas DataFrame containing the data to be inserted.
        """
        # insert data into the table
        lazy_insert_logger.info(f"Inserting data into table {self.table_name}.")

        # bulk insert data into the table
        for i in range(0, df.shape[0], self.chunk_size):
            chunk = df.iloc[i:i + self.chunk_size]
            insert_query = f"INSERT INTO {self.table_name} ({', '.join([str(column).replace(' ', '_').lower() for column in df.columns])}) VALUES ({', '.join(['%s' for _ in df.columns])})"
            values = [tuple(row) for row in chunk.values]

            if self.log_insert_query:
                lazy_insert_logger.info(f"Executing query: {insert_query} with values: {values}")

            cursor.executemany(insert_query, values)

        self._connection.commit()
        lazy_insert_logger.info(f"Data inserted successfully into table {self.table_name}.")

    def perform_staging_insert(self):
        """
        Performs the staging insert operation by reading the CSV file, creating or dropping the table as required, and inserting data into the table.
        """
        try:
            df = pd.read_csv(self.path_to_csv)
            cursor = self._connection.cursor()
            columns = ', '.join([f'{str(column).replace(" ", "_").lower()} TEXT' for column in df.columns])

            # check if table exists in database
            cursor.execute(f"SHOW TABLES LIKE '{self.table_name}'")
            result = cursor.fetchone()
            if result:
                lazy_insert_logger.info(f"Table {self.table_name} exists in the database.")

                if self.drop_if_exists:
                    lazy_insert_logger.info(f"Dropping table {self.table_name} from the database.")
                    cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
                    self._connection.commit()
                    lazy_insert_logger.info(f"Table {self.table_name} dropped successfully.")

                    # create table
                    self.create_table(cursor, columns)

            else:
                if self.create_if_not_exists:
                    self.create_table(cursor, columns)

            # insert data into the table
            self.insert_data(cursor, df)

        except Exception as e:
            lazy_insert_logger.error(f"Error while reading csv file: {e}")
            raise e
