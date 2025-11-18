"""
Database initialization script for Fishing Fort outpost.

This script creates and populates the SQLite database for the Fishing Fort
outpost with thematic tables and sample data.

Educational Note:
This demonstrates database initialization patterns commonly used in
distributed systems. Each outpost maintains its own local database.

Usage:
    python raspberry_pi/db/init_fishing_fort.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Configuration
DATABASE_NAME = "fishing_fort.db"
SCHEMA_FILE = "schemas/fishing_fort_schema.sql"


def get_db_path() -> Path:
    """
    Determine the database file path.

    Returns:
        Path object for the database file

    Educational Note:
    We store databases in a 'data' directory to keep them separate from code.
    This makes backup and deployment easier.
    """
    # Create data directory if it doesn't exist
    db_dir = Path(__file__).parent / "data"
    db_dir.mkdir(exist_ok=True)

    return db_dir / DATABASE_NAME


def get_schema_path() -> Path:
    """Get the path to the SQL schema file."""
    return Path(__file__).parent / SCHEMA_FILE


def initialize_database(db_path: Path, schema_path: Path) -> bool:
    """
    Initialize the database with schema and sample data.

    Args:
        db_path: Path to the database file
        schema_path: Path to the SQL schema file

    Returns:
        True if successful, False otherwise

    Educational Note:
    SQLite databases are single files, making them perfect for embedded
    systems like Raspberry Pi. The database is created automatically when
    we first connect to it.
    """
    try:
        print(f"📦 Initializing Fishing Fort database at {db_path}")

        # Read schema SQL
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Connect to database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute schema SQL
        print("📝 Executing schema SQL...")
        cursor.executescript(schema_sql)

        # Commit changes
        conn.commit()

        # Verify tables were created
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = cursor.fetchall()

        print("\n✅ Database initialized successfully!")
        print(f"📊 Created tables: {', '.join(t[0] for t in tables)}")

        # Show sample data counts
        print("\n📈 Sample data loaded:")
        for table_name in [t[0] for t in tables]:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")

        # Close connection
        conn.close()

        print(f"\n🎉 Fishing Fort database ready at: {db_path}")
        print("💡 You can now start the FastAPI server to access the data via API")

        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def verify_database(db_path: Path) -> None:
    """
    Verify database integrity and show summary statistics.

    Args:
        db_path: Path to the database file

    Educational Note:
    It's good practice to verify database state after initialization.
    This helps catch issues early.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n🔍 Database Verification:")
        print("=" * 50)

        # Inventory summary
        cursor.execute("""
            SELECT category, COUNT(*), SUM(quantity)
            FROM inventory
            GROUP BY category
        """)
        print("\n📦 Inventory by Category:")
        for category, item_count, total_qty in cursor.fetchall():
            print(f"  - {category}: {item_count} items, {total_qty} total units")

        # Catch records summary
        cursor.execute("""
            SELECT fish_type, COUNT(*), SUM(weight_pounds)
            FROM catch_records
            GROUP BY fish_type
            ORDER BY SUM(weight_pounds) DESC
        """)
        print("\n🎣 Catch Records by Fish Type:")
        for fish_type, count, total_weight in cursor.fetchall():
            print(f"  - {fish_type}: {count} catches, {total_weight:.1f} lbs total")

        # Equipment summary
        cursor.execute("""
            SELECT equipment_type, COUNT(*), condition
            FROM equipment
            GROUP BY equipment_type, condition
        """)
        print("\n🛠️  Equipment Status:")
        for eq_type, count, condition in cursor.fetchall():
            print(f"  - {eq_type} ({condition}): {count}")

        conn.close()
        print("=" * 50)

    except Exception as e:
        print(f"⚠️  Verification warning: {e}")


def main():
    """Main execution function."""
    print("🏔️  Raspberry Pi Frontier - Fishing Fort Database Initialization")
    print("=" * 70)

    # Get paths
    db_path = get_db_path()
    schema_path = get_schema_path()

    # Check if database already exists
    if db_path.exists():
        response = input(f"\n⚠️  Database already exists at {db_path}\n"
                        "Do you want to reinitialize it? This will DELETE all data! (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Initialization cancelled.")
            return
        print("🗑️  Removing existing database...")
        db_path.unlink()

    # Initialize database
    success = initialize_database(db_path, schema_path)

    if success:
        # Verify database
        verify_database(db_path)
        print("\n✨ Initialization complete!")
    else:
        print("\n❌ Initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
