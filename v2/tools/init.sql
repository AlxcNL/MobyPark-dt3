-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'USER' CHECK(role IN ('USER', 'ADMIN')),
    active BOOLEAN DEFAULT TRUE,
    business_id INTEGER NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create parking_lots table
CREATE TABLE IF NOT EXISTS parking_lots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT,
    latitude REAL,
    longitude REAL,
    total_capacity INTEGER NOT NULL,
    available_spots INTEGER NOT NULL,
    hourly_rate REAL NOT NULL,
    daily_rate REAL NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    business_id INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    license_plate TEXT UNIQUE NOT NULL,
    vehicle_name TEXT,
    brand TEXT,
    model TEXT,
    color TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create parking_sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parking_lots_id INTEGER NOT NULL,
    vehicle_id INTEGER NULL,
    license_plate TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NULL,
    duration_minutes INTEGER,
    hourly_rate REAL NOT NULL DEFAULT 0.00,
    calculated_amount REAL DEFAULT 0.00,
    status TEXT DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parking_lots_id) REFERENCES parking_lots(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE SET NULL
);

    -- Create reservations table
    CREATE TABLE IF NOT EXISTS reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicles_id INTEGER NOT NULL,
    parking_lots_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL CHECK (status IN ('confirmed', 'completed', 'canceled')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    cost REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (parking_lots_id) REFERENCES parking_lots (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (vehicles_id) REFERENCES vehicles (vehicle_id)
        ON DELETE CASCADE ON UPDATE CASCADE
    );
    CREATE INDEX IF NOT EXISTS fk_reservation_parking_lots1_idx ON reservation (parking_lots_id);
    CREATE INDEX IF NOT EXISTS fk_reservation_vehicles1_idx ON reservation (vehicles_id);

-- Create payments table
    CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    sessions_id INTEGER NOT NULL,
    initiator_users_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    hash TEXT,
    method TEXT,
    issuer TEXT,
    bank TEXT,
    FOREIGN KEY (initiator_users_id) REFERENCES users (id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (sessions_id) REFERENCES sessions (id)
        ON DELETE SET NULL ON UPDATE CASCADE
    );
    CREATE INDEX IF NOT EXISTS fk_payments_users1_idx ON payments (initiator_users_id);
    CREATE INDEX IF NOT EXISTS fk_payments_sessions1_idx ON payments (sessions_id);


CREATE TABLE businesses (
	business_id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
    address TEXT, 
	PRIMARY KEY (business_id)
);

-- -- Insert sample data
-- -- Default admin user
-- INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, role, business_id) VALUES
-- (1, 'admin', 'admin@mobypark.com', 'admin123', 'Administrator', 'ADMIN', NULL),
-- (2, 'testuser', 'test@mobypark.com', 'password123', 'Test User', 'USER', NULL),
-- (3, 'ertu', 'test@ertu.nl','test123', 'ertu', 'ADMIN', NULL);

-- -- Sample parking lots
-- INSERT OR IGNORE INTO parking_lots (name, address, city, total_capacity, available_spots, hourly_rate, daily_rate) VALUES
-- ('Central Station Parking', 'Stationsplein 1', 'Amsterdam', 200, 200, 3.50, 25.00),
-- ('Airport Parking P1', 'Schiphol Airport', 'Amsterdam', 500, 500, 4.00, 30.00),
-- ('City Center Mall', 'Dam Square 10', 'Amsterdam', 150, 150, 2.50, 20.00),
-- ('Rotterdam Centraal', 'Stationsplein 1', 'Rotterdam', 300, 300, 3.00, 22.00),
-- ('Utrecht CS Parking', 'Stationsplein 14', 'Utrecht', 250, 250, 3.25, 24.00);

-- -- Sample vehicles
-- INSERT OR IGNORE INTO vehicles (user_id, license_plate, vehicle_name, brand, model, color) VALUES
-- (2, '12-ABC-3', 'My Car', 'Toyota', 'Corolla', 'Blue'),
-- (2, '45-DEF-6', 'Work Van', 'Ford', 'Transit', 'White');

-- -- Create user and hotel
-- INSERT OR IGNORE INTO users (id, username, email, password_hash, full_name, role, business_id) VALUES
-- (3, 'hotel_user', 'test2@mobypark.com', 'password1234', 'Test User', 'USER', NULL);

-- INSERT OR IGNORE INTO businesses (business_id, name, address) VALUES
-- (1, 'hotel1', 'Naamlaan 156');
