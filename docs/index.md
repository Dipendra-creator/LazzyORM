# LazyORM: A Powerful Lazy Loading ORM for MySQL

![PyPI - version](https://badge.fury.io/py/LazzyORM.svg)(https://pypi.org/project/LazzyORM/)

LazyORM is a Python library crafted to streamline your database operations with MySQL, emphasizing efficiency and simplicity through lazy loading techniques.

## Key Features

* **Lazy Loading:** Only fetches data when necessary, significantly enhancing performance while minimizing memory footprint.
* **Simplified API:** Offers an intuitive interface for database interactions, ensuring a seamless development process.
* **Connection Pooling:** Optimizes database connection management, leading to quicker and more stable access.
* **Logging:** Equipped with extensive logging features to aid in the monitoring and debugging of database activities.

## Installation

Install LazyORM effortlessly using pip:

```bash
pip install LazzyORM
```

## Quick Start

Here's a simple example to get you started with LazyORM:

```python
from lazzy_orm.config import Connector
from lazzy_orm.lazzy_fetch.lazzy_fetch import LazyFetch
from lazzy_orm.logger.logger import Logger
from dataclasses import dataclass

# Connect to the database
connector = Connector(host='localhost', user='root', password='root', database='testdb', port=3306)
logger = Logger(log_file="main.log", logger_name="main_logger").logger

@dataclass
class Table:
    table_name: str

if __name__ == '__main__':
    # Create a table
    connection_pool = connector.get_connection_pool()
    with connection_pool.get_connection() as connection:
        with connection.cursor() as cursor:
            # print all the tables in the database
            tables = LazyFetch(model=Table, query="show tables", _connection_pool=connection_pool).get()
            logger.info(f"Tables in the database: {tables}")
```

Here's a simple example of LazyInsert to with LazyORM:
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
