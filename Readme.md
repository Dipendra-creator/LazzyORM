# LazyORM: A Powerful Lazy Loading ORM for MySQL

[![PyPI - version](https://d25lcipzij17d.cloudfront.net/badge.svg?id=py&r=r&ts=1683906897&type=6e&v=0.2.2&x2=0)](https://pypi.org/project/LazzyORM/)


LazyORM is a Python library designed to simplify database interactions with MySQL. It provides a clean and efficient way to work with your data by leveraging lazy loading techniques.

## Key Features

* **Lazy Loading:** Fetch data from the database only when it's actually needed, improving performance and reducing memory usage.
* **Simplified API:** Interact with your database using intuitive methods for a smooth development experience.
* **Connection Pooling:** Manages database connections efficiently for faster and more reliable database access.
* **Logging:** Provides comprehensive logging capabilities to help you monitor and troubleshoot database interactions.

## Installation

You can install LazyORM using pip:

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
from lazzy_orm.lazzy_fetch.lazzy_fetch import LazyFetch
from lazzy_orm.lazzy_insert.lazzy_insert import LazyInsert
from lazzy_orm.logger.logger import Logger
from dataclasses import dataclass
import os


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
            
            current_dir = os.path.dirname(__file__)
        cursor.close()
    
    # dumping csv into the database 
    test_csv = os.path.join(current_dir, "test_table.csv")
    lazy_insert = LazyInsert(
        table_name="test_table",
        path_to_csv=test_csv,
        _connection_pool=connection_pool,
        drop_if_exists=True,
        auto_increment=True,
        chunk_size=10000,
        log_create_table_query=True,
        log_insert_query=True
    )
    lazy_insert.perform_staging_insert()
    
    @dataclass
    class Tutorial:
        id: int
        title: str
        description: str
        published: int

    data = [
        Tutorial(1, 'Python', 'Python programming language', 1),
        Tutorial(2, 'Java', 'Java programming language', 1),
        Tutorial(3, 'C++', 'C++ programming language', 0)
    ]    
    
    lazy_insert_data = LazyInsert(
        table_name="tutorial",
        data=data,
        _connection_pool=connection_pool,
        query="insert into tutorial (id, title, description, published) values (%s, %s, %s, %s)",
    )
    
    lazy_insert_data.insert()
    
    logger.info("Data inserted successfully")    

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
