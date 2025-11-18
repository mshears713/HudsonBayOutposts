-- Fishing Fort Database Schema
--
-- This schema represents a frontier fishing outpost with thematic inventory,
-- catch records, and equipment tracking. The data model supports the educational
-- goals of teaching database design and API development.
--
-- Educational Note:
-- SQLite uses a simplified type system. Common types include:
-- - INTEGER: whole numbers
-- - REAL: floating-point numbers
-- - TEXT: strings
-- - BLOB: binary data

-- Drop existing tables if they exist (for fresh initialization)
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS catch_records;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS weather_log;

-- Inventory Table: Tracks general supplies at the fishing outpost
CREATE TABLE inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,  -- e.g., 'food', 'tools', 'supplies'
    quantity INTEGER NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,  -- e.g., 'pounds', 'pieces', 'barrels'
    value REAL NOT NULL DEFAULT 0.0,  -- Value in frontier currency
    description TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catch Records: Tracks fish caught over time
CREATE TABLE catch_records (
    catch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fish_type TEXT NOT NULL,  -- e.g., 'salmon', 'trout', 'pike'
    quantity INTEGER NOT NULL,
    weight_pounds REAL NOT NULL,
    catch_date DATE NOT NULL,
    location TEXT,  -- Fishing location description
    fisher_name TEXT,
    quality TEXT CHECK(quality IN ('poor', 'fair', 'good', 'excellent')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Equipment: Tracks fishing equipment and its condition
CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,  -- e.g., 'net', 'rod', 'boat', 'trap'
    condition TEXT CHECK(condition IN ('broken', 'poor', 'fair', 'good', 'excellent')),
    quantity INTEGER NOT NULL DEFAULT 1,
    last_maintained DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather Log: Tracks weather conditions affecting fishing
CREATE TABLE weather_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE NOT NULL,
    temperature_f REAL,
    conditions TEXT,  -- e.g., 'sunny', 'cloudy', 'rainy', 'stormy'
    wind_speed TEXT,  -- e.g., 'calm', 'moderate', 'strong'
    ice_coverage TEXT CHECK(ice_coverage IN ('none', 'partial', 'full')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_inventory_category ON inventory(category);
CREATE INDEX idx_catch_records_date ON catch_records(catch_date);
CREATE INDEX idx_catch_records_type ON catch_records(fish_type);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_weather_log_date ON weather_log(log_date);

-- Insert sample data for educational purposes
INSERT INTO inventory (name, category, quantity, unit, value, description) VALUES
    ('Salted Fish', 'food', 150, 'pounds', 75.0, 'Preserved salmon for winter storage'),
    ('Fishing Line', 'supplies', 500, 'feet', 25.0, 'Braided hemp line'),
    ('Salt Barrels', 'supplies', 12, 'barrels', 120.0, 'For preserving catches'),
    ('Dried Meat', 'food', 80, 'pounds', 60.0, 'Emergency rations'),
    ('Hooks', 'tools', 200, 'pieces', 40.0, 'Iron fishing hooks'),
    ('Nets', 'tools', 6, 'pieces', 180.0, 'Large fishing nets'),
    ('Flour', 'food', 100, 'pounds', 50.0, 'For making bannock'),
    ('Tea', 'food', 20, 'pounds', 30.0, 'Black tea leaves'),
    ('Rope', 'supplies', 300, 'feet', 45.0, 'Heavy duty rope'),
    ('Candles', 'supplies', 50, 'pieces', 15.0, 'Tallow candles');

INSERT INTO catch_records (fish_type, quantity, weight_pounds, catch_date, location, fisher_name, quality, notes) VALUES
    ('Salmon', 45, 180.5, '2024-11-15', 'North River Bend', 'Jacques Dubois', 'excellent', 'Large run, very fresh'),
    ('Trout', 23, 34.2, '2024-11-15', 'East Creek', 'William McKenzie', 'good', 'Smaller than usual'),
    ('Pike', 8, 56.3, '2024-11-14', 'Deep Lake', 'Marie Laporte', 'excellent', 'Trophy catch'),
    ('Salmon', 67, 268.0, '2024-11-14', 'North River Bend', 'Jacques Dubois', 'good', 'Standard autumn run'),
    ('Whitefish', 102, 153.0, '2024-11-13', 'South Bay', 'Thomas Greene', 'fair', 'Some freezer burn'),
    ('Trout', 31, 46.5, '2024-11-13', 'East Creek', 'William McKenzie', 'good', 'Consistent catches'),
    ('Pike', 5, 42.1, '2024-11-12', 'Deep Lake', 'Marie Laporte', 'poor', 'Old ice damage'),
    ('Salmon', 89, 356.0, '2024-11-12', 'North River Bend', 'Jacques Dubois', 'excellent', 'Peak season'),
    ('Sturgeon', 2, 78.5, '2024-11-11', 'Main Channel', 'Jean Baptiste', 'excellent', 'Rare catch!'),
    ('Whitefish', 124, 186.0, '2024-11-10', 'South Bay', 'Thomas Greene', 'good', 'School located');

INSERT INTO equipment (name, equipment_type, condition, quantity, last_maintained, notes) VALUES
    ('Large Seine Net', 'net', 'good', 2, '2024-11-01', 'Need minor repairs by spring'),
    ('Fishing Rods', 'rod', 'excellent', 8, '2024-10-15', 'Recently crafted'),
    ('Canoe - Birchbark', 'boat', 'fair', 3, '2024-09-20', 'Requires pitch repairs'),
    ('Fish Traps', 'trap', 'good', 12, '2024-11-05', 'Willow construction, holding well'),
    ('Ice Auger', 'tool', 'excellent', 2, '2024-10-01', 'Sharpened and ready for winter'),
    ('Gill Nets', 'net', 'good', 5, '2024-10-20', 'Standard maintenance'),
    ('Spears', 'tool', 'fair', 6, '2024-08-15', 'Iron tips need re-forging'),
    ('Storage Canoe', 'boat', 'poor', 1, '2024-06-10', 'Needs major repairs or replacement'),
    ('Hand Lines', 'line', 'excellent', 20, '2024-11-01', 'Fresh line stock');

INSERT INTO weather_log (log_date, temperature_f, conditions, wind_speed, ice_coverage, notes) VALUES
    ('2024-11-15', 28.5, 'partly cloudy', 'calm', 'none', 'Good fishing weather'),
    ('2024-11-14', 32.0, 'cloudy', 'moderate', 'none', 'Light snow in afternoon'),
    ('2024-11-13', 25.3, 'clear', 'calm', 'partial', 'Ice forming on edges'),
    ('2024-11-12', 30.2, 'sunny', 'moderate', 'partial', 'Excellent visibility'),
    ('2024-11-11', 22.0, 'overcast', 'strong', 'partial', 'Difficult fishing conditions'),
    ('2024-11-10', 35.5, 'rainy', 'moderate', 'none', 'Last rain before freeze'),
    ('2024-11-09', 38.0, 'cloudy', 'calm', 'none', 'Warm front moving through'),
    ('2024-11-08', 27.8, 'clear', 'calm', 'none', 'Perfect autumn day');
