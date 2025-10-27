PRAGMA foreign_keys = ON;

-- users
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  email TEXT NOT NULL,
  phone TEXT,
  role TEXT NOT NULL CHECK (role IN ('user','admin')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  birth_year INTEGER,
  active INTEGER NOT NULL DEFAULT 1,
  UNIQUE(username),
  UNIQUE(email)
);

-- vehicles (cascade on user delete)
CREATE TABLE IF NOT EXISTS vehicles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  users_id INTEGER NOT NULL,
  license_plate_clean TEXT NOT NULL,
  license_plate TEXT NOT NULL,
  make TEXT,
  model TEXT,
  color TEXT,
  year INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (users_id) REFERENCES users (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE(license_plate_clean)
);
CREATE INDEX IF NOT EXISTS fk_Vehicles_Users_idx ON vehicles (users_id);

-- parking_lots
CREATE TABLE IF NOT EXISTS parking_lots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  location TEXT,
  address TEXT,
  capacity INTEGER NOT NULL CHECK (capacity >= 0),
  reserved INTEGER NOT NULL DEFAULT 0 CHECK (reserved >= 0 AND reserved <= capacity),
  tariff REAL,
  daytariff REAL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  latitude REAL,
  longitude REAL
);

-- sessions (cascade on lot/vehicle delete)
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parking_lots_id INTEGER NOT NULL,
  vehicles_id INTEGER NOT NULL,
  start_date TEXT NOT NULL,
  stop_date TEXT,
  duration_minutes INTEGER,
  cost REAL,
  payment_status TEXT NOT NULL CHECK (payment_status IN ('pending', 'completed')),
  FOREIGN KEY (parking_lots_id) REFERENCES parking_lots (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (vehicles_id) REFERENCES vehicles (id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX IF NOT EXISTS fk_sessions_parking_lots1_idx ON sessions (parking_lots_id);
CREATE INDEX IF NOT EXISTS fk_sessions_Vehicles1_idx ON sessions (vehicles_id);

-- reservation (cascade on lot/vehicle delete)
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
  FOREIGN KEY (vehicles_id) REFERENCES vehicles (id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX IF NOT EXISTS fk_reservation_parking_lots1_idx ON reservation (parking_lots_id);
CREATE INDEX IF NOT EXISTS fk_reservation_vehicles1_idx ON reservation (vehicles_id);

-- payments (cascade on user delete)
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
