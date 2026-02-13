"""
Unit tests for LazyQuery class.
"""
import pytest
from unittest.mock import Mock
from lazzy_orm.lazzy_query.lazzy_query import LazyQuery
from lazzy_orm.exceptions import ValidationError, QueryError
from tests.conftest import MockUser


def test_lazy_query_initialization(mock_connection_pool):
    """Test LazyQuery initialization."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    assert query.model == MockUser
    assert query._connection_pool == mock_connection_pool


def test_lazy_query_missing_connection_pool():
    """Test LazyQuery initialization without connection pool."""
    with pytest.raises(ValidationError):
        LazyQuery(model=MockUser, connection_pool=None)


def test_lazy_query_select_all(mock_connection_pool):
    """Test select_all method."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.select_all()
    assert result == query
    assert query._select_columns == ['*']


def test_lazy_query_select_specific_columns(mock_connection_pool):
    """Test select method with specific columns."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.select("id", "name")
    assert result == query
    assert query._select_columns == ["id", "name"]


def test_lazy_query_select_no_columns(mock_connection_pool):
    """Test select method without columns."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    with pytest.raises(ValidationError):
        query.select()


def test_lazy_query_where(mock_connection_pool):
    """Test where method."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.where("id", 1)
    assert result == query
    assert len(query._where_conditions) == 1
    assert len(query._where_params) == 1


def test_lazy_query_where_invalid_operator(mock_connection_pool):
    """Test where method with invalid operator."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    with pytest.raises(ValidationError):
        query.where("id", 1, "INVALID")


def test_lazy_query_where_invalid_column(mock_connection_pool):
    """Test where method with invalid column name."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    with pytest.raises(ValidationError):
        query.where("id; DROP TABLE users;", 1)


def test_lazy_query_where_in(mock_connection_pool):
    """Test where method with IN operator."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.where("id", [1, 2, 3], "IN")
    assert result == query
    assert len(query._where_params) == 3


def test_lazy_query_order_by(mock_connection_pool):
    """Test order_by method."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.order_by("name", "ASC")
    assert result == query
    assert len(query._order_by) == 1


def test_lazy_query_order_by_invalid_direction(mock_connection_pool):
    """Test order_by with invalid direction."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    with pytest.raises(ValidationError):
        query.order_by("name", "INVALID")


def test_lazy_query_limit(mock_connection_pool):
    """Test limit method."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.limit(10)
    assert result == query
    assert query._limit_value == 10


def test_lazy_query_limit_invalid(mock_connection_pool):
    """Test limit with invalid value."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    with pytest.raises(ValidationError):
        query.limit(-1)


def test_lazy_query_build_simple_query(mock_connection_pool):
    """Test building a simple SELECT query."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    query.select_all()
    sql = query._build_query()
    assert "SELECT * FROM MockUser" in sql


def test_lazy_query_build_query_with_where(mock_connection_pool):
    """Test building query with WHERE clause."""
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    query.select_all().where("id", 1)
    sql = query._build_query()
    assert "WHERE" in sql


def test_lazy_query_to_list(mock_connection_pool, sample_users):
    """Test to_list method."""
    # Setup mock to return sample data
    cursor = mock_connection_pool.get_connection().cursor()
    cursor.fetchall.return_value = [
        (1, "Alice", "alice@example.com", 25),
        (2, "Bob", "bob@example.com", 30),
    ]
    
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    results = query.select_all().to_list()
    
    assert len(results) == 2
    assert results[0].name == "Alice"
    assert results[1].name == "Bob"


def test_lazy_query_first(mock_connection_pool):
    """Test first method."""
    cursor = mock_connection_pool.get_connection().cursor()
    cursor.fetchall.return_value = [(1, "Alice", "alice@example.com", 25)]
    
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.select_all().first()
    
    assert result is not None
    assert result.name == "Alice"


def test_lazy_query_first_no_results(mock_connection_pool):
    """Test first method with no results."""
    cursor = mock_connection_pool.get_connection().cursor()
    cursor.fetchall.return_value = []
    
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    result = query.select_all().first()
    
    assert result is None


def test_lazy_query_count(mock_connection_pool):
    """Test count method."""
    cursor = mock_connection_pool.get_connection().cursor()
    cursor.fetchone.return_value = (5,)
    
    query = LazyQuery(model=MockUser, connection_pool=mock_connection_pool)
    count = query.count()
    
    assert count == 5
