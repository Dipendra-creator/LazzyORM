"""
Custom exceptions for LazzyORM.

This module provides custom exception classes for better error handling
throughout the LazzyORM library.
"""


class LazzyORMError(Exception):
    """Base exception for all LazzyORM errors."""
    pass


class ConnectionError(LazzyORMError):
    """Raised when there's an error connecting to the database."""
    pass


class QueryError(LazzyORMError):
    """Raised when there's an error executing a query."""
    pass


class ValidationError(LazzyORMError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(LazzyORMError):
    """Raised when there's a configuration error."""
    pass


class DataMappingError(LazzyORMError):
    """Raised when there's an error mapping data to models."""
    pass


class PoolExhaustedError(LazzyORMError):
    """Raised when connection pool is exhausted."""
    pass
