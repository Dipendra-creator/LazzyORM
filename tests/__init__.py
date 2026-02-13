"""
Test runner script - ensures all tests can be discovered and run.
"""
import pytest
import sys


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "--cov=lazzy_orm", "--cov-report=html", "--cov-report=term"]))
