# LazzyORM API Reference

## Table of Contents
- [Connector](#connector)
- [LazyFetch](#lazyfetch)
- [LazyQuery](#lazyquery)
- [LazyInsert](#lazyinsert)
- [LazyUpdate](#lazyupdate)
- [LazyDelete](#lazydelete)
- [Logger](#logger)
- [Exceptions](#exceptions)
- [Utilities](#utilities)

---

## Connector

Database connection manager with pooling support.

### Constructor

```python
Connector(
    host: str,
    user: str,
    database: str,
    port: int,
    is_azure_server: bool = False,
    password: str = "",
    client_id: str = "",
    pool_size: int = 10,
    pool_name: str = "Lazy_ORM_Pool"
)
```

**Parameters:**
- `host` - MySQL server hostname
- `user` - MySQL username
- `database` - Database name
- `port` - MySQL port (typically 3306)
- `is_azure_server` - Enable Azure authentication
- `password` - MySQL password
- `client_id` - Azure client ID (if using Azure)
- `pool_size` - Connection pool size
- `pool_name` - Connection pool name

### Methods

#### `get_connection_pool()`
Returns MySQL connection pool.

**Returns:** `MySQLConnectionPool`

**Raises:** `ConnectionError` if pool creation fails

#### `test_connection()`
Test database connection.

**Returns:** `bool` - True if connection successful

#### `show_process_list()`
Get list of running MySQL processes.

**Returns:** `list` - Process information

#### `close_pool()`
Close all connections in the pool.

### Example

```python
connector = Connector(
    host='localhost',
    user='root',
    password='password',
    database='mydb',
    port=3306,
    pool_size=20
)

pool = connector.get_connection_pool()
```

---

## LazyFetch

Fetch data with optional caching.

### Constructor

```python
LazyFetch(
    model,
    query: str,
    connection_pool: MySQLConnectionPool,
    params: tuple = None,
    use_cache: bool = True
)
```

**Parameters:**
- `model` - Data model class (typically a dataclass)
- `query` - SQL SELECT query
- `connection_pool` - MySQL connection pool
- `params` - Query parameters (for parameterized queries)
- `use_cache` - Whether to cache results

### Methods

#### `get()`
Execute query and return results.

**Returns:** `List[T]` - List of model instances

**Raises:** `QueryError` if query fails

#### `clear_cache(model_name: str = None)` (class method)
Clear cached results.

**Parameters:**
- `model_name` - Clear cache for specific model (None = clear all)

### Example

```python
users = LazyFetch(
    model=User,
    query="SELECT * FROM users WHERE status = %s",
    connection_pool=pool,
    params=('active',)
).get()
```

---

## LazyQuery

Query builder for SELECT operations.

### Constructor

```python
LazyQuery(
    model,
    connection_pool: MySQLConnectionPool,
    table_name: str = None
)
```

**Parameters:**
- `model` - Data model class
- `connection_pool` - MySQL connection pool
- `table_name` - Table name (defaults to model.__name__)

### Methods

#### `select_all()`
Select all columns.

**Returns:** `self` for chaining

#### `select(*columns: str)`
Select specific columns.

**Parameters:**
- `*columns` - Column names

**Returns:** `self` for chaining

#### `where(column: str, value: Any, operator: str = '=')`
Add WHERE condition.

**Parameters:**
- `column` - Column name
- `value` - Comparison value
- `operator` - One of: `=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`, `IN`, `NOT IN`

**Returns:** `self` for chaining

#### `order_by(column: str, direction: str = 'ASC')`
Add ORDER BY clause.

**Parameters:**
- `column` - Column to sort by
- `direction` - `ASC` or `DESC`

**Returns:** `self` for chaining

#### `limit(limit: int, offset: int = 0)`
Add LIMIT clause.

**Parameters:**
- `limit` - Max rows to return
- `offset` - Rows to skip

**Returns:** `self` for chaining

#### `to_list()`
Execute query and return results.

**Returns:** `List[T]` - List of model instances

#### `first()`
Execute query and return first result.

**Returns:** `Optional[T]` - First result or None

#### `count()`
Count matching rows.

**Returns:** `int` - Row count

### Example

```python
users = (
    LazyQuery(model=User, connection_pool=pool)
    .select("id", "name", "email")
    .where("age", 25, ">")
    .where("status", "active")
    .order_by("name", "ASC")
    .limit(10)
    .to_list()
)
```

---

## LazyInsert

Insert data from CSV or data objects.

### Constructor

```python
LazyInsert(
    table_name: str,
    connection_pool: MySQLConnectionPool,
    path_to_csv: str = None,
    auto_increment: bool = False,
    drop_if_exists: bool = False,
    create_if_not_exists: bool = True,
    log_create_table_query: bool = False,
    log_insert_query: bool = False,
    chunk_size: int = 1000,
    data: List[T] = None,
    query: str = None
)
```

**Parameters:**
- `table_name` - Target table name
- `connection_pool` - MySQL connection pool
- `path_to_csv` - CSV file path (for CSV import)
- `auto_increment` - Add auto-increment ID column
- `drop_if_exists` - Drop table if exists
- `create_if_not_exists` - Create table if doesn't exist
- `log_create_table_query` - Log table creation
- `log_insert_query` - Log insert queries
- `chunk_size` - Rows per insert batch
- `data` - Data objects to insert
- `query` - INSERT query (for data objects)

### Methods

#### `perform_staging_insert()`
Import data from CSV file.

**Returns:** `int` - Rows inserted

**Raises:** `ValidationError`, `QueryError`

#### `insert()`
Insert data objects.

**Returns:** `int` - Rows inserted

**Raises:** `ValidationError`, `QueryError`

### Example

```python
# From CSV
lazy_insert = LazyInsert(
    table_name="users",
    path_to_csv="data.csv",
    connection_pool=pool,
    chunk_size=10000
)
rows = lazy_insert.perform_staging_insert()

# From objects
lazy_insert = LazyInsert(
    table_name="users",
    data=user_objects,
    connection_pool=pool,
    query="INSERT INTO users VALUES (%s, %s, %s)"
)
rows = lazy_insert.insert()
```

---

## LazyUpdate

Update database records.

### Constructor

```python
LazyUpdate(
    table_name: str,
    connection_pool: MySQLConnectionPool
)
```

**Parameters:**
- `table_name` - Table to update
- `connection_pool` - MySQL connection pool

### Methods

#### `set(values: Dict[str, Any])`
Set column values.

**Parameters:**
- `values` - Dictionary of column:value pairs

**Returns:** `self` for chaining

#### `where(column: str, value: Any, operator: str = '=')`
Add WHERE condition.

**Parameters:**
- `column` - Column name
- `value` - Comparison value
- `operator` - Comparison operator

**Returns:** `self` for chaining

#### `execute()`
Execute UPDATE query.

**Returns:** `int` - Rows affected

**Raises:** `QueryError`

### Example

```python
rows = (
    LazyUpdate(table_name="users", connection_pool=pool)
    .set({"status": "inactive", "updated_at": "2024-01-01"})
    .where("last_login", "2023-01-01", "<")
    .execute()
)
```

---

## LazyDelete

Delete database records.

### Constructor

```python
LazyDelete(
    table_name: str,
    connection_pool: MySQLConnectionPool
)
```

**Parameters:**
- `table_name` - Table to delete from
- `connection_pool` - MySQL connection pool

### Methods

#### `where(column: str, value: Any, operator: str = '=')`
Add WHERE condition.

**Parameters:**
- `column` - Column name
- `value` - Comparison value
- `operator` - Comparison operator

**Returns:** `self` for chaining

#### `limit(limit: int)`
Limit number of deletions.

**Parameters:**
- `limit` - Max rows to delete

**Returns:** `self` for chaining

#### `execute(confirm_delete_all: bool = False)`
Execute DELETE query.

**Parameters:**
- `confirm_delete_all` - Must be True to delete without WHERE clause

**Returns:** `int` - Rows deleted

**Raises:** `ValidationError`, `QueryError`

### Example

```python
rows = (
    LazyDelete(table_name="users", connection_pool=pool)
    .where("status", "inactive")
    .limit(1000)
    .execute()
)

# Delete all (requires confirmation)
rows = (
    LazyDelete(table_name="temp_table", connection_pool=pool)
    .execute(confirm_delete_all=True)
)
```

---

## Logger

Custom logger with colored output.

### Constructor

```python
Logger(
    log_file: str = None,
    log_dir: str = "logs",
    logger_name: str = None,
    level: int = logging.DEBUG
)
```

**Parameters:**
- `log_file` - Log file name
- `log_dir` - Log directory
- `logger_name` - Logger name
- `level` - Logging level

### Attributes

#### `logger`
Standard Python logger instance.

### Example

```python
logger = Logger(
    log_file="app.log",
    logger_name="app_logger",
    level=logging.INFO
).logger

logger.info("Application started")
logger.error("Error occurred")
```

---

## Exceptions

### Exception Hierarchy

```
LazzyORMError (base)
├── ConnectionError
├── QueryError
├── ValidationError
├── ConfigurationError
├── DataMappingError
└── PoolExhaustedError
```

### Usage

```python
from lazzy_orm.exceptions import QueryError, ValidationError

try:
    users = query.select_all().to_list()
except ValidationError as e:
    print(f"Invalid input: {e}")
except QueryError as e:
    print(f"Query failed: {e}")
```

---

## Utilities

### parse_date

Parse date strings in various formats.

```python
parse_date(input_date: str) -> date
```

**Parameters:**
- `input_date` - Date string

**Returns:** `date` object

**Raises:** `ValueError` if format not recognized

**Supported Formats:**
- ISO: `2023-01-15`
- US: `01/15/2023`
- EU: `15/01/2023`
- With month names: `Jan 15, 2023`
- Compact: `20230115`
- And many more...

**Example:**

```python
from lazzy_orm import parse_date

date1 = parse_date("2023-01-15")
date2 = parse_date("Jan 15, 2023")
date3 = parse_date("15/01/2023")
```

---

## Context Managers

All major classes support context managers for automatic resource cleanup:

```python
# LazyQuery
with LazyQuery(model=User, connection_pool=pool) as query:
    users = query.select_all().to_list()

# LazyUpdate
with LazyUpdate(table_name="users", connection_pool=pool) as updater:
    rows = updater.set({"status": "active"}).where("id", 1).execute()

# LazyDelete
with LazyDelete(table_name="users", connection_pool=pool) as deleter:
    rows = deleter.where("status", "inactive").execute()

# Connector
with Connector(host='localhost', user='root', password='pass', database='db', port=3306) as conn:
    pool = conn.get_connection_pool()
```

---

## Type Hints

All classes and methods include comprehensive type hints:

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

# Type hints are automatically inferred
users: List[User] = LazyQuery(model=User, connection_pool=pool).select_all().to_list()
user: Optional[User] = LazyQuery(model=User, connection_pool=pool).where("id", 1).first()
```

---

## Best Practices

1. **Always use connection pools** instead of creating individual connections
2. **Use context managers** for automatic resource cleanup
3. **Use parameterized queries** (automatically handled by LazzyORM)
4. **Handle exceptions** appropriately
5. **Clear cache** when data changes outside LazzyORM
6. **Use type hints** with your models
7. **Enable logging** for debugging
8. **Validate inputs** before database operations

---

## Common Patterns

### Pattern: Safe Query Execution

```python
from lazzy_orm.exceptions import QueryError

try:
    with LazyQuery(model=User, connection_pool=pool) as query:
        users = query.select_all().where("status", "active").to_list()
except QueryError as e:
    logger.error(f"Query failed: {e}")
    users = []
```

### Pattern: Bulk Operations

```python
# Insert in chunks
lazy_insert = LazyInsert(
    table_name="users",
    data=large_dataset,
    connection_pool=pool,
    query="INSERT INTO users VALUES (%s, %s, %s)",
    chunk_size=10000  # Process 10k at a time
)
rows = lazy_insert.insert()
```

### Pattern: Conditional Updates

```python
# Update only if conditions met
updater = LazyUpdate(table_name="users", connection_pool=pool)
updater.set({"last_checked": datetime.now()})

if include_inactive:
    pass  # No additional where clause
else:
    updater.where("status", "active")

rows = updater.execute()
```

---

## Version Information

This API reference is for **LazzyORM v0.3.0**

For older versions, see the [CHANGELOG](CHANGELOG.md).

---

## Support

- **Documentation**: [README.md](Readme.md)
- **Examples**: [examples/](examples/)
- **Issues**: [GitHub Issues](https://github.com/Dipendra-creator/LazzyORM/issues)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
