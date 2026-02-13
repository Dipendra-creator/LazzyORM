"""
Unit tests for Connector class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from lazzy_orm.config.connector import Connector
from lazzy_orm.exceptions import ConnectionError, ConfigurationError


def test_connector_initialization():
    """Test Connector initialization with valid parameters."""
    connector = Connector(
        host="localhost",
        user="root",
        password="password",
        database="testdb",
        port=3306
    )
    assert connector.host == "localhost"
    assert connector.user == "root"
    assert connector.database == "testdb"
    assert connector.port == 3306


def test_connector_missing_host():
    """Test Connector initialization with missing host."""
    with pytest.raises(ConfigurationError):
        Connector(host="", user="root", password="pass", database="testdb", port=3306)


def test_connector_missing_user():
    """Test Connector initialization with missing user."""
    with pytest.raises(ConfigurationError):
        Connector(host="localhost", user="", password="pass", database="testdb", port=3306)


def test_connector_missing_database():
    """Test Connector initialization with missing database."""
    with pytest.raises(ConfigurationError):
        Connector(host="localhost", user="root", password="pass", database="", port=3306)


def test_connector_invalid_port():
    """Test Connector initialization with invalid port."""
    with pytest.raises(ConfigurationError):
        Connector(host="localhost", user="root", password="pass", database="testdb", port=-1)


def test_connector_invalid_pool_size():
    """Test Connector initialization with invalid pool size."""
    with pytest.raises(ConfigurationError):
        Connector(
            host="localhost",
            user="root",
            password="pass",
            database="testdb",
            port=3306,
            pool_size=-1
        )


def test_get_connection_config():
    """Test get_connection_config method."""
    connector = Connector(
        host="localhost",
        user="root",
        password="password",
        database="testdb",
        port=3306
    )
    config = connector.get_connection_config()
    assert config['host'] == "localhost"
    assert config['user'] == "root"
    assert config['password'] == "password"
    assert config['database'] == "testdb"
    assert config['port'] == 3306


def test_context_manager():
    """Test Connector as context manager."""
    connector = Connector(
        host="localhost",
        user="root",
        password="password",
        database="testdb",
        port=3306
    )
    with connector as conn:
        assert conn is not None
