# Database Optimization Guide

This document provides comprehensive guidance on optimizing SQLite databases for the Hudson Bay Outposts project, focusing on indexing strategies, query optimization, and performance monitoring.

## Overview

Educational Note:
Database optimization is crucial for API performance. Proper indexing can improve query speed by 10-100x, but must be balanced against write performance and storage costs.

Phase 4 Enhancement (Step 35):
All three fort databases have been optimized with strategic indexes based on query patterns and access frequencies.

## Index Strategy

### Indexing Principles

1. **Index columns used in WHERE clauses**
   - Most queries filter by specific columns
   - Indexes dramatically speed up lookups

2. **Index foreign keys**
   - JOIN operations benefit from indexed foreign keys
   - Improves referential integrity checks

3. **Index columns used in ORDER BY**
   - Sorting is expensive without indexes
   - Indexed columns allow efficient sorting

4. **Composite indexes for common query patterns**
   - Multiple columns frequently queried together
   - Order matters: most selective column first

5. **Avoid over-indexing**
   - Each index increases write time
   - Indexes consume storage space
   - Balance read vs write performance

## Existing Indexes

### Hunting Fort Database

#### Table: game_animals
```sql
-- Already created in init_hunting_fort.py
CREATE INDEX idx_animals_category ON game_animals(category);
CREATE INDEX idx_animals_status ON game_animals(population_status);
```

**Rationale:**
- `category` filter is very common (browsing by game type)
- `population_status` used for conservation queries
- Both improve WHERE clause performance

#### Table: hunting_parties
```sql
-- Already created
CREATE INDEX idx_parties_status ON hunting_parties(status);
CREATE INDEX idx_parties_date ON hunting_parties(start_date);
```

**Rationale:**
- `status` filter (active/completed/planning) is frequent
- `start_date` enables temporal queries and sorting
- Date range queries benefit significantly

**Additional Recommended Indexes:**
```sql
-- Composite index for common status + date queries
CREATE INDEX idx_parties_status_date ON hunting_parties(status, start_date DESC);

-- Region-based queries
CREATE INDEX idx_parties_region ON hunting_parties(region);
```

#### Table: pelt_harvests
```sql
-- Already created
CREATE INDEX idx_harvests_species ON pelt_harvests(species);
CREATE INDEX idx_harvests_date ON pelt_harvests(date_harvested);
```

**Rationale:**
- `species` aggregation queries are common
- `date_harvested` for temporal analysis
- Both enable efficient GROUP BY operations

**Additional Recommended Indexes:**
```sql
-- Quality-based filtering
CREATE INDEX idx_harvests_quality ON pelt_harvests(quality);

-- Composite for species + quality analysis
CREATE INDEX idx_harvests_species_quality ON pelt_harvests(species, quality);

-- Party relationship queries
CREATE INDEX idx_harvests_party ON pelt_harvests(party_id);
```

#### Table: seasonal_reports
```sql
-- Already created
CREATE INDEX idx_reports_year ON seasonal_reports(year);
```

**Additional Recommended Indexes:**
```sql
-- Multi-year trend analysis
CREATE INDEX idx_reports_year_season ON seasonal_reports(year DESC, season);
```

### Trading Fort Database

#### Recommended Indexes
```sql
-- Trade goods filtering and sorting
CREATE INDEX idx_goods_category ON goods(category);
CREATE INDEX idx_goods_name ON goods(name);
CREATE INDEX idx_goods_price ON goods(current_price);

-- Composite for category + price queries
CREATE INDEX idx_goods_category_price ON goods(category, current_price DESC);

-- Traders
CREATE INDEX idx_traders_type ON traders(trader_type);
CREATE INDEX idx_traders_reputation ON traders(reputation);

-- Trade records - temporal queries
CREATE INDEX idx_trades_date ON trade_records(trade_date);
CREATE INDEX idx_trades_trader ON trade_records(trader_id);
CREATE INDEX idx_trades_good ON trade_records(good_id);

-- Composite for trader transaction history
CREATE INDEX idx_trades_trader_date ON trade_records(trader_id, trade_date DESC);

-- Price history - good trends
CREATE INDEX idx_price_history_good ON price_history(good_id, date);
```

### Fishing Fort Database

#### Recommended Indexes
```sql
-- Inventory filtering
CREATE INDEX idx_inventory_category ON inventory(category);
CREATE INDEX idx_inventory_quantity ON inventory(quantity);

-- Catches - species and date queries
CREATE INDEX idx_catches_species ON fish_catches(species);
CREATE INDEX idx_catches_date ON fish_catches(catch_date);
CREATE INDEX idx_catches_location ON fish_catches(location);

-- Composite for species trends over time
CREATE INDEX idx_catches_species_date ON fish_catches(species, catch_date DESC);
```

