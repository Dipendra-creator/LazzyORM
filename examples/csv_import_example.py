"""
Example: CSV Import with LazzyORM
"""
from lazzy_orm import Connector, LazyInsert, Logger
import logging
import os
import csv


# Setup logging
logger = Logger(log_file="csv_import.log", logger_name="csv_import", level=logging.INFO).logger


def create_sample_csv(filepath: str):
    """Create a sample CSV file for testing."""
    data = [
        ["id", "name", "email", "age", "city"],
        ["1", "John Doe", "john@example.com", "30", "New York"],
        ["2", "Jane Smith", "jane@example.com", "25", "Los Angeles"],
        ["3", "Bob Johnson", "bob@example.com", "35", "Chicago"],
        ["4", "Alice Williams", "alice@example.com", "28", "Houston"],
        ["5", "Charlie Brown", "charlie@example.com", "32", "Phoenix"],
    ]
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    logger.info(f"Created sample CSV: {filepath}")


def main():
    """Demonstrate CSV import functionality."""
    
    # Create sample CSV
    csv_path = "examples/data/users.csv"
    create_sample_csv(csv_path)
    
    # Connect to database
    logger.info("Connecting to database...")
    connector = Connector(
        host='localhost',
        user='root',
        password='your_password',
        database='testdb',
        port=3306
    )
    
    connection_pool = connector.get_connection_pool()
    logger.info("Connected successfully!")
    
    # Import CSV with auto table creation
    logger.info("\n--- Importing CSV ---")
    lazy_insert = LazyInsert(
        table_name="users_from_csv",
        path_to_csv=csv_path,
        connection_pool=connection_pool,
        drop_if_exists=True,        # Drop table if exists
        auto_increment=True,         # Add auto-increment ID
        chunk_size=1000,            # Insert in chunks of 1000
        log_create_table_query=True,
        log_insert_query=True
    )
    
    try:
        rows_inserted = lazy_insert.perform_staging_insert()
        logger.info(f"✓ Successfully imported {rows_inserted} rows from CSV")
    except Exception as e:
        logger.error(f"✗ CSV import failed: {e}")
    
    # Import large CSV with custom settings
    logger.info("\n--- Importing Large CSV ---")
    large_csv = "examples/data/large_dataset.csv"
    
    # You would have your large CSV here
    # For demo, we'll use the same small CSV
    if os.path.exists(csv_path):
        lazy_insert_large = LazyInsert(
            table_name="large_dataset",
            path_to_csv=csv_path,
            connection_pool=connection_pool,
            drop_if_exists=False,       # Don't drop if exists
            create_if_not_exists=True,  # Create if doesn't exist
            auto_increment=True,
            chunk_size=10000,           # Larger chunks for performance
            log_create_table_query=False,
            log_insert_query=False      # Don't log each query for large imports
        )
        
        try:
            rows = lazy_insert_large.perform_staging_insert()
            logger.info(f"✓ Imported {rows} rows from large dataset")
        except Exception as e:
            logger.error(f"✗ Large import failed: {e}")
    
    # Cleanup
    connector.close_pool()
    logger.info("\n✓ Import completed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
