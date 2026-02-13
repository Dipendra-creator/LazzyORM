from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_file(filename):
    """Read and return the contents of a file."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), encoding='utf-8') as f:
        return f.read()

PACKAGE_NAME = "LazzyORM"
VERSION = "0.3.0"
DESCRIPTION = "A Powerful Lazy Loading ORM for MySQL with SQL Injection Protection"
LONG_DESCRIPTION = read_file("Readme.md")
AUTHOR = "Dipendra Bhardwaj"
AUTHOR_EMAIL = "dipu.sharma.1122@gmail.com"
URL = "https://github.com/Dipendra-creator/LazzyORM"
DOWNLOAD_URL = f"https://github.com/Dipendra-creator/LazzyORM/archive/v{VERSION}.tar.gz"
LICENSE = "MIT"

INSTALL_REQUIRES = [
    "mysql-connector-python>=8.0.0",
    "click>=7.0",
    "requests>=2.25.0",
    "pandas>=1.0.0",
]

DEV_REQUIRES = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
    "isort>=5.10.0",
]

DOCS_REQUIRES = [
    "mkdocs>=1.4.0",
    "mkdocs-material>=8.5.0",
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    download_url=DOWNLOAD_URL,
    license=LICENSE,
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require={
        "dev": DEV_REQUIRES,
        "docs": DOCS_REQUIRES,
        "all": DEV_REQUIRES + DOCS_REQUIRES,
    },
    entry_points={
        "console_scripts": [
            "lazzy_orm=lazzy_orm.cli:cli"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Framework :: Flask",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    keywords=[
        "mysql",
        "orm",
        "database",
        "lazy-loading",
        "connection-pooling",
        "sql",
        "mysql-connector",
        "query-builder",
        "sql-injection-protection",
        "database-abstraction",
        "crud",
        "csv-import",
    ],
    project_urls={
        "Documentation": "https://github.com/Dipendra-creator/LazzyORM#readme",
        "Bug Reports": "https://github.com/Dipendra-creator/LazzyORM/issues",
        "Source": "https://github.com/Dipendra-creator/LazzyORM",
        "Changelog": "https://github.com/Dipendra-creator/LazzyORM/blob/main/CHANGELOG.md",
        "API Reference": "https://github.com/Dipendra-creator/LazzyORM/blob/main/API_REFERENCE.md",
    },
    zip_safe=False,
)