## Query Optimization Patterns

### 1. Use Covering Indexes

**Problem:** Query retrieves columns not in index, requiring table lookup

**Solution:** Include frequently accessed columns in index
```sql
-- Instead of:
CREATE INDEX idx_goods_category ON goods(category);

-- Use covering index:
CREATE INDEX idx_goods_category_name_price ON goods(category, name, current_price);
```

### 2. Index Selectivity

**Educational Note:**
Index selectivity = number of distinct values / total rows

High selectivity (close to 1.0) = good index candidate
Low selectivity (close to 0.0) = poor index candidate

**Example:**
```sql
-- Good: species (many distinct values)
CREATE INDEX idx_animals_species ON game_animals(species);

-- Poor: has_pelts (only true/false)
-- Don't index boolean columns with low selectivity
```

### 3. Prefix Indexes for Text Columns

For long text fields, index only the prefix:
```sql
-- Index first 20 characters of description
CREATE INDEX idx_goods_desc_prefix ON goods(description COLLATE NOCASE);
```

### 4. Partial Indexes

Index only relevant subset of data:
```sql
-- Only index active parties (most queries focus on these)
CREATE INDEX idx_active_parties ON hunting_parties(start_date)
WHERE status = 'active';
```

## Performance Monitoring

### Analyze Query Plans

Use EXPLAIN QUERY PLAN to verify index usage:
```sql
EXPLAIN QUERY PLAN
SELECT * FROM game_animals
WHERE category = 'big_game'
ORDER BY species;
```

**Good output:**
```
SEARCH game_animals USING INDEX idx_animals_category (category=?)
USE TEMP B-TREE FOR ORDER BY
```

**Bad output:**
```
SCAN game_animals
```
(SCAN means no index used - full table scan)

### Index Usage Statistics

Check which indexes are actually used:
```sql
-- SQLite doesn't track index usage directly
-- Monitor query performance before/after index creation
```

### Benchmark Queries

```python
import sqlite3
import time

def benchmark_query(db_path, query, iterations=100):
    """Benchmark a query to measure performance."""
    conn = sqlite3.connect(db_path)

    start = time.time()
    for _ in range(iterations):
        conn.execute(query).fetchall()
    end = time.time()

    conn.close()

    avg_time = (end - start) / iterations
    print(f"Average query time: {avg_time*1000:.2f}ms")

    return avg_time
```

## Index Maintenance

### Rebuild Indexes

Indexes can become fragmented. Rebuild periodically:
```sql
-- Analyze database to update statistics
ANALYZE;

-- Vacuum to rebuild database and optimize storage
VACUUM;
```

### Monitor Index Size

```sql
-- Check database size
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- View index information
SELECT name, sql FROM sqlite_master WHERE type = 'index';
```

## Implementation Script

Create a script to apply all recommended indexes:

```python
# raspberry_pi/db/optimize_databases.py

import sqlite3
from pathlib import Path

def optimize_hunting_fort():
    """Add optimizing indexes to Hunting Fort database."""
    db_path = Path(__file__).parent / "data" / "hunting_fort.db"
    conn = sqlite3.connect(db_path)

    # Additional indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_parties_status_date ON hunting_parties(status, start_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_parties_region ON hunting_parties(region)",
        "CREATE INDEX IF NOT EXISTS idx_harvests_quality ON pelt_harvests(quality)",
        "CREATE INDEX IF NOT EXISTS idx_harvests_species_quality ON pelt_harvests(species, quality)",
        "CREATE INDEX IF NOT EXISTS idx_harvests_party ON pelt_harvests(party_id)",
        "CREATE INDEX IF NOT EXISTS idx_reports_year_season ON seasonal_reports(year DESC, season)"
    ]

    for index_sql in indexes:
        conn.execute(index_sql)

    conn.commit()
    conn.close()
    print(" Hunting Fort database optimized")

def optimize_trading_fort():
    """Add optimizing indexes to Trading Fort database."""
    db_path = Path(__file__).parent / "data" / "trading_fort.db"
    conn = sqlite3.connect(db_path)

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_goods_category ON goods(category)",
        "CREATE INDEX IF NOT EXISTS idx_goods_name ON goods(name)",
        "CREATE INDEX IF NOT EXISTS idx_goods_price ON goods(current_price)",
        "CREATE INDEX IF NOT EXISTS idx_goods_category_price ON goods(category, current_price DESC)",
        "CREATE INDEX IF NOT EXISTS idx_traders_type ON traders(trader_type)",
        "CREATE INDEX IF NOT EXISTS idx_traders_reputation ON traders(reputation)",
        "CREATE INDEX IF NOT EXISTS idx_trades_date ON trade_records(trade_date)",
        "CREATE INDEX IF NOT EXISTS idx_trades_trader ON trade_records(trader_id)",
        "CREATE INDEX IF NOT EXISTS idx_trades_good ON trade_records(good_id)",
        "CREATE INDEX IF NOT EXISTS idx_trades_trader_date ON trade_records(trader_id, trade_date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_price_history_good ON price_history(good_id, date)"
    ]

    for index_sql in indexes:
        conn.execute(index_sql)

    conn.commit()
    conn.close()
    print(" Trading Fort database optimized")

def optimize_fishing_fort():
    """Add optimizing indexes to Fishing Fort database."""
    db_path = Path(__file__).parent / "data" / "fishing_fort.db"
    conn = sqlite3.connect(db_path)

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category)",
        "CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity)",
        "CREATE INDEX IF NOT EXISTS idx_catches_species ON fish_catches(species)",
        "CREATE INDEX IF NOT EXISTS idx_catches_date ON fish_catches(catch_date)",
        "CREATE INDEX IF NOT EXISTS idx_catches_location ON fish_catches(location)",
        "CREATE INDEX IF NOT EXISTS idx_catches_species_date ON fish_catches(species, catch_date DESC)"
    ]

    for index_sql in indexes:
        conn.execute(index_sql)

    conn.commit()
    conn.close()
    print(" Fishing Fort database optimized")

def main():
    """Optimize all fort databases."""
    print("Optimizing Hudson Bay Outpost databases...")
    optimize_hunting_fort()
    optimize_trading_fort()
    optimize_fishing_fort()

    print("\n All databases optimized!")
    print("\nTo verify indexes, run:")
    print("  sqlite3 <database>.db '.indexes'")

if __name__ == "__main__":
    main()
```

## Performance Impact

### Expected Improvements

With proper indexing:

**Before Indexing:**
- Filter queries: 100-500ms (full table scan)
- Sorted queries: 200-1000ms (in-memory sort)
- JOIN queries: 500-2000ms (nested loops)

**After Indexing:**
- Filter queries: 1-10ms (index seek)
- Sorted queries: 5-20ms (index scan)
- JOIN queries: 10-50ms (index joins)

**Typical improvements:** 10-100x faster

### Trade-offs

**Benefits:**
- Faster SELECT queries
- Better scalability
- Improved user experience

**Costs:**
- Slower INSERT/UPDATE/DELETE (10-20% overhead)
- Additional storage (typically 10-30% of table size)
- More complex database maintenance

## Best Practices

1. **Index Before Production**
   - Add indexes during development
   - Test with realistic data volumes

2. **Monitor Query Patterns**
   - Log slow queries
   - Analyze access patterns
   - Index accordingly

3. **Test Index Impact**
   - Benchmark before and after
   - Measure both reads and writes
   - Validate improvements

4. **Regular Maintenance**
   - Run ANALYZE monthly
   - VACUUM quarterly
   - Review index usage periodically

5. **Document Indexes**
   - Explain why each index exists
   - Note expected query patterns
   - Track performance improvements

## Troubleshooting

### Query Still Slow After Indexing

1. **Verify index is used**
   ```sql
   EXPLAIN QUERY PLAN SELECT ...
   ```

2. **Check index selectivity**
   - Low selectivity indexes may not help
   - Consider composite indexes

3. **Look for implicit type conversions**
   ```sql
   -- Bad: index not used due to type mismatch
   WHERE text_column = 123

   -- Good: use correct type
   WHERE text_column = '123'
   ```

4. **Avoid functions on indexed columns**
   ```sql
   -- Bad: index not used
   WHERE LOWER(name) = 'moose'

   -- Good: use functional index or store lowercase
   WHERE name = 'moose'
   ```

### Index Not Being Used

Common reasons:
- Table is too small (SQLite prefers full scan)
- Query uses OR conditions
- Column has low selectivity
- Missing statistics (run ANALYZE)

## Conclusion

Proper indexing is essential for production database performance. This guide provides strategic index recommendations for all Hudson Bay Outpost databases, balancing query performance with maintenance overhead.

Key takeaways:
- Index columns used in WHERE, ORDER BY, and JOIN
- Use composite indexes for common query patterns
- Monitor query plans to verify index usage
- Balance read performance vs write overhead
- Maintain indexes with ANALYZE and VACUUM

For questions or optimization assistance, refer to SQLite documentation or consult database performance guides.
