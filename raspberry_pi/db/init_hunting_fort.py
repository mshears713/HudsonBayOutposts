"""
Database Initialization Script for Hunting Fort

This script creates and populates the Hunting Fort database with tables and sample data.

Educational Note:
This demonstrates database schema design for a hunting management system,
including wildlife tracking, hunting parties, pelt harvests, and seasonal reports.

To run:
    python raspberry_pi/db/init_hunting_fort.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random

# Database file path
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "hunting_fort.db"


def create_database():
    """
    Create the Hunting Fort database and tables.

    Educational Note:
    This function demonstrates:
    - Creating related tables with foreign keys
    - Proper data types and constraints
    - Indexes for performance
    """
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Remove existing database if it exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed existing database: {DB_PATH}")

    # Create new database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Creating Hunting Fort database...")

    # ========================================================================
    # Create Tables
    # ========================================================================

    # Game animals table
    cursor.execute("""
        CREATE TABLE game_animals (
            animal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            species TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('big_game', 'small_game', 'fur_bearer', 'waterfowl')),
            typical_size TEXT NOT NULL,
            pelt_value REAL,
            meat_yield TEXT,
            population_status TEXT NOT NULL CHECK(population_status IN ('abundant', 'common', 'fair', 'scarce', 'protected')),
            best_season TEXT NOT NULL,
            habitat TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created game_animals table")

    # Hunting parties table
    cursor.execute("""
        CREATE TABLE hunting_parties (
            party_id INTEGER PRIMARY KEY AUTOINCREMENT,
            leader_name TEXT NOT NULL,
            party_size INTEGER NOT NULL CHECK(party_size >= 1 AND party_size <= 20),
            start_date DATE NOT NULL,
            end_date DATE,
            status TEXT NOT NULL CHECK(status IN ('planning', 'active', 'completed', 'cancelled')),
            target_species TEXT,
            region TEXT,
            total_harvest INTEGER DEFAULT 0,
            success_rate REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created hunting_parties table")

    # Pelt harvests table
    cursor.execute("""
        CREATE TABLE pelt_harvests (
            harvest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            party_id INTEGER NOT NULL,
            species TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 1),
            quality TEXT NOT NULL CHECK(quality IN ('poor', 'fair', 'good', 'prime', 'exceptional')),
            date_harvested DATE NOT NULL,
            estimated_value REAL NOT NULL CHECK(estimated_value >= 0),
            condition TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (party_id) REFERENCES hunting_parties(party_id)
        )
    """)
    print("✓ Created pelt_harvests table")

    # Seasonal reports table
    cursor.execute("""
        CREATE TABLE seasonal_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT NOT NULL,
            year INTEGER NOT NULL,
            total_parties INTEGER DEFAULT 0,
            total_hunters INTEGER DEFAULT 0,
            total_pelts INTEGER DEFAULT 0,
            total_value REAL DEFAULT 0.0,
            top_species TEXT,
            weather_conditions TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created seasonal_reports table")

    # ========================================================================
    # Create Indexes
    # ========================================================================

    cursor.execute("CREATE INDEX idx_animals_category ON game_animals(category)")
    cursor.execute("CREATE INDEX idx_animals_status ON game_animals(population_status)")
    cursor.execute("CREATE INDEX idx_parties_status ON hunting_parties(status)")
    cursor.execute("CREATE INDEX idx_parties_date ON hunting_parties(start_date)")
    cursor.execute("CREATE INDEX idx_harvests_species ON pelt_harvests(species)")
    cursor.execute("CREATE INDEX idx_harvests_date ON pelt_harvests(date_harvested)")
    cursor.execute("CREATE INDEX idx_reports_year ON seasonal_reports(year)")
    print("✓ Created indexes")

    conn.commit()
    return conn


