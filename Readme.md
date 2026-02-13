# LazzyORM: A Powerful Lazy Loading ORM for MySQL

[![PyPI - version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&ts=1683906897&type=6e&v=0.3.0&x2=0)](https://pypi.org/project/LazzyORM/)
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

### Fetching Data (LazyFetch)

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

# Disable caching for real-time data
fresh_data = LazyFetch(
    model=User,
    query="SELECT * FROM users WHERE id = %s",
    connection_pool=connection_pool,
    params=(1,),
    use_cache=False
).get()

# Clear cache when needed
LazyFetch.clear_cache()  # Clear all cache
LazyFetch.clear_cache('User')  # Clear cache for specific model
```

### Query Building (LazyQuery)

```python
from lazzy_orm import LazyQuery

# Simple query
users = LazyQuery(model=User, connection_pool=connection_pool).select_all().to_list()

# Query with WHERE conditions
admin_users = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .select_all()
    .where("role", "admin")
    .where("status", "active")
    .to_list()
)

# Select specific columns
user_names = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .select("id", "name", "email")
    .where("age", 18, ">=")
    .to_list()
)

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

# Using IN operator
users_in_cities = (
    LazyQuery(model=User, connection_pool=connection_pool)
    .select_all()
    .where("city", ["New York", "Los Angeles", "Chicago"], "IN")
    .to_list()
)

# Context manager for automatic cleanup
with LazyQuery(model=User, connection_pool=connection_pool) as query:
    users = query.select_all().where("status", "active").to_list()
```

### Inserting Data (LazyInsert)

#### From CSV File

```python
from lazzy_orm import LazyInsert
import os

# Insert data from CSV
csv_file = "data/users.csv"
lazy_insert = LazyInsert(
    table_name="users",
    path_to_csv=csv_file,
    connection_pool=connection_pool,
    drop_if_exists=True,  # Drop table if exists
    auto_increment=True,  # Add auto-increment ID
    chunk_size=10000,  # Insert in chunks
    log_create_table_query=True,
    log_insert_query=True
)

rows_inserted = lazy_insert.perform_staging_insert()
logger.info(f"Inserted {rows_inserted} rows from CSV")
```

#### From Data Objects

```python
from lazzy_orm import LazyInsert
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: int

# Prepare data
products = [
    Product(1, "Laptop", 999.99, 50),
    Product(2, "Mouse", 29.99, 200),
    Product(3, "Keyboard", 79.99, 150)
]

# Insert data
lazy_insert = LazyInsert(
    table_name="products",
    data=products,
    connection_pool=connection_pool,
    query="INSERT INTO products (id, name, price, stock) VALUES (%s, %s, %s, %s)"
)

rows_inserted = lazy_insert.insert()
logger.info(f"Inserted {rows_inserted} products")
```

### Updating Data (LazyUpdate)

```python
from lazzy_orm import LazyUpdate

# Update single record
rows_updated = (
    LazyUpdate(table_name="users", connection_pool=connection_pool)
    .set({"name": "John Doe", "age": 30})
    .where("id", 1)
    .execute()
)

# Update multiple records
rows_updated = (
    LazyUpdate(table_name="users", connection_pool=connection_pool)
    .set({"status": "inactive"})
    .where("last_login", "2023-01-01", "<")
    .execute()
)

# Update with multiple conditions
rows_updated = (
    LazyUpdate(table_name="products", connection_pool=connection_pool)
    .set({"price": 99.99, "discount": 10})
    .where("category", "electronics")
    .where("stock", 0, ">")
    .execute()
)

# Context manager
with LazyUpdate(table_name="users", connection_pool=connection_pool) as updater:
    rows = updater.set({"verified": True}).where("email_verified", True).execute()
```

### Deleting Data (LazyDelete)

```python
from lazzy_orm import LazyDelete

# Delete single record
rows_deleted = (
    LazyDelete(table_name="users", connection_pool=connection_pool)
    .where("id", 1)
    .execute()
)

# Delete multiple records
rows_deleted = (
    LazyDelete(table_name="users", connection_pool=connection_pool)
    .where("status", "inactive")
    .execute()
)

# Delete with limit
rows_deleted = (
    LazyDelete(table_name="logs", connection_pool=connection_pool)
    .where("created_at", "2023-01-01", "<")
    .limit(1000)
    .execute()
)

