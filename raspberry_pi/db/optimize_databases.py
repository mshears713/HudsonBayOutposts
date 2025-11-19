"""
Database Optimization Script

This script applies performance-enhancing indexes to all Hudson Bay Outpost databases.

Educational Note:
Indexes dramatically improve query performance but must be added thoughtfully.
This script implements the indexing strategy documented in DATABASE_OPTIMIZATION.md

To run:
    python raspberry_pi/db/optimize_databases.py

Phase 4 Feature (Step 35):
Automated database optimization with strategic indexing.
"""

import sqlite3
from pathlib import Path
import sys

# Database file paths
DB_DIR = Path(__file__).parent / "data"
HUNTING_DB = DB_DIR / "hunting_fort.db"
TRADING_DB = DB_DIR / "trading_fort.db"
FISHING_DB = DB_DIR / "fishing_fort.db"


def optimize_hunting_fort():
    """
    Add optimizing indexes to Hunting Fort database.

    Educational Note:
    These indexes target common query patterns:
    - Filtering by status and date
    - Species and quality aggregations
    - Party-harvest relationships
    """
    if not HUNTING_DB.exists():
        print(f"   Hunting Fort database not found at {HUNTING_DB}")
        print("   Run: python raspberry_pi/db/init_hunting_fort.py")
        return False

    conn = sqlite3.connect(HUNTING_DB)

    print("Optimizing Hunting Fort database...")

    # Additional indexes beyond what's in init script
    indexes = [
        ("idx_parties_status_date", "hunting_parties(status, start_date DESC)"),
        ("idx_parties_region", "hunting_parties(region)"),
        ("idx_harvests_quality", "pelt_harvests(quality)"),
        ("idx_harvests_species_quality", "pelt_harvests(species, quality)"),
        ("idx_harvests_party", "pelt_harvests(party_id)"),
        ("idx_reports_year_season", "seasonal_reports(year DESC, season)")
    ]

    created_count = 0
    for index_name, columns in indexes:
        try:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {columns}")
            print(f"   Created index: {index_name}")
            created_count += 1
        except sqlite3.Error as e:
            print(f"   Failed to create {index_name}: {e}")

    # Run ANALYZE to update statistics
    conn.execute("ANALYZE")

    conn.commit()
    conn.close()

    print(f" Hunting Fort: {created_count} indexes created\n")
    return True


def optimize_trading_fort():
    """
    Add optimizing indexes to Trading Fort database.

    Educational Note:
    Trading Fort indexes focus on:
    - Good category and price filtering
    - Trader type and reputation queries
    - Trade record temporal analysis
    """
    if not TRADING_DB.exists():
        print(f"   Trading Fort database not found at {TRADING_DB}")
        print("   Run: python raspberry_pi/db/init_trading_fort.py")
        return False

    conn = sqlite3.connect(TRADING_DB)

    print("Optimizing Trading Fort database...")

    indexes = [
        ("idx_goods_category", "goods(category)"),
        ("idx_goods_name", "goods(name)"),
        ("idx_goods_price", "goods(current_price)"),
        ("idx_goods_category_price", "goods(category, current_price DESC)"),
        ("idx_traders_type", "traders(trader_type)"),
        ("idx_traders_reputation", "traders(reputation)"),
        ("idx_trades_date", "trade_records(trade_date)"),
        ("idx_trades_trader", "trade_records(trader_id)"),
        ("idx_trades_good", "trade_records(good_id)"),
        ("idx_trades_trader_date", "trade_records(trader_id, trade_date DESC)"),
        ("idx_price_history_good", "price_history(good_id, date)")
    ]

    created_count = 0
    for index_name, columns in indexes:
        try:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {columns}")
            print(f"   Created index: {index_name}")
            created_count += 1
        except sqlite3.Error as e:
            print(f"   Failed to create {index_name}: {e}")

    # Run ANALYZE
    conn.execute("ANALYZE")

    conn.commit()
    conn.close()

    print(f" Trading Fort: {created_count} indexes created\n")
    return True