def populate_sample_data(conn):
    """
    Populate the database with educational sample data.

    Educational Note:
    This creates realistic hunting fort data to demonstrate API capabilities
    and provide context for learning.
    """
    cursor = conn.cursor()

    print("\nPopulating sample data...")

    # ========================================================================
    # Game Animals (Wildlife tracked by the fort)
    # ========================================================================

    game_animals = [
        # Fur bearers
        ("Beaver", "fur_bearer", "15-30 kg", 25.00, "N/A", "abundant", "Fall/Winter", "Rivers, streams, wetlands", "Primary fur trade species"),
        ("Muskrat", "fur_bearer", "1-2 kg", 3.50, "N/A", "abundant", "Fall/Winter", "Marshes, ponds", "Common small fur bearer"),
        ("River Otter", "fur_bearer", "5-15 kg", 35.00, "N/A", "common", "Winter", "Rivers, lakes", "Prized for soft fur"),
        ("Mink", "fur_bearer", "1-3 kg", 18.00, "N/A", "common", "Winter", "Waterways", "Valuable dark fur"),
        ("Red Fox", "fur_bearer", "4-7 kg", 22.00, "N/A", "common", "Winter", "Forests, fields", "Popular for red coat"),
        ("Lynx", "fur_bearer", "8-18 kg", 45.00, "N/A", "fair", "Winter", "Boreal forest", "Rare, luxurious fur"),
        ("Wolf", "fur_bearer", "30-80 kg", 15.00, "N/A", "fair", "Winter", "Forest territories", "Difficult to trap"),

        # Big game
        ("Moose", "big_game", "400-600 kg", 50.00, "200-400 kg", "common", "Fall/Winter", "Boreal forest, wetlands", "Largest game animal"),
        ("White-tailed Deer", "big_game", "60-130 kg", 30.00, "30-60 kg", "abundant", "Fall/Winter", "Forest edges, fields", "Common game"),
        ("Caribou", "big_game", "90-210 kg", 40.00, "50-100 kg", "common", "Fall/Winter", "Tundra, boreal forest", "Migratory herds"),
        ("Black Bear", "big_game", "90-270 kg", 60.00, "40-80 kg", "common", "Spring/Fall", "Forests", "Valuable pelt and meat"),

        # Small game
        ("Snowshoe Hare", "small_game", "1.5-2 kg", 1.50, "0.5 kg", "abundant", "All seasons", "Forests", "Food and fur"),
        ("Porcupine", "small_game", "5-12 kg", 5.00, "3-5 kg", "common", "All seasons", "Forests", "Quills used for decoration"),
        ("Raccoon", "small_game", "5-12 kg", 8.00, "N/A", "common", "Fall/Winter", "Forests near water", "Thick winter coat"),

        # Waterfowl
        ("Canada Goose", "waterfowl", "3-7 kg", 2.00, "2-4 kg", "abundant", "Spring/Fall", "Lakes, wetlands", "Seasonal migration"),
        ("Mallard Duck", "waterfowl", "1-1.5 kg", 1.00, "0.5 kg", "abundant", "Spring/Fall", "Ponds, marshes", "Common waterfowl"),
    ]

    cursor.executemany("""
        INSERT INTO game_animals
        (species, category, typical_size, pelt_value, meat_yield, population_status, best_season, habitat, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, game_animals)
    print(f"✓ Inserted {len(game_animals)} game animals")

    # ========================================================================
    # Hunting Parties
    # ========================================================================

    # Generate hunting parties over the past 6 months
    base_date = datetime.now() - timedelta(days=180)

    leaders = [
        "Jean-Baptiste Lafleur", "Thomas Mackenzie", "Pierre Dubois",
        "William Campbell", "Jacques Beaumont", "Robert Fraser",
        "Antoine Leclerc", "Duncan McDonald", "Henri Rousseau",
        "James Stewart", "François Mercier", "Alexander Ross"
    ]

    regions = [
        "North Creek Territory", "Pine Ridge District", "Beaver Meadows",
        "Whispering Pines", "Thunder Lake Region", "Wolf Creek Valley",
        "Moose Mountain", "Silver River Basin"
    ]

    target_species_list = ["Beaver", "Muskrat", "Fox", "Lynx", "Moose", "Deer", "Mixed"]

    parties = []
    for i in range(25):
        start = base_date + timedelta(days=random.randint(0, 160))
        duration = random.randint(3, 21)
        end = start + timedelta(days=duration)

        # Most parties are completed, some are active
        if i < 22:
            status = "completed"
        elif i < 24:
            status = "active"
            end = None
        else:
            status = "planning"
            end = None

        party_size = random.randint(2, 8)
        target = random.choice(target_species_list)
        region = random.choice(regions)
        harvest = random.randint(5, 50) if status == "completed" else random.randint(0, 15) if status == "active" else 0
        success = round(random.uniform(40, 95), 1) if status == "completed" else None

        parties.append((
            random.choice(leaders),
            party_size,
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d") if end else None,
            status,
            target,
            region,
            harvest,
            success,
            f"Party targeting {target} in {region}"
        ))

    cursor.executemany("""
        INSERT INTO hunting_parties
        (leader_name, party_size, start_date, end_date, status, target_species, region, total_harvest, success_rate, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, parties)
    print(f"✓ Inserted {len(parties)} hunting parties")

    # ========================================================================
    # Pelt Harvests
    # ========================================================================

    qualities = ["poor", "fair", "good", "prime", "exceptional"]
    quality_multipliers = {"poor": 0.5, "fair": 0.75, "good": 1.0, "prime": 1.4, "exceptional": 2.0}

    harvests = []

    # Get completed parties
    completed_parties = cursor.execute("""
        SELECT party_id, start_date, end_date, target_species
        FROM hunting_parties
        WHERE status = 'completed'
    """).fetchall()

    for party in completed_parties:
        party_id, start_date, end_date, target = party

        # Get pelt value for target species
        if target and target != "Mixed":
            species_data = cursor.execute(
                "SELECT pelt_value FROM game_animals WHERE species = ?",
                (target,)
            ).fetchone()

            if species_data:
                base_value = species_data[0]

                # Generate 1-5 harvest records per party
                num_harvests = random.randint(1, 5)
                for _ in range(num_harvests):
                    quantity = random.randint(1, 8)
                    quality = random.choice(qualities)
                    multiplier = quality_multipliers[quality]
                    value = round(base_value * quantity * multiplier, 2)

                    # Random date during the hunt
                    days_range = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
                    harvest_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=random.randint(0, max(1, days_range)))

                    harvests.append((
                        party_id,
                        target,
                        quantity,
                        quality,
                        harvest_date.strftime("%Y-%m-%d"),
                        value,
                        f"{quality.capitalize()} quality pelts"
                    ))

    cursor.executemany("""
        INSERT INTO pelt_harvests
        (party_id, species, quantity, quality, date_harvested, estimated_value, condition)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, harvests)
    print(f"✓ Inserted {len(harvests)} pelt harvests")

    # ========================================================================
    # Seasonal Reports
    # ========================================================================

    seasons = [
        ("Winter 2024", 2024, 18, 82, 412, 9850.50, "Beaver", "Cold and clear, excellent trapping conditions"),
        ("Spring 2024", 2024, 12, 56, 245, 5240.75, "Muskrat", "Mild spring, good water levels"),
        ("Summer 2024", 2024, 8, 38, 156, 3120.00, "Mixed", "Warm summer, limited activity"),
        ("Fall 2024", 2024, 15, 68, 328, 7650.25, "Beaver", "Early freeze, prime pelts"),
        ("Winter 2025", 2025, 22, 98, 489, 11250.00, "Fox", "Harsh winter, excellent fur quality"),
    ]

    cursor.executemany("""
        INSERT INTO seasonal_reports
        (season, year, total_parties, total_hunters, total_pelts, total_value, top_species, weather_conditions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, seasons)
    print(f"✓ Inserted {len(seasons)} seasonal reports")

    conn.commit()


def verify_database(conn):
    """Verify the database was created correctly."""
    cursor = conn.cursor()

    print("\nVerifying database...")

    tables = ["game_animals", "hunting_parties", "pelt_harvests", "seasonal_reports"]

    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} records")

    print("\n✓ Database verification complete!")


def main():
    """Main execution function."""
    print("="*70)
    print("Hudson Bay Hunting Fort Database Initialization")
    print("="*70)

    try:
        # Create database and tables
        conn = create_database()

        # Populate with sample data
        populate_sample_data(conn)

        # Verify
        verify_database(conn)

        # Close connection
        conn.close()

        print("\n" + "="*70)
        print(f"✓ SUCCESS: Database created at {DB_PATH}")
        print("="*70)
        print("\nYou can now start the API with:")
        print("  uvicorn raspberry_pi.api.hunting_fort:app --host 0.0.0.0 --port 8002 --reload")
        print("\nOr access the database directly:")
        print(f"  sqlite3 {DB_PATH}")
        print("="*70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