# Delete with IN operator
rows_deleted = (
    LazyDelete(table_name="users", connection_pool=connection_pool)
    .where("id", [1, 2, 3, 4, 5], "IN")
    .execute()
)

# Delete all records (requires confirmation)
rows_deleted = (
    LazyDelete(table_name="temp_data", connection_pool=connection_pool)
    .execute(confirm_delete_all=True)
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

# ✅ SAFE - With LazyFetch
users = LazyFetch(
    model=User,
    query="SELECT * FROM users WHERE status = %s",
    params=(status,),
    connection_pool=connection_pool
).get()
```

### Input Validation

All inputs are validated to prevent malicious data:

```python
# Invalid column names are rejected
try:
    query.where("id; DROP TABLE users;", 1)  # Raises ValidationError
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
```

## 🔍 Error Handling

LazzyORM provides custom exceptions for better error handling:

```python
from lazzy_orm.exceptions import (
    LazzyORMError,
    ConnectionError,
    QueryError,
    ValidationError,
    ConfigurationError
)

try:
    users = LazyQuery(model=User, connection_pool=connection_pool).select_all().to_list()
except ConnectionError as e:
    logger.error(f"Database connection failed: {e}")
except QueryError as e:
    logger.error(f"Query execution failed: {e}")
except ValidationError as e:
    logger.error(f"Invalid input: {e}")
except LazzyORMError as e:
    logger.error(f"LazzyORM error: {e}")
```

## 📊 Logging

LazzyORM includes comprehensive logging:

```python
from lazzy_orm import Logger
import logging

# Create custom logger
logger = Logger(
    log_file="myapp.log",
    logger_name="myapp_logger",
    level=logging.INFO,
    log_dir="logs"
).logger

# Use the logger
logger.info("Application started")
logger.debug("Debug information")
logger.error("Error occurred")
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install LazzyORM[dev]

# Run tests with coverage
pytest tests/ -v --cov=lazzy_orm --cov-report=html

# Run specific test file
pytest tests/test_lazy_query.py -v
```

## 📚 Advanced Usage

### Connection Pool Configuration

```python
connector = Connector(
    host='localhost',
    user='root',
    password='password',
    database='mydb',
    port=3306,
    pool_size=20,  # Custom pool size
    pool_name="MyApp_Pool"  # Custom pool name
)

# Test connection
if connector.test_connection():
    print("Connection successful!")

# Show running processes
processes = connector.show_process_list()

# Context manager
with Connector(host='localhost', user='root', password='pass', database='db', port=3306) as conn:
    pool = conn.get_connection_pool()
```

### Date Parsing Utility

```python
from lazzy_orm import parse_date
from datetime import date

# Parse various date formats
date1 = parse_date("2023-01-15")  # ISO format
date2 = parse_date("15-01-2023")  # DD-MM-YYYY
date3 = parse_date("Jan 15, 2023")  # Month name
date4 = parse_date("20230115")  # Compact format

assert all(isinstance(d, date) for d in [date1, date2, date3, date4])
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

LazzyORM is distributed under the MIT License. See `LICENSE` for more information.

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
- ✨ Added LazyUpdate and LazyDelete classes for complete CRUD operations
- 🔒 Implemented SQL injection protection with parameterized queries
- ✅ Added comprehensive input validation
- 🐛 Fixed connection leaks and resource management issues
- 📝 Added complete type hints throughout the codebase
- 🧪 Added comprehensive test suite with pytest
- 📚 Improved documentation with more examples
- ⚡ Enhanced query building with ORDER BY, LIMIT, and advanced operators
- 🎯 Added context manager support for all classes
- 📊 Improved logging and error handling
- 🔧 Added pyproject.toml for modern Python packaging

### Version 0.2.4
- Basic LazyFetch, LazyInsert, and LazyQuery functionality
- Connection pooling support
- CSV import capabilities

## 💡 Tips and Best Practices

1. **Always use connection pooling** for better performance
2. **Use context managers** to ensure proper resource cleanup
3. **Enable logging** in production for debugging
4. **Use parameterized queries** - LazzyORM does this automatically!
5. **Clear cache** when data is updated outside of LazzyORM
6. **Handle exceptions** appropriately for robust applications
7. **Use type hints** with your models for better code quality

## ⚠️ Important Notes

- LazzyORM currently supports MySQL only
- Python 3.7+ is required
- Always close connections properly or use context managers
- Be cautious with operations that affect all rows (without WHERE clauses)
