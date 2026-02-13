"""
Unit tests for LazzyORM exceptions.
"""
import pytest
from lazzy_orm.exceptions import (
    LazzyORMError,
    ConnectionError,
    QueryError,
    ValidationError,
    ConfigurationError,
    DataMappingError,
    PoolExhaustedError
)


def test_base_exception():
    """Test base LazzyORMError."""
    with pytest.raises(LazzyORMError):
        raise LazzyORMError("Base error")


def test_connection_error():
    """Test ConnectionError."""
    with pytest.raises(ConnectionError):
        raise ConnectionError("Connection failed")


def test_query_error():
    """Test QueryError."""
    with pytest.raises(QueryError):
        raise QueryError("Query failed")


def test_validation_error():
    """Test ValidationError."""
    with pytest.raises(ValidationError):
        raise ValidationError("Validation failed")


def test_configuration_error():
    """Test ConfigurationError."""
    with pytest.raises(ConfigurationError):
        raise ConfigurationError("Configuration invalid")


def test_data_mapping_error():
    """Test DataMappingError."""
    with pytest.raises(DataMappingError):
        raise DataMappingError("Mapping failed")


def test_pool_exhausted_error():
    """Test PoolExhaustedError."""
    with pytest.raises(PoolExhaustedError):
        raise PoolExhaustedError("Pool exhausted")


def test_exception_inheritance():
    """Test that all exceptions inherit from LazzyORMError."""
    assert issubclass(ConnectionError, LazzyORMError)
    assert issubclass(QueryError, LazzyORMError)
    assert issubclass(ValidationError, LazzyORMError)
    assert issubclass(ConfigurationError, LazzyORMError)
    assert issubclass(DataMappingError, LazzyORMError)
    assert issubclass(PoolExhaustedError, LazzyORMError)
