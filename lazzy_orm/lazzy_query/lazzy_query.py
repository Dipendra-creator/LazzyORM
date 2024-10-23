from typing import TypeVar, Generic, List

from mysql.connector import pooling
from lazzy_orm.logger.logger import Logger

T = TypeVar('T')

lazy_fetch_logger = Logger(log_file="lazy_fetch.log", logger_name="lazy_fetch_logger").logger

class LazyQuery(Generic[T]):
    """
    A class for creating mysql queries to fetch data from a table.

    Example:
    ```sql
    SELECT * FROM my_table
    ```

    ```python
    LazyQuery<MyTable>(connection_pool=connection_pool).select_all()
    ```

    ```sql
    SELECT * FROM my_table WHERE id = 1
    ```

    ```python
    LazyQuery<MyTable>(connection_pool=connection_pool).where("id", 1).select_all()
    ```

    ```sql
    SELECT departmentId FROM my_table WHERE id = 1 AND name = 'Dipendra'
    ```

    ```python
    LazyQuery<MyTable>(connection_pool=connection_pool).where("id", 1).where("name", "Dipendra").select("departmentId")
    ```
    """

    def __init__(self, model, _connection_pool: pooling.MySQLConnectionPool or None):
        self.model = model
        self._connection_pool = _connection_pool
        self._connection = self._connection_pool.get_connection()
        self._cursor = self._connection.cursor()
        self._query = None
        self._where = None
        self._select = None

    def select_all(self):
        self._query = f"SELECT * FROM {self.model.__name__}"
        return self

    def where(self, column, value):
        if self._where is None:
            self._where = f" WHERE {column} = '{value}'"
        else:
            self._where += f" AND {column} = '{value}'"
        return self

    def select(self, column):
        self._select = f"SELECT {column} FROM {self.model.__name__}"
        return self

    def to_list(self):
        if self._query is not None:
            self._cursor.execute(self._query)
            data = self._cursor.fetchall()
            lookups = [self.model(*row) for row in data]
            return lookups
        elif self._where is not None:
            self._cursor.execute(self._select + self._where)
            data = self._cursor.fetchall()
            lookups = [self.model(*row) for row in data]
            return lookups
        elif self._select is not None:
            self._cursor.execute(self._select)
            data = self._cursor.fetchall()
            lookups = [self.model(*row) for row in data]
            return lookups
        else:
            raise Exception("Query not found")

    def __exit__(self, exc_type, exc_value, traceback):
        self._cursor.close()
        self._connection.close()
        lazy_fetch_logger.info(f"Connection closed for {self.model.__name__}")


