import json
import sqlite3

RESERVATIONS_JSON = "./tools/import jsons/data/reservations.json"

def _cents(value) -> int:
    if value in (None, ""):
        return 0
    return int(round(float(value) * 100))

def _normalize_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "completed":
        return "completed"
    if s in {"cancelled", "canceled"}:
        return "canceled"
    # treat "pending" (and everything else) as confirmed
    return "confirmed"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(RESERVATIONS_JSON, "r", encoding="utf-8") as f:   
        reservations = json.load(f)

    def _vehicle_exists(veh_id: int) -> bool:
        cur.execute("SELECT 1 FROM vehicles WHERE id = ? LIMIT 1", (veh_id,))
        return cur.fetchone() is not None

    def _lot_exists(lot_id: int) -> bool:
        cur.execute("SELECT 1 FROM parking_lots WHERE id = ? LIMIT 1", (lot_id,))
        return cur.fetchone() is not None

    sql = """
        INSERT OR REPLACE INTO reservation
            (id, vehicless_id, parking_lots_id, start_time, end_time, status, created_at, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

