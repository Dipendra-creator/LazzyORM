"""
LazyDelete - Safe delete operations for MySQL databases.
"""
import logging
from typing import Any, Optional

from mysql.connector import pooling, Error

from lazzy_orm.logger.logger import Logger
from lazzy_orm.exceptions import QueryError, ValidationError

lazy_delete_logger = Logger(log_file="lazy_delete.log", logger_name="lazy_delete_logger", level=logging.INFO).logger


class LazyDelete:
    """
    A class for safely deleting records from MySQL database tables.

    Example:
    ```python
    from lazzy_orm.lazzy_delete import LazyDelete
    
    # Delete with WHERE conditions
    deleter = LazyDelete(
        table_name="users",
        connection_pool=connection_pool
    )
    
    rows_deleted = deleter.where("id", 1).execute()
    
    # Delete multiple records
    rows_deleted = deleter.where("status", "inactive").execute()
    
    # Delete with IN clause
    rows_deleted = deleter.where("id", [1, 2, 3], "IN").execute()
    ```
    """

    def __init__(self, table_name: str, connection_pool: Optional[pooling.MySQLConnectionPool] = None):
        """Initialize LazyDelete instance.
        
        Args:
            table_name: Name of the table to delete from
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
        self._where_conditions = []
        self._where_params = []
        self._limit_value = None

    def where(self, column: str, value: Any, operator: str = '='):
        """Add a WHERE condition.
        
        Args:
            column: Column name
            value: Value to compare
            operator: Comparison operator (=, !=, >, <, >=, <=, LIKE, IN, NOT IN)
            
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

    def limit(self, limit: int):
        """Add LIMIT clause to restrict number of deletions.
        
        Args:
            limit: Maximum number of rows to delete
            
        Returns:
            Self for method chaining
        """
        if not isinstance(limit, int) or limit < 0:
            raise ValidationError("Limit must be a non-negative integer")
        
        self._limit_value = limit
        return self

    def _build_query(self) -> tuple:
        """Build the DELETE SQL query.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        query = f"DELETE FROM {self.table_name}"
        params = []
        
        # Add WHERE clause
        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"
            params.extend(self._where_params)
        else:
            lazy_delete_logger.warning(f"DELETE on {self.table_name} without WHERE clause - this will delete ALL rows!")
        
        # Add LIMIT clause
        if self._limit_value is not None:
            query += f" LIMIT {self._limit_value}"
        
        return query, params

    def execute(self, confirm_delete_all: bool = False) -> int:
        """Execute the DELETE query.
        
        Args:
            confirm_delete_all: Must be True to delete all rows (no WHERE clause)
        
        Returns:
            Number of rows deleted
            
        Raises:
            ValidationError: If trying to delete all rows without confirmation
            QueryError: If delete fails
        """
        # Safety check: prevent accidental deletion of all rows
        if not self._where_conditions and not confirm_delete_all:
            raise ValidationError(
                "Cannot delete all rows without WHERE clause. "
                "Use confirm_delete_all=True to explicitly confirm this action."
            )
        
        try:
            self._connection = self._connection_pool.get_connection()
            self._cursor = self._connection.cursor()
            
            query, params = self._build_query()
            lazy_delete_logger.info(f"Executing delete: {query} with params: {params}")
            
            self._cursor.execute(query, params)
            self._connection.commit()
            
            rows_deleted = self._cursor.rowcount
            lazy_delete_logger.info(f"Delete successful: {rows_deleted} rows deleted")
            
            return rows_deleted
            
        except Error as e:
            if self._connection:
                self._connection.rollback()
            lazy_delete_logger.error(f"Delete failed: {e}")
            raise QueryError(f"Failed to delete from {self.table_name}: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up cursor and connection."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception as e:
                lazy_delete_logger.warning(f"Error closing cursor: {e}")
            finally:
                self._cursor = None
        
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                lazy_delete_logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit."""
        self._cleanup()
