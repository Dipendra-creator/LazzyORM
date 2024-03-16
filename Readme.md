# LazyORM: A Powerful Lazy Loading ORM for MySQL

[![PyPI - version](https://badge.fury.io/py/lazyorm.svg)](https://pypi.org/project/lazyorm/)  # Update the link once you publish to PyPI

LazyORM is a Python library designed to simplify database interactions with MySQL. It provides a clean and efficient way to work with your data by leveraging lazy loading techniques.

## Key Features

* **Lazy Loading:** Fetch data from the database only when it's actually needed, improving performance and reducing memory usage.
* **Simplified API:** Interact with your database using intuitive methods for a smooth development experience.
* **Connection Pooling:** Manages database connections efficiently for faster and more reliable database access.
* **Logging:** Provides comprehensive logging capabilities to help you monitor and troubleshoot database interactions.

## Installation

You can install LazyORM using pip:

```bash
pip install lazyorm
```

## Quick Start

Here's a simple example to get you started with LazyORM:

```python
from lazyorm import LazyFetch

class User(object):
  def __init__(self, id, name, email):
    self.id = id
    self.name = name
    self.email = email

def get_users():
  query = "SELECT * FROM users"
  return LazyFetch(User, query).get()

users = get_users()

for user in users:
  print(f"User: {user.name} (Email: {user.email})")
```

## Documentation

For more details on how to use LazyORM, check out the [documentation](https://github.com/Dipendra-creator).

## Contributing

If you'd like to contribute to LazyORM, please read our [contributing guidelines](

## License

LazyORM is distributed under the [MIT License](
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
