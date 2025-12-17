import json
import sqlite3

PARKING_LOTS_JSON = "./tools/import_jsons/data/parking-lots.json"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(PARKING_LOTS_JSON, "r", encoding="utf-8") as f:
        lots_data = json.load(f)

    # parking-lots.json is an object keyed by id, so take the values
    lots = list(lots_data.values())

    sql = """
        INSERT OR REPLACE INTO parking_lots
            (lot_id, name, address, city, postal_code, latitude, longitude,
             total_capacity, available_spots, hourly_rate, daily_rate, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for lot in lots:
        coords = lot.get("coordinates", {})
        capacity = int(lot.get("capacity", 0))
        reserved = int(lot.get("reserved", 0))
        available = capacity - reserved if capacity >= reserved else capacity

        cur.execute(sql, (
            int(lot["id"]),
            lot["name"],
            lot.get("address", ""),
            lot.get("location", "Unknown"),  # Use location as city
            None,  # postal_code - not in source data
            coords.get("lat"),
            coords.get("lng"),
            capacity,
            available,
            float(lot.get("tariff")) if lot.get("tariff") is not None else 0.0,
            float(lot.get("daytariff")) if lot.get("daytariff") is not None else 0.0,
            1,  # is_active - default to true
            lot.get("created_at"),
        ))
        conn.commit()

    print(f"[parking_lots] imported {len(lots)} records (duplicates replaced)")
