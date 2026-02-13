"""
LazyUpdate - Safe update operations for MySQL databases.
"""
import logging
from typing import Any, Dict, Optional

from mysql.connector import pooling, Error

from lazzy_orm.logger.logger import Logger
from lazzy_orm.exceptions import QueryError, ValidationError

lazy_update_logger = Logger(log_file="lazy_update.log", logger_name="lazy_update_logger", level=logging.INFO).logger


class LazyUpdate:
    """
    A class for safely updating records in MySQL database tables.

    Example:
    ```python
    from lazzy_orm.lazzy_update import LazyUpdate
    
    # Update with WHERE conditions
    updater = LazyUpdate(
        table_name="users",
        connection_pool=connection_pool
    )
    
    rows_affected = updater.set({"name": "John", "age": 30}).where("id", 1).execute()
    
    # Update multiple records
    rows_affected = updater.set({"status": "active"}).where("created_at", "2024-01-01", ">").execute()
    ```
    """

    def __init__(self, table_name: str, connection_pool: Optional[pooling.MySQLConnectionPool] = None):
        """Initialize LazyUpdate instance.
        
        Args:
            table_name: Name of the table to update
            connection_pool: MySQL connection pool (required)
            
        Raises:
            ValidationError: If required parameters are missing or invalid
        """
        if not table_name or not isinstance(table_name, str):
            raise ValidationError("Table name is required and must be a string")
        if connection_pool is None:
            raise ValidationError("Connection pool is required")
        
        # Validate table name to prevent SQL injection
        if not table_name.replace('_', '').isalnum():
            raise ValidationError(f"Invalid table name: {table_name}")
        
        self.table_name = table_name
        self._connection_pool = connection_pool
        self._connection = None
        self._cursor = None
        self._set_values = {}
        self._where_conditions = []
        self._where_params = []

    def set(self, values: Dict[str, Any]):
        """Set column values to update.
        
        Args:
            values: Dictionary of column names and their new values
            
        Returns:
            Self for method chaining
        """
        if not values or not isinstance(values, dict):
            raise ValidationError("Values must be a non-empty dictionary")
        
        # Validate column names
        for column in values.keys():
            if not column.replace('_', '').isalnum():
                raise ValidationError(f"Invalid column name: {column}")
        
        self._set_values.update(values)
        return self

    def where(self, column: str, value: Any, operator: str = '='):
        """Add a WHERE condition.
        
        Args:
            column: Column name
            value: Value to compare
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE)
            
        Returns:
            Self for method chaining
        """
        allowed_operators = ['=', '!=', '>', '<', '>=', '<=', 'LIKE', 'IN', 'NOT IN']
        if operator.upper() not in allowed_operators:
            raise ValidationError(f"Operator '{operator}' is not allowed")
        
        # Validate column name
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

    def _build_query(self) -> tuple:
        """Build the UPDATE SQL query.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        if not self._set_values:
            raise ValidationError("No values to update. Use set() method first")
        
        # Build SET clause
        set_clauses = [f"{col} = %s" for col in self._set_values.keys()]
        set_params = list(self._set_values.values())
        
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
        params = set_params
        
        # Add WHERE clause
        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"
            params.extend(self._where_params)
        else:
            lazy_update_logger.warning(f"UPDATE on {self.table_name} without WHERE clause - this will update ALL rows!")
        
        return query, params

    def execute(self) -> int:
        """Execute the UPDATE query.
        
        Returns:
            Number of rows affected
            
        Raises:
            QueryError: If update fails
        """
        try:
            self._connection = self._connection_pool.get_connection()
            self._cursor = self._connection.cursor()
            
            query, params = self._build_query()
            lazy_update_logger.info(f"Executing update: {query} with params: {params}")
            
            self._cursor.execute(query, params)
            self._connection.commit()
            
            rows_affected = self._cursor.rowcount
            lazy_update_logger.info(f"Update successful: {rows_affected} rows affected")
            
            return rows_affected
            
        except Error as e:
            if self._connection:
                self._connection.rollback()
            lazy_update_logger.error(f"Update failed: {e}")
            raise QueryError(f"Failed to update {self.table_name}: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up cursor and connection."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception as e:
                lazy_update_logger.warning(f"Error closing cursor: {e}")
            finally:
                self._cursor = None
        
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                lazy_update_logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self._cleanup()
