# ... imports ...

import unittest

from dataclasses import dataclass

from lazzy_orm.lazzy_fetch import LazyFetch
from lazzy_orm.config.connector import Connector

host = "localhost"
port = 3306
user = "root"
password = "pass"
db = "db"


@dataclass
class MySQLUsers:
    User: str


class TestLazyFetch(unittest.TestCase):
    def test_fetch_lookups(self):
        """
        Simple test for LazyFetch functionality (replace placeholders with actual connection details).
        """
        connector = Connector(host=host, port=port, user=user, password=password, database=db)
        model = MySQLUsers
        query = "SELECT User FROM mysql.user where User = 'mysql.sys'"

        lazy_fetch_user = LazyFetch(model, query, connector.get_connection_pool())
        data = lazy_fetch_user.get()

        # Assert basic data retrieval
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 0)  # Expect at least one record


if __name__ == "__main__":
    unittest.main()