def optimize_fishing_fort():
    """
    Add optimizing indexes to Fishing Fort database.

    Educational Note:
    Fishing Fort indexes enable:
    - Category-based inventory filtering
    - Species catch analysis
    - Location-based queries
    - Temporal trend analysis
    """
    if not FISHING_DB.exists():
        print(f"   Fishing Fort database not found at {FISHING_DB}")
        print("   Run: python raspberry_pi/db/init_fishing_fort.py")
        return False

    conn = sqlite3.connect(FISHING_DB)

    print("Optimizing Fishing Fort database...")

    indexes = [
        ("idx_inventory_category", "inventory(category)"),
        ("idx_inventory_quantity", "inventory(quantity)"),
        ("idx_catches_species", "fish_catches(species)"),
        ("idx_catches_date", "fish_catches(catch_date)"),
        ("idx_catches_location", "fish_catches(location)"),
        ("idx_catches_species_date", "fish_catches(species, catch_date DESC)")
    ]

    created_count = 0
    for index_name, columns in indexes:
        try:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {columns}")
            print(f"   Created index: {index_name}")
            created_count += 1
        except sqlite3.Error as e:
            print(f"   Failed to create {index_name}: {e}")

    # Run ANALYZE
    conn.execute("ANALYZE")

    conn.commit()
    conn.close()

    print(f" Fishing Fort: {created_count} indexes created\n")
    return True


def verify_indexes(db_path: Path, db_name: str):
    """
    Verify indexes exist in database.

    Args:
        db_path: Path to database file
        db_name: Database name for display
    """
    if not db_path.exists():
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name"
    )

    indexes = [row[0] for row in cursor.fetchall()]
    conn.close()

    if indexes:
        print(f"\n{db_name} Indexes ({len(indexes)}):")
        for idx in indexes:
            print(f"  - {idx}")
    else:
        print(f"\n{db_name}: No custom indexes found")


def show_database_stats():
    """Show statistics for all databases."""
    print("\n" + "="*70)
    print("Database Statistics")
    print("="*70)

    for db_path, db_name in [
        (HUNTING_DB, "Hunting Fort"),
        (TRADING_DB, "Trading Fort"),
        (FISHING_DB, "Fishing Fort")
    ]:
        if not db_path.exists():
            print(f"\n{db_name}: Database not found")
            continue

        conn = sqlite3.connect(db_path)

        # Get database size
        size_query = "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
        size_bytes = conn.execute(size_query).fetchone()[0]
        size_kb = size_bytes / 1024

        # Count indexes
        index_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        ).fetchone()[0]

        # Count tables
        table_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchone()[0]

        conn.close()

        print(f"\n{db_name}:")
        print(f"  Size: {size_kb:.2f} KB")
        print(f"  Tables: {table_count}")
        print(f"  Indexes: {index_count}")


def main():
    """
    Main execution function.

    Optimizes all fort databases and displays statistics.
    """
    print("="*70)
    print("Hudson Bay Outposts Database Optimization")
    print("="*70)
    print()

    # Optimize each database
    results = []
    results.append(("Hunting Fort", optimize_hunting_fort()))
    results.append(("Trading Fort", optimize_trading_fort()))
    results.append(("Fishing Fort", optimize_fishing_fort()))

    # Show results summary
    print("="*70)
    print("Optimization Summary")
    print("="*70)

    for db_name, success in results:
        status = " Success" if success else "   Skipped (database not found)"
        print(f"{db_name}: {status}")

    # Verify indexes
    print("\n" + "="*70)
    print("Verification")
    print("="*70)

    verify_indexes(HUNTING_DB, "Hunting Fort")
    verify_indexes(TRADING_DB, "Trading Fort")
    verify_indexes(FISHING_DB, "Fishing Fort")

    # Show statistics
    show_database_stats()

    print("\n" + "="*70)
    print(" Database optimization complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart API servers to use optimized databases")
    print("2. Monitor query performance improvements")
    print("3. Run ANALYZE periodically to update statistics")
    print("\nSee docs/DATABASE_OPTIMIZATION.md for details")
    print("="*70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
