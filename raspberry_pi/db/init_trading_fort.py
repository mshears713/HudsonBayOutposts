"""
Trading Fort Database Initialization Script

This script creates and initializes the SQLite database for the Trading Fort outpost.
The trading fort manages trade goods, trade records, traders, and price history.

Educational Note:
This demonstrates thematic database design for a trading outpost in the frontier.
The schema supports tracking goods, traders, transactions, and market dynamics.

To run:
    python raspberry_pi/db/init_trading_fort.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Database path
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "trading_fort.db"


def create_tables(conn):
    """
    Create database tables for the trading fort.

    Educational Note:
    The schema includes:
    - goods: Trade goods inventory (furs, supplies, tools)
    - trade_records: Historical trade transactions
    - traders: Registry of trappers and traders
    - price_history: Price fluctuations over time
    """
    cursor = conn.cursor()

    # Goods inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goods (
            good_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            unit TEXT NOT NULL,
            base_price REAL NOT NULL,
            current_price REAL NOT NULL,
            quality TEXT CHECK(quality IN ('poor', 'fair', 'good', 'excellent')),
            origin TEXT,
            description TEXT,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Trade records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_records (
            trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            good_id INTEGER,
            trader_id INTEGER,
            trade_type TEXT CHECK(trade_type IN ('buy', 'sell', 'exchange')),
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            total_value REAL NOT NULL,
            trade_date TEXT NOT NULL,
            payment_method TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (good_id) REFERENCES goods(good_id),
            FOREIGN KEY (trader_id) REFERENCES traders(trader_id)
        )
    """)

    # Traders registry table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traders (
            trader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            trader_type TEXT CHECK(trader_type IN ('trapper', 'native_trader', 'fort_trader', 'merchant')),
            reputation TEXT CHECK(reputation IN ('poor', 'fair', 'good', 'excellent')),
            total_trades INTEGER DEFAULT 0,
            total_value REAL DEFAULT 0.0,
            credit_limit REAL DEFAULT 0.0,
            last_trade_date TEXT,
            notes TEXT,
            registered_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Price history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            good_id INTEGER,
            price REAL NOT NULL,
            recorded_date TEXT NOT NULL,
            market_condition TEXT,
            FOREIGN KEY (good_id) REFERENCES goods(good_id)
        )
    """)

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_goods_category ON goods(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_date ON trade_records(trade_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_type ON trade_records(trade_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_traders_type ON traders(trader_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(recorded_date)")

    conn.commit()
    print("✓ Tables created successfully")


def insert_sample_goods(conn):
    """Insert sample trade goods."""
    cursor = conn.cursor()

    goods = [
        # Furs (high value items)
        ("Beaver Pelt", "furs", 150, "pelt", 25.00, 28.50, "excellent", "Northern Territories", "Prime winter beaver, thick and lustrous"),
        ("Otter Fur", "furs", 80, "pelt", 18.00, 19.75, "good", "River Valleys", "River otter, waterproof and durable"),
        ("Fox Pelt", "furs", 45, "pelt", 12.00, 13.25, "good", "Forest Regions", "Red fox, soft and warm"),
        ("Mink Fur", "furs", 30, "pelt", 22.00, 24.00, "excellent", "Wetlands", "Mink fur, highly prized"),
        ("Rabbit Hide", "furs", 200, "hide", 2.50, 2.75, "fair", "Local Trapping", "Common rabbit, good for lining"),

        # Tools and Equipment
        ("Steel Trap", "tools", 25, "unit", 8.50, 9.00, "good", "Montreal", "Bear-sized steel leg trap"),
        ("Hunting Knife", "tools", 40, "unit", 5.00, 5.50, "excellent", "Sheffield", "High-carbon steel blade"),
        ("Axe Head", "tools", 15, "unit", 6.50, 7.00, "good", "Montreal", "Forged iron axe head"),
        ("Fish Hooks", "tools", 500, "dozen", 0.75, 0.80, "good", "England", "Barbed iron hooks"),
        ("Powder Horn", "tools", 12, "unit", 3.00, 3.25, "fair", "Local Craft", "Carved buffalo horn"),

        # Trade Goods and Supplies
        ("Glass Beads", "trade_goods", 50, "pound", 4.00, 4.50, "excellent", "Venice", "Colorful glass beads for trade"),
        ("Wool Blanket", "trade_goods", 35, "unit", 12.00, 13.00, "good", "England", "Heavy wool, point-marked"),
        ("Brass Kettle", "trade_goods", 20, "unit", 8.00, 8.75, "excellent", "Birmingham", "Riveted brass cooking pot"),
        ("Iron Nails", "trade_goods", 100, "pound", 0.50, 0.55, "good", "Montreal", "Forged iron nails"),
        ("Cotton Cloth", "trade_goods", 200, "yard", 1.50, 1.65, "good", "Manchester", "Sturdy cotton fabric"),

        # Provisions
        ("Pemmican", "provisions", 300, "pound", 0.75, 0.85, "good", "Fort Stores", "Dried meat and berry mixture"),
        ("Flour", "provisions", 500, "pound", 0.25, 0.28, "fair", "Red River", "Ground wheat flour"),
        ("Tea", "provisions", 25, "pound", 3.50, 4.00, "excellent", "China", "Black tea leaves"),
        ("Tobacco", "provisions", 40, "pound", 2.50, 2.75, "good", "Virginia", "Twist tobacco for trade"),
        ("Salt", "provisions", 100, "pound", 0.40, 0.45, "good", "Liverpool", "Sea salt for preservation"),
    ]

    cursor.executemany("""
        INSERT INTO goods (name, category, quantity, unit, base_price, current_price, quality, origin, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, goods)

    conn.commit()
    print(f"✓ Inserted {len(goods)} sample goods")


