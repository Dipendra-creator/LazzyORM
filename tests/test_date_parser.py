"""
Unit tests for date parser.
"""
import pytest
from datetime import date
from lazzy_orm.config.date_parser import parse_date


def test_parse_date_with_hyphen_dmy():
    """Test parsing date in DD-MM-YYYY format."""
    result = parse_date("15-01-2023")
    assert result == date(2023, 1, 15)


def test_parse_date_with_slash_mdy():
    """Test parsing date in MM/DD/YYYY format."""
    result = parse_date("01/15/2023")
    assert result == date(2023, 1, 15)


def test_parse_date_iso_format():
    """Test parsing date in ISO format YYYY-MM-DD."""
    result = parse_date("2023-01-15")
    assert result == date(2023, 1, 15)


def test_parse_date_with_month_name():
    """Test parsing date with month name."""
    result = parse_date("Jan 15, 2023")
    assert result == date(2023, 1, 15)


def test_parse_date_compact():
    """Test parsing compact date format YYYYMMDD."""
    result = parse_date("20230115")
    assert result == date(2023, 1, 15)


def test_parse_date_invalid():
    """Test parsing invalid date format."""
    with pytest.raises(ValueError):
        parse_date("invalid-date")


def test_parse_date_whitespace():
    """Test parsing date with leading/trailing whitespace."""
    result = parse_date("  2023-01-15  ")
    assert result == date(2023, 1, 15)
