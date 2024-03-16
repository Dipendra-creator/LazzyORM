import logging
from typing import TypeVar, Generic
from lazzy_orm.logger.logger import Logger
from mysql.connector import pooling

T = TypeVar('T')
lazy_fetch_logger = Logger(log_file="lazy_fetch.log", logger_name="lazy_fetch_logger", level=logging.INFO).logger


def fetch_lookups(connection, model, query):
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    lookups = [model(*row) for row in data]
    return lookups


class LazyFetch(Generic[T]):
    """
        A class to lazily fetch an object.
        Model the data into a class to make it more readable and maintainable.

        Example:
        ``` select * from transactions_type_lookup ```

        Model the data into a class:
        ```TransactionsTypeLookup```

        Then, use the class to fetch the data into List.

        function_name: fetch_lookups returns a list of lookups.

        first argument: connection
        second argument: model
        third argument: query

    """
    _global_lookups = {}  # Global dictionary to store fetched data

    def __init__(self, model, query, _connection_pool: pooling.MySQLConnectionPool or None):
        self.model = model
        self.query = query
        self._key = f"{model.__name__}_{query}"  # Unique key for each fetch
        self._connection_pool = _connection_pool
        self._connection = self._connection_pool.get_connection()

    def get(self):
        if self._key not in LazyFetch._global_lookups:
            LazyFetch._global_lookups[self._key] = fetch_lookups(
                self._connection, self.model, self.query
            )
        lazy_fetch_logger.info(
            f"Fetching {self.model.__name__} from database got {len(LazyFetch._global_lookups[self._key])} rows.")
        return LazyFetch._global_lookups[self._key]
