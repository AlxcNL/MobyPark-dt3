import json
import sqlite3

SESSIONS_JSON = "./tools/import_jsons/data/p1-sessions.json"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(SESSIONS_JSON, "r", encoding="utf-8") as f:
        data_obj = json.load(f)

    sessions = list(data_obj.values())

    def _lot_exists(lot_id: int) -> bool:
        cur.execute("SELECT 1 FROM parking_lots WHERE lot_id = ? LIMIT 1", (lot_id,))
        return cur.fetchone() is not None

    def _get_lot_rate(lot_id: int) -> float:
        cur.execute("SELECT hourly_rate FROM parking_lots WHERE lot_id = ? LIMIT 1", (lot_id,))
        row = cur.fetchone()
        return row[0] if row else 0.0

    def _user_id_by_username(username: str | None):
        if not username:
            return None
        cur.execute("SELECT user_id FROM users WHERE username = ? LIMIT 1", (username,))
        row = cur.fetchone()
        return row[0] if row else None

    def _vehicle_id_by_plate(plate: str):
        if not plate:
            return None
        cur.execute("SELECT vehicle_id FROM vehicles WHERE license_plate = ? LIMIT 1", (plate,))
        row = cur.fetchone()
        return row[0] if row else None

    def _get_vehicle_info(veh_id: int):
        cur.execute("SELECT user_id, license_plate FROM vehicles WHERE vehicle_id = ? LIMIT 1", (veh_id,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else (None, None)

    def _create_vehicle(plate: str, username: str | None, created_at: str | None):
        if not plate:
            return None

        user_id = _user_id_by_username(username)
        if not user_id:
            return None

        cur.execute(
            """
            INSERT INTO vehicles
                (user_id, license_plate, vehicle_name, brand, model, color, is_active, created_at)
            VALUES (?, ?, NULL, NULL, NULL, NULL, 1, ?)
            """,
            (user_id, plate, created_at),
        )
        return cur.lastrowid

    sql = """
        INSERT OR REPLACE INTO parking_sessions
            (session_id, user_id, lot_id, vehicle_id, license_plate, start_time, end_time,
             duration_minutes, hourly_rate, calculated_amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = skipped = created_vehicles = 0
    for s in sessions:
        sid = int(s["id"])
        lot_id = int(s["parking_lot_id"]) if s.get("parking_lot_id") else None
        plate = (s.get("licenseplate") or "").strip()

        if not lot_id or not _lot_exists(lot_id):
            skipped += 1
            print(f"[sessions] skip id={sid} (missing parking_lots.lot_id={lot_id})")
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

        user_id, vehicle_plate = _get_vehicle_info(veh_id)
        if not user_id:
            skipped += 1
            print(f"[sessions] skip id={sid} (user not found for vehicle={veh_id})")
            continue

        # Determine status based on payment_status and whether session is stopped
        paystat = str(s.get("payment_status", "")).lower()
        has_stopped = s.get("stopped") is not None
        if has_stopped and paystat == "paid":
            status = "COMPLETED"
        elif has_stopped:
            status = "COMPLETED"  # Session ended but payment might be pending
        else:
            status = "ACTIVE"

        hourly_rate = _get_lot_rate(lot_id)
        cost = float(s.get("cost", 0)) if s.get("cost") is not None else 0.0

        cur.execute(sql, (
            sid,
            user_id,
            lot_id,
            veh_id,
            vehicle_plate,
            s.get("started"),
            s.get("stopped"),
            int(s.get("duration_minutes") or 0),
            hourly_rate,
            cost,
            status,
            s.get("started"),  # Use started as created_at
        ))
        inserted += 1

    conn.commit()
    print(f"[sessions] imported={inserted} skipped={skipped} vehicles_created={created_vehicles} total={len(sessions)}")
