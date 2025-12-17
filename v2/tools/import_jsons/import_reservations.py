import json
import sqlite3

RESERVATIONS_JSON = "./tools/import_jsons/data/reservations.json"

def _normalize_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "completed":
        return "COMPLETED"
    if s in {"cancelled", "canceled"}:
        return "CANCELLED"
    if s == "active":
        return "ACTIVE"
    if s == "pending":
        return "PENDING"
    # treat everything else as confirmed
    return "CONFIRMED"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(RESERVATIONS_JSON, "r", encoding="utf-8") as f:
        reservations = json.load(f)

    def _vehicle_exists(veh_id: int) -> bool:
        cur.execute("SELECT 1 FROM vehicles WHERE vehicle_id = ? LIMIT 1", (veh_id,))
        return cur.fetchone() is not None

    def _lot_exists(lot_id: int) -> bool:
        cur.execute("SELECT 1 FROM parking_lots WHERE lot_id = ? LIMIT 1", (lot_id,))
        return cur.fetchone() is not None

    def _get_vehicle_info(veh_id: int):
        cur.execute("SELECT user_id, license_plate FROM vehicles WHERE vehicle_id = ? LIMIT 1", (veh_id,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else (None, None)

    sql = """
        INSERT OR REPLACE INTO reservations
            (reservation_id, user_id, lot_id, vehicle_id, license_plate,
             start_date, end_date, start_time, end_time, total_amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted, skipped_vehicle, skipped_lot = 0, 0, 0
    for r in reservations:
        rid = int(r["id"])
        veh_id = int(r.get("vehicle_id") or 0)
        lot_id = int(r.get("parking_lot_id") or 0)

        if not veh_id or not _vehicle_exists(veh_id):
            skipped_vehicle += 1
            print(f"[reservations] skip id={rid} (vehicle {veh_id} missing)")
            continue

        if not lot_id or not _lot_exists(lot_id):
            skipped_lot += 1
            print(f"[reservations] skip id={rid} (parking_lot {lot_id} missing)")
            continue

        user_id, license_plate = _get_vehicle_info(veh_id)
        if not user_id:
            skipped_vehicle += 1
            print(f"[reservations] skip id={rid} (user not found for vehicle={veh_id})")
            continue

        # Parse start_time and end_time if they contain both date and time
        start_datetime = r.get("start_time", "")
        end_datetime = r.get("end_time", "")

        # Try to split datetime into date and time parts
        start_date = start_datetime.split("T")[0] if "T" in start_datetime else start_datetime.split(" ")[0]
        start_time = start_datetime.split("T")[1] if "T" in start_datetime else None
        end_date = end_datetime.split("T")[0] if "T" in end_datetime else end_datetime.split(" ")[0]
        end_time = end_datetime.split("T")[1] if "T" in end_datetime else None

        cost = float(r.get("cost", 0)) if r.get("cost") is not None else 0.0

        cur.execute(
            sql,
            (
                rid,
                user_id,
                lot_id,
                veh_id,
                license_plate,
                start_date,
                end_date,
                start_time,
                end_time,
                cost,
                _normalize_status(r.get("status")),
                r.get("created_at") or start_datetime,
            ),
        )
        inserted += 1

    conn.commit()
    total = len(reservations)
    skipped = skipped_vehicle + skipped_lot
    print(
        f"[reservations] imported={inserted} "
        f"skipped_vehicle={skipped_vehicle} skipped_lot={skipped_lot} total={total}"
    )
