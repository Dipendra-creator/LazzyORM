from setuptools import setup, find_packages

PACKAGE_NAME = "LazzyORM"
DESCRIPTION = "A Powerful Lazy Loading ORM for MySQL"
AUTHOR = "Dipendra Bhardwaj"
AUTHOR_EMAIL = "dipu.sharma.1122@gmail.com"

INSTALL_REQUIRES = [
    "mysql-connector-python",
    "click",
    "requests",
    "pandas"
]

setup(
    name=PACKAGE_NAME,
    version="0.2.0",
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    install_requires=INSTALL_REQUIRES,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "lazzy_orm=lazzy_orm.cli:cli"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    url="https://pypi.org/project/LazzyORM/"
)
