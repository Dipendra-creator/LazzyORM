"""
Example: Complete CRUD operations with LazzyORM
"""
from lazzy_orm import (
    Connector,
    LazyFetch,
    LazyInsert,
    LazyQuery,
    LazyUpdate,
    LazyDelete,
    Logger
)
from dataclasses import dataclass
import logging


# Setup logging
logger = Logger(log_file="crud_example.log", logger_name="crud_example", level=logging.INFO).logger


@dataclass
class User:
    """User data model."""
    id: int
    name: str
    email: str
    age: int
    status: str = "active"


def main():
    """Demonstrate CRUD operations."""
    
    # 1. Connect to database
    logger.info("Connecting to database...")
    connector = Connector(
        host='localhost',
        user='root',
        password='your_password',
        database='testdb',
        port=3306,
        pool_size=10
    )
    
    # Test connection
    if not connector.test_connection():
        logger.error("Failed to connect to database")
        return
    
    connection_pool = connector.get_connection_pool()
    logger.info("Connected successfully!")
    
    # 2. CREATE - Insert new users
    logger.info("\n--- CREATE Operation ---")
    users_to_insert = [
        User(1, "Alice Johnson", "alice@example.com", 28, "active"),
        User(2, "Bob Smith", "bob@example.com", 35, "active"),
        User(3, "Charlie Brown", "charlie@example.com", 42, "inactive"),
    ]
    
    insert_query = "INSERT INTO users (id, name, email, age, status) VALUES (%s, %s, %s, %s, %s)"
    lazy_insert = LazyInsert(
        table_name="users",
        data=users_to_insert,
        connection_pool=connection_pool,
        query=insert_query
    )
    
    try:
        rows_inserted = lazy_insert.insert()
        logger.info(f"✓ Inserted {rows_inserted} users")
    except Exception as e:
        logger.error(f"✗ Insert failed: {e}")
    
    # 3. READ - Fetch users
    logger.info("\n--- READ Operation ---")
    
    # Fetch all users
    all_users = LazyFetch(
        model=User,
        query="SELECT * FROM users",
        connection_pool=connection_pool
    ).get()
    logger.info(f"✓ Found {len(all_users)} users total")
    
    # Query specific users
    active_users = (
        LazyQuery(model=User, connection_pool=connection_pool)
        .select_all()
        .where("status", "active")
        .order_by("age", "ASC")
        .to_list()
    )
    logger.info(f"✓ Found {len(active_users)} active users")
    for user in active_users:
        logger.info(f"  - {user.name} (age {user.age})")
    
    # Get single user
    user = (
        LazyQuery(model=User, connection_pool=connection_pool)
        .select_all()
        .where("email", "alice@example.com")
        .first()
    )
    if user:
        logger.info(f"✓ Found user by email: {user.name}")
    
    # Count users
    user_count = (
        LazyQuery(model=User, connection_pool=connection_pool)
        .where("age", 30, ">=")
        .count()
    )
    logger.info(f"✓ Users aged 30+: {user_count}")
    
    # 4. UPDATE - Modify existing records
    logger.info("\n--- UPDATE Operation ---")
    
    # Update single user
    rows_updated = (
        LazyUpdate(table_name="users", connection_pool=connection_pool)
        .set({"age": 29})
        .where("name", "Alice Johnson")
        .execute()
    )
    logger.info(f"✓ Updated {rows_updated} user(s)")
    
    # Update multiple users
    rows_updated = (
        LazyUpdate(table_name="users", connection_pool=connection_pool)
        .set({"status": "verified"})
        .where("age", 30, ">=")
        .execute()
    )
    logger.info(f"✓ Set {rows_updated} user(s) as verified")
    
    # 5. DELETE - Remove records
    logger.info("\n--- DELETE Operation ---")
    
    # Delete specific user
    rows_deleted = (
        LazyDelete(table_name="users", connection_pool=connection_pool)
        .where("status", "inactive")
        .execute()
    )
    logger.info(f"✓ Deleted {rows_deleted} inactive user(s)")
    
    # Delete with IN clause
    rows_deleted = (
        LazyDelete(table_name="users", connection_pool=connection_pool)
        .where("id", [1, 2], "IN")
        .execute()
    )
    logger.info(f"✓ Deleted {rows_deleted} user(s) by ID")
    
    # 6. Advanced Queries
    logger.info("\n--- Advanced Queries ---")
    
    # Complex query with multiple conditions
    results = (
        LazyQuery(model=User, connection_pool=connection_pool)
        .select("name", "email", "age")
        .where("age", 25, ">=")
        .where("status", "active")
        .order_by("name", "ASC")
        .limit(10)
        .to_list()
    )
    logger.info(f"✓ Complex query returned {len(results)} results")
    
    # Using context managers
    logger.info("\n--- Using Context Managers ---")
    with LazyQuery(model=User, connection_pool=connection_pool) as query:
        users = query.select_all().where("status", "active").to_list()
        logger.info(f"✓ Found {len(users)} users using context manager")
    
    # 7. Clear cache
    LazyFetch.clear_cache('User')
    logger.info("\n✓ Cache cleared")
    
    # 8. Close connection pool
    connector.close_pool()
    logger.info("✓ Connection pool closed\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
