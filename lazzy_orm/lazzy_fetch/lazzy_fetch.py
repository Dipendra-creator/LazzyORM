import logging
from typing import TypeVar, Generic, List, Optional
from lazzy_orm.logger.logger import Logger
from lazzy_orm.exceptions import QueryError, ValidationError
from mysql.connector import pooling, Error

T = TypeVar('T')
lazy_fetch_logger = Logger(log_file="lazy_fetch.log", logger_name="lazy_fetch_logger", level=logging.INFO).logger


def fetch_lookups(connection, model, query, params=None):
    """Fetch data from database and map to model instances.
    
    Args:
        connection: Database connection
        model: Data model class
        query: SQL query string
        params: Query parameters for parameterized queries
        
    Returns:
        List of model instances
    """
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()
        lookups = [model(*row) for row in data]
        return lookups
    except Error as e:
        lazy_fetch_logger.error(f"Query execution failed: {e}")
        raise QueryError(f"Failed to fetch data: {e}")
    except TypeError as e:
        lazy_fetch_logger.error(f"Failed to map data to model: {e}")
        raise QueryError(f"Failed to map query results to model {model.__name__}: {e}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                lazy_fetch_logger.warning(f"Error closing cursor: {e}")


class LazyFetch(Generic[T]):
    """
    A class to lazily fetch an object with caching support.
    Model the data into a class to make it more readable and maintainable.

    Example:
    ```python
    from dataclasses import dataclass
    
    @dataclass
    class TransactionsTypeLookup:
        id: int
        type_name: str
    
    # Fetch with caching
    lookups = LazyFetch(
        model=TransactionsTypeLookup,
        query="SELECT * FROM transactions_type_lookup",
        connection_pool=connection_pool
    ).get()
    
    # Fetch without caching
    lookups = LazyFetch(
        model=TransactionsTypeLookup,
        query="SELECT * FROM transactions_type_lookup WHERE id = %s",
        connection_pool=connection_pool,
        params=(1,),
        use_cache=False
    ).get()
    ```
    """
    _global_lookups = {}  # Global dictionary to store fetched data

    def __init__(
        self, 
        model, 
        query: str, 
        connection_pool: Optional[pooling.MySQLConnectionPool] = None,
        params: Optional[tuple] = None,
        use_cache: bool = True
    ):
        """Initialize LazyFetch instance.
        
        Args:
            model: Data model class to map results to
            query: SQL query string
            connection_pool: MySQL connection pool
            params: Query parameters for parameterized queries
            use_cache: Whether to use caching for this query
        """
        if connection_pool is None:
            raise ValidationError("Connection pool is required")
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string")
            
        self.model = model
        self.query = query
        self.params = params
        self.use_cache = use_cache
        self._key = f"{model.__name__}_{query}_{params}"  # Unique key for each fetch
        self._connection_pool = connection_pool
        self._connection = None

    def get(self) -> List[T]:
        """Fetch data from database with optional caching.
        
        Returns:
            List of model instances
        """
        # Return cached data if available and caching is enabled
        if self.use_cache and self._key in LazyFetch._global_lookups:
            cached_data = LazyFetch._global_lookups[self._key]
            lazy_fetch_logger.info(
                f"Returning cached {self.model.__name__} ({len(cached_data)} rows)")
            return cached_data
        
        # Fetch fresh data
        try:
            self._connection = self._connection_pool.get_connection()
            data = fetch_lookups(self._connection, self.model, self.query, self.params)
            
            # Cache the data if caching is enabled
            if self.use_cache:
                LazyFetch._global_lookups[self._key] = data
            
            lazy_fetch_logger.info(
                f"Fetched {self.model.__name__} from database: {len(data)} rows")
            return data
            
        except Error as e:
            lazy_fetch_logger.error(f"Failed to get connection from pool: {e}")
            raise QueryError(f"Failed to get connection: {e}")
        finally:
            if self._connection:
                try:
                    self._connection.close()
                except Exception as e:
                    lazy_fetch_logger.warning(f"Error closing connection: {e}")
                finally:
                    self._connection = None

    @classmethod
    def clear_cache(cls, model_name: Optional[str] = None):
        """Clear cached data.
        
        Args:
            model_name: If provided, clear cache only for this model.
                       If None, clear all cache.
        """
        if model_name:
            keys_to_remove = [key for key in cls._global_lookups if key.startswith(f"{model_name}_")]
            for key in keys_to_remove:
                del cls._global_lookups[key]
            lazy_fetch_logger.info(f"Cleared cache for model: {model_name}")
        else:
            cls._global_lookups.clear()
            lazy_fetch_logger.info("Cleared all cache")
