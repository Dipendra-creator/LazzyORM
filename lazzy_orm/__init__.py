"""
LazzyORM - A Powerful Lazy Loading ORM for MySQL

LazzyORM is a Python library designed to simplify database interactions with MySQL.
It provides a clean and efficient way to work with your data by leveraging lazy loading techniques.
"""

__version__ = "0.3.0"
__author__ = "Dipendra Bhardwaj"
__email__ = "dipu.sharma.1122@gmail.com"

from lazzy_orm.config.connector import Connector
from lazzy_orm.config.date_parser import parse_date
from lazzy_orm.lazzy_fetch import LazyFetch
from lazzy_orm.lazzy_insert import LazyInsert
from lazzy_orm.lazzy_query.lazzy_query import LazyQuery
from lazzy_orm.lazzy_update import LazyUpdate
from lazzy_orm.lazzy_delete import LazyDelete
from lazzy_orm.logger import Logger
from lazzy_orm.exceptions import (
    LazzyORMError,
    ConnectionError,
    QueryError,
    ValidationError,
    ConfigurationError,
    DataMappingError,
    PoolExhaustedError
)

__all__ = [
    # Core classes
    'Connector',
    'LazyFetch',
    'LazyInsert',
    'LazyQuery',
    'LazyUpdate',
    'LazyDelete',
    'Logger',
    
    # Utilities
    'parse_date',
    
    # Exceptions
    'LazzyORMError',
    'ConnectionError',
    'QueryError',
    'ValidationError',
    'ConfigurationError',
    'DataMappingError',
    'PoolExhaustedError',
]

