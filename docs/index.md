# LazzyORM: A Powerful Lazy Loading ORM for MySQL

[![PyPI - version](https://badge.fury.io/py/LazzyORM.svg)](https://pypi.org/project/LazzyORM/)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LazzyORM is a modern, secure, and efficient Python library designed to simplify database interactions with MySQL. It provides a clean, intuitive API for working with your data by leveraging lazy loading techniques, connection pooling, and comprehensive error handling.

## 🚀 Key Features

* **Lazy Loading**: Fetch data from the database only when it's actually needed, improving performance and reducing memory usage
* **SQL Injection Protection**: Parameterized queries throughout to prevent SQL injection attacks
* **Connection Pooling**: Efficient connection management for faster and more reliable database access
* **Comprehensive CRUD Operations**: Full support for Create, Read, Update, and Delete operations
* **Query Building**: Intuitive, chainable query builder with support for WHERE, ORDER BY, LIMIT, and more
* **Type Safety**: Full type hints for better IDE support and code quality
* **Error Handling**: Custom exceptions for better error tracking and debugging
* **Logging**: Comprehensive logging capabilities to monitor database interactions
* **CSV Import**: Bulk insert data from CSV files with automatic table creation
* **Context Managers**: Proper resource cleanup with context manager support

## 📦 Installation

Install LazzyORM using pip:

```bash
pip install LazzyORM
```

For development with testing tools:

```bash
pip install LazzyORM[dev]
```

For all dependencies including documentation tools:

```bash
pip install LazzyORM[all]
```

## 🔧 Quick Start

### Basic Setup

```python
from lazzy_orm import Connector, LazyFetch, Logger
from dataclasses import dataclass

# Setup logging
logger = Logger(log_file="app.log", logger_name="app_logger").logger

# Connect to the database
connector = Connector(
    host='localhost',
    user='root',
    password='your_password',
    database='testdb',
    port=3306
)

# Get connection pool
connection_pool = connector.get_connection_pool()

# Define your data models
@dataclass
class User:
    id: int
    name: str
    email: str
    age: int
```

### Fetching Data

```python
from lazzy_orm import LazyFetch

# Fetch all users
users = LazyFetch(
    model=User,
    query="SELECT * FROM users",
    connection_pool=connection_pool
).get()

logger.info(f"Found {len(users)} users")

# Fetch with parameters (prevents SQL injection)
active_users = LazyFetch(
    model=User,
    query="SELECT * FROM users WHERE status = %s",
    connection_pool=connection_pool,
    params=('active',)
).get()
```

### Query Building

```python
from lazzy_orm import LazyQuery

# Advanced querying
results = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .select_all()
    .where("age", 25, ">")
    .where("country", "USA")
    .order_by("name", "ASC")
    .limit(10, offset=0)
    .to_list()
)

# Get single result
user = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .select_all()
    .where("id", 1)
    .first()
)

# Count results
user_count = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .where("status", "active")
    .count()
)
```

### Inserting Data

```python
from lazzy_orm import LazyInsert

# Insert data from CSV
csv_file = "data/users.csv"
lazy_insert = LazyInsert(
    table_name="users",
    path_to_csv=csv_file,
    connection_pool=connection_pool,
    drop_if_exists=True,
    auto_increment=True,
    chunk_size=10000
)

rows_inserted = lazy_insert.perform_staging_insert()
logger.info(f"Inserted {rows_inserted} rows from CSV")
```

### Updating Data

```python
from lazzy_orm import LazyUpdate

# Update records
rows_updated = (
    LazyUpdate(table_name="users", connection_pool=connection_pool)
    .set({"name": "John Doe", "age": 30})
    .where("id", 1)
    .execute()
)
```

### Deleting Data

```python
from lazzy_orm import LazyDelete

# Delete records
rows_deleted = (
    LazyDelete(table_name="users", connection_pool=connection_pool)
    .where("status", "inactive")
    .execute()
)
```

## 🛡️ Security Features

### SQL Injection Prevention

LazzyORM uses parameterized queries throughout to prevent SQL injection attacks:

```python
# ✅ SAFE - Parameterized query
user = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .where("username", user_input)  # Automatically parameterized
    .first()
)
```

## 🔍 Error Handling

LazzyORM provides custom exceptions for better error handling:

```python
from lazzy_orm.exceptions import (
    LazzyORMError,
    ConnectionError,
    QueryError,
    ValidationError
)

try:
    users = LazyQuery(model=User, connection_pool=connection_pool).select_all().to_list()
except ConnectionError as e:
    logger.error(f"Database connection failed: {e}")
except QueryError as e:
    logger.error(f"Query execution failed: {e}")
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
```

## 📚 Documentation

- **Full Documentation**: [README.md](https://github.com/Dipendra-creator/LazzyORM#readme)
- **API Reference**: [API_REFERENCE.md](https://github.com/Dipendra-creator/LazzyORM/blob/main/API_REFERENCE.md)
- **Contributing Guide**: [CONTRIBUTING.md](https://github.com/Dipendra-creator/LazzyORM/blob/main/CONTRIBUTING.md)
- **Changelog**: [CHANGELOG.md](https://github.com/Dipendra-creator/LazzyORM/blob/main/CHANGELOG.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](https://github.com/Dipendra-creator/LazzyORM/blob/main/CONTRIBUTING.md) for details.

## 📝 License

LazzyORM is distributed under the MIT License. See [LICENSE](https://github.com/Dipendra-creator/LazzyORM/blob/main/LICENSE) for more information.

## 👤 Author

**Dipendra Bhardwaj**
- Email: dipu.sharma.1122@gmail.com
- GitHub: [@Dipendra-creator](https://github.com/Dipendra-creator)

## 🔗 Links

- [PyPI Package](https://pypi.org/project/LazzyORM/)
- [GitHub Repository](https://github.com/Dipendra-creator/LazzyORM)
- [Issue Tracker](https://github.com/Dipendra-creator/LazzyORM/issues)

## 📈 Changelog

### Version 0.3.0 (Latest)
- ✨ Added LazyUpdate and LazyDelete classes
- 🔒 Implemented SQL injection protection
- ✅ Added comprehensive input validation
- 🐛 Fixed connection leaks
- 📝 Added complete type hints
- 🧪 Added comprehensive test suite
- 📚 Improved documentation

See [CHANGELOG.md](https://github.com/Dipendra-creator/LazzyORM/blob/main/CHANGELOG.md) for complete version history.
```python
from lazzy_orm.config import Connector
from lazzy_orm.lazzy_insert.lazzy_insert import LazyInsert
import os

connector = Connector(
    host="localhost",
    user="root",
    database="testdb",
    port=3306,
    password="root"
)


if __name__ == '__main__':
    connection_pool = connector.get_connection_pool()
    current_dir = os.path.dirname(__file__)
    test_csv = os.path.join(current_dir, "test.csv")
    lazy_insert = LazyInsert(
        table_name="test_table",
        path_to_csv=test_csv,
        _connection_pool=connection_pool,
        drop_if_exists=True,
        auto_increment=True,
        chunk_size=10000
    )
    lazy_insert.perform_staging_insert()
```

## Documentation

For more details on how to use LazyORM, check out the [documentation](https://github.com/Dipendra-creator).

## Contributing

If you'd like to contribute to LazyORM, please read our [contributing guidelines]

## License

LazyORM is distributed under the [MIT License]
```python
# Path: setup.py
from setuptools import setup, find_packages

setup(
    name="LazzyORM",
    version="0.1.1",
    description="A Lazy Loading ORM for MySQL",
    author="Dipendra Bhardwaj",
    author_email="dipu.sharma.1122@gmail.com",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "mysql-connector-python",
        "requests",
        "click",
        "colorama",
    ],
)
```
