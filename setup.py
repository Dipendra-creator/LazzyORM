from setuptools import setup, find_packages

PACKAGE_NAME = "LazzyORM"
DESCRIPTION = "A Powerful Lazy Loading ORM for MySQL"
AUTHOR = "Dipendra Bhardwaj"
AUTHOR_EMAIL = "dipu.sharma.1122@gmail.com"

INSTALL_REQUIRES = [
    "mysql-connector-python",
    "click",
    "requests",
]

setup(
    name=PACKAGE_NAME,
    version="0.1.8",
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    install_requires=INSTALL_REQUIRES,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "lazyorm_cli=lazyorm.cli:main",
        ],
    },
)
