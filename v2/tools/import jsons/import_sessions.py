import json
import re
import sqlite3

SESSIONS_JSON = "./tools/import jsons/data/pdata/p1-sessions.json"

def _lpclean(plate: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", plate).upper()

def _cents(euros) -> int:
    return int(round(float(euros) * 100)) if euros is not None else 0

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(SESSIONS_JSON, "r", encoding="utf-8") as f:
        data_obj = json.load(f)

    sessions = list(data_obj.values())

    def _lot_exists(lot_id: int) -> bool:
        cur.execute("SELECT 1 FROM parking_lots WHERE id = ? LIMIT 1", (lot_id,))
        return cur.fetchone() is not None

    def _user_id_by_username(username: str | None):
        if not username:
            return None
        cur.execute("SELECT id FROM users WHERE username = ? LIMIT 1", (username,))
        row = cur.fetchone()
        return row[0] if row else None

    def _vehicle_id_by_plate(plate: str):
        lp_clean = _lpclean(plate)
        if not lp_clean:
            return None
        cur.execute("SELECT id FROM vehicles WHERE license_plate_clean = ? LIMIT 1", (lp_clean,))
        row = cur.fetchone()
        return row[0] if row else None

    def _create_vehicle(plate: str, username: str | None, created_at: str | None):
        lp_clean = _lpclean(plate)
        if not lp_clean:
            return None

        user_id = _user_id_by_username(username)
        if not user_id:
            return None

        cur.execute(
            """
            INSERT INTO vehicles
                (users_id, license_plate_clean, license_plate, make, model, color, year, created_at)
            VALUES (?, ?, ?, NULL, NULL, NULL, NULL, ?)
            """,
            (user_id, lp_clean, plate, created_at),
        )
        return cur.lastrowid

    inserted = skipped = created_vehicles = 0

    for s in sessions:
        sid = int(s["id"])
        lot_id = int(s["parking_lot_id"]) if s.get("parking_lot_id") else None
        plate = (s.get("licenseplate") or "").strip()

        if not lot_id or not _lot_exists(lot_id):
            skipped += 1
            print(f"[sessions] skip id={sid} (missing parking_lots.id={lot_id})")
            continue

        veh_id = _vehicle_id_by_plate(plate)
        if not veh_id:
            veh_id = _create_vehicle(plate, s.get("user"), s.get("started"))
            if veh_id:
                created_vehicles += 1

        if not veh_id:
            skipped += 1
            print(f"[sessions] skip id={sid} (vehicle not found for plate={plate})")
            continue
