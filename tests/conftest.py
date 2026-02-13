"""
Shared test fixtures and configuration for pytest.
"""
import pytest
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass


@dataclass
class MockUser:
    """Mock user model for testing."""
    id: int
    name: str
    email: str
    age: int


@dataclass
class MockProduct:
    """Mock product model for testing."""
    id: int
    name: str
    price: float


@pytest.fixture
def mock_connection_pool():
    """Create a mock connection pool."""
    pool = Mock()
    connection = Mock()
    cursor = Mock()
    
    # Setup cursor behavior
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.close.return_value = None
    cursor.rowcount = 0
    
    # Setup connection behavior
    connection.cursor.return_value = cursor
    connection.commit.return_value = None
    connection.rollback.return_value = None
    connection.close.return_value = None
    connection.is_connected.return_value = True
    
    # Setup pool behavior
    pool.get_connection.return_value = connection
    
    return pool


@pytest.fixture
def sample_users():
    """Create sample user data."""
    return [
        MockUser(1, "Alice", "alice@example.com", 25),
        MockUser(2, "Bob", "bob@example.com", 30),
        MockUser(3, "Charlie", "charlie@example.com", 35),
    ]


@pytest.fixture
def sample_products():
    """Create sample product data."""
    return [
        MockProduct(1, "Laptop", 999.99),
        MockProduct(2, "Mouse", 29.99),
        MockProduct(3, "Keyboard", 79.99),
    ]
