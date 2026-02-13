from typing import TypeVar, Generic, List, Any, Optional, Union
import logging

from mysql.connector import pooling, Error
from lazzy_orm.logger.logger import Logger
from lazzy_orm.exceptions import QueryError, ValidationError

T = TypeVar('T')

lazy_query_logger = Logger(log_file="lazy_query.log", logger_name="lazy_query_logger", level=logging.INFO).logger


class LazyQuery(Generic[T]):
    """
    A class for creating mysql queries to fetch data from a table.

    Example:
    ```sql
    SELECT * FROM my_table
    ```

    ```python
    LazyQuery(model=MyTable, connection_pool=connection_pool).select_all().to_list()
    ```

    ```sql
    SELECT * FROM my_table WHERE id = 1
    ```

    ```python
    LazyQuery(model=MyTable, connection_pool=connection_pool).where("id", 1).select_all().to_list()
    ```

    ```sql
    SELECT departmentId FROM my_table WHERE id = 1 AND name = 'Dipendra'
    ```

    ```python
    LazyQuery(model=MyTable, connection_pool=connection_pool).where("id", 1).where("name", "Dipendra").select("departmentId").to_list()
    ```
    """

    def __init__(self, model, connection_pool: Optional[pooling.MySQLConnectionPool] = None, table_name: Optional[str] = None):
        if connection_pool is None:
            raise ValidationError("Connection pool is required")
        
        self.model = model
        self._connection_pool = connection_pool
        self._connection = None
        self._cursor = None
        self._query_parts = []
        self._where_conditions = []
        self._where_params = []
        self._select_columns = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._table_name = table_name or model.__name__

    def _ensure_connection(self):
        """Ensures a database connection is available."""
        if self._connection is None:
            try:
                self._connection = self._connection_pool.get_connection()
                self._cursor = self._connection.cursor()
            except Error as e:
                lazy_query_logger.error(f"Failed to get connection from pool: {e}")
                raise QueryError(f"Failed to get connection: {e}")

    def select_all(self):
        """Select all columns from the table."""
        self._select_columns = ['*']
        return self

    def select(self, *columns: str):
        """Select specific columns from the table.
        
        Args:
            *columns: Column names to select
        """
        if not columns:
            raise ValidationError("At least one column must be specified")
        self._select_columns = list(columns)
        return self

    def where(self, column: str, value: Any, operator: str = '='):
        """Add a WHERE condition with parameterized query to prevent SQL injection.
        
        Args:
            column: Column name
            value: Value to compare
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE, IN)
        """
        allowed_operators = ['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN', 'NOT IN']
        if operator.upper() not in allowed_operators:
            raise ValidationError(f"Operator '{operator}' is not allowed. Use: {', '.join(allowed_operators)}")
        
        # Validate column name to prevent SQL injection
        if not column.replace('_', '').replace('.', '').isalnum():
            raise ValidationError(f"Invalid column name: {column}")
        
        if operator.upper() in ['IN', 'NOT IN']:
            if not isinstance(value, (list, tuple)):
                raise ValidationError(f"Value for {operator} must be a list or tuple")
            placeholders = ', '.join(['%s'] * len(value))
            self._where_conditions.append(f"{column} {operator.upper()} ({placeholders})")
            self._where_params.extend(value)
        else:
            self._where_conditions.append(f"{column} {operator} %s")
            self._where_params.append(value)
        
        return self

    def order_by(self, column: str, direction: str = 'ASC'):
        """Add ORDER BY clause.
        
        Args:
            column: Column name to sort by
            direction: Sort direction (ASC or DESC)
        """
        direction = direction.upper()
        if direction not in ['ASC', 'DESC']:
            raise ValidationError("Direction must be 'ASC' or 'DESC'")
        
        # Validate column name
        if not column.replace('_', '').replace('.', '').isalnum():
            raise ValidationError(f"Invalid column name: {column}")
        
        self._order_by.append(f"{column} {direction}")
        return self

    def limit(self, limit: int, offset: int = 0):
        """Add LIMIT clause.
        
        Args:
            limit: Maximum number of rows to return
            offset: Number of rows to skip
        """
        if not isinstance(limit, int) or limit < 0:
            raise ValidationError("Limit must be a non-negative integer")
        if not isinstance(offset, int) or offset < 0:
            raise ValidationError("Offset must be a non-negative integer")
        
        self._limit_value = limit
        self._offset_value = offset
        return self

    def _build_query(self) -> str:
        """Build the SQL query from all parts."""
        if not self._select_columns:
            self._select_columns = ['*']
        
        query = f"SELECT {', '.join(self._select_columns)} FROM {self._table_name}"
        
        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"
        
        if self._order_by:
            query += f" ORDER BY {', '.join(self._order_by)}"
        
        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"
            if self._offset_value:
                query += f" OFFSET {self._offset_value}"
        
        return query

    def to_list(self) -> List[T]:
        """Execute the query and return results as a list of model instances."""
        self._ensure_connection()
        
        try:
            query = self._build_query()
            lazy_query_logger.info(f"Executing query: {query} with params: {self._where_params}")
            
            self._cursor.execute(query, self._where_params or None)
            data = self._cursor.fetchall()
            
            if not data:
                return []
            
            # Map data to model instances
            try:
                lookups = [self.model(*row) for row in data]
            except TypeError as e:
                lazy_query_logger.error(f"Failed to map data to model: {e}")
                raise QueryError(f"Failed to map query results to model {self.model.__name__}: {e}")
            
            lazy_query_logger.info(f"Query returned {len(lookups)} rows")
            return lookups
            
        except Error as e:
            lazy_query_logger.error(f"Query execution failed: {e}")
            raise QueryError(f"Query execution failed: {e}")
        finally:
            self._cleanup()

    def first(self) -> Optional[T]:
        """Execute the query and return the first result."""
        self._limit_value = 1
        results = self.to_list()
        return results[0] if results else None

    def count(self) -> int:
        """Return the count of rows matching the query."""
        self._ensure_connection()
        
        try:
            # Build count query
            query = f"SELECT COUNT(*) FROM {self._table_name}"
            
            if self._where_conditions:
                query += f" WHERE {' AND '.join(self._where_conditions)}"
            
            lazy_query_logger.info(f"Executing count query: {query} with params: {self._where_params}")
            
            self._cursor.execute(query, self._where_params or None)
            result = self._cursor.fetchone()
            
            return result[0] if result else 0
            
        except Error as e:
            lazy_query_logger.error(f"Count query execution failed: {e}")
            raise QueryError(f"Count query execution failed: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up cursor and connection."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception as e:
                lazy_query_logger.warning(f"Error closing cursor: {e}")
            finally:
                self._cursor = None
        
        if self._connection:
            try:
                self._connection.close()
                lazy_query_logger.debug(f"Connection closed for {self.model.__name__}")
            except Exception as e:
                lazy_query_logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None

    def __enter__(self):
        """Context manager entry."""
        self._ensure_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self._cleanup()