def insert_sample_traders(conn):
    """Insert sample traders."""
    cursor = conn.cursor()

    traders = [
        ("Jacques Dumont", "trapper", "excellent", 45, 1250.00, 150.00, "2024-11-01", "Reliable beaver trapper from Quebec"),
        ("Running Deer", "native_trader", "good", 32, 890.00, 100.00, "2024-10-28", "Cree trader, expert in local furs"),
        ("William McKenzie", "fort_trader", "excellent", 78, 3200.00, 500.00, "2024-11-05", "Senior trader, handles bulk orders"),
        ("Marie Beaumont", "merchant", "good", 23, 1100.00, 200.00, "2024-10-15", "French merchant from Montreal"),
        ("Black Hawk", "native_trader", "fair", 18, 450.00, 75.00, "2024-09-30", "Ojibwe trapper, seasonal visitor"),
        ("Thomas O'Brien", "trapper", "good", 29, 720.00, 125.00, "2024-11-10", "Irish trapper, works the northern lines"),
        ("Grey Wolf", "native_trader", "excellent", 56, 2100.00, 300.00, "2024-11-12", "Respected elder, fair dealer"),
        ("Pierre Lafleur", "trapper", "fair", 12, 380.00, 50.00, "2024-10-20", "Young trapper, learning the trade"),
    ]

    cursor.executemany("""
        INSERT INTO traders (name, trader_type, reputation, total_trades, total_value, credit_limit, last_trade_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, traders)

    conn.commit()
    print(f"✓ Inserted {len(traders)} sample traders")


def insert_sample_trades(conn):
    """Insert sample trade records."""
    cursor = conn.cursor()

    # Get some good and trader IDs
    cursor.execute("SELECT good_id FROM goods LIMIT 10")
    good_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT trader_id FROM traders LIMIT 5")
    trader_ids = [row[0] for row in cursor.fetchall()]

    trades = []
    base_date = datetime.now() - timedelta(days=30)

    for i in range(25):
        good_id = random.choice(good_ids)
        trader_id = random.choice(trader_ids)
        trade_type = random.choice(['buy', 'sell', 'exchange'])
        quantity = random.randint(5, 50)
        price_per_unit = round(random.uniform(1.0, 30.0), 2)
        total_value = round(quantity * price_per_unit, 2)
        trade_date = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        payment_method = random.choice(['cash', 'credit', 'barter', 'furs'])

        trades.append((
            good_id, trader_id, trade_type, quantity, price_per_unit,
            total_value, trade_date, payment_method, f"Trade #{i+1}"
        ))

    cursor.executemany("""
        INSERT INTO trade_records (good_id, trader_id, trade_type, quantity, price_per_unit, total_value, trade_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trades)

    conn.commit()
    print(f"✓ Inserted {len(trades)} sample trade records")


def insert_price_history(conn):
    """Insert sample price history data."""
    cursor = conn.cursor()

    cursor.execute("SELECT good_id, current_price FROM goods LIMIT 5")
    goods = cursor.fetchall()

    history = []
    base_date = datetime.now() - timedelta(days=90)

    for good_id, current_price in goods:
        for day in range(0, 90, 7):  # Weekly price records
            date = (base_date + timedelta(days=day)).strftime('%Y-%m-%d')
            # Price fluctuates ±20% from current
            price_variance = random.uniform(0.8, 1.2)
            price = round(current_price * price_variance, 2)
            market_condition = random.choice(['stable', 'rising', 'falling', 'volatile'])

            history.append((good_id, price, date, market_condition))

    cursor.executemany("""
        INSERT INTO price_history (good_id, price, recorded_date, market_condition)
        VALUES (?, ?, ?, ?)
    """, history)

    conn.commit()
    print(f"✓ Inserted {len(history)} price history records")


def main():
    """Main initialization function."""
    print(f"🏪 Initializing Trading Fort Database...")
    print(f"📂 Database path: {DB_PATH}")

    # Remove existing database for fresh start
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("✓ Removed existing database")

    # Create connection and initialize
    conn = sqlite3.connect(DB_PATH)

    try:
        create_tables(conn)
        insert_sample_goods(conn)
        insert_sample_traders(conn)
        insert_sample_trades(conn)
        insert_price_history(conn)

        # Print summary
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM goods")
        goods_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM traders")
        traders_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM trade_records")
        trades_count = cursor.fetchone()[0]

        print("\n" + "="*50)
        print("📊 Database Summary:")
        print(f"  - Trade Goods: {goods_count}")
        print(f"  - Registered Traders: {traders_count}")
        print(f"  - Trade Records: {trades_count}")
        print("="*50)
        print("\n✅ Trading Fort database initialized successfully!")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
