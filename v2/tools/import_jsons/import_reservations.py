import json
import sqlite3

RESERVATIONS_JSON = "./tools/import_jsons/data/reservations.json"

def _normalize_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s == "completed":
        return "completed"
    if s in {"cancelled", "canceled"}:
        return "canceled"
    # treat everything else as confirmed
    return "confirmed"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(RESERVATIONS_JSON, "r", encoding="utf-8") as f:
        reservations = json.load(f)

    def _vehicle_exists(veh_id: int) -> bool:
        cur.execute("SELECT 1 FROM vehicles WHERE vehicle_id = ? LIMIT 1", (veh_id,))
        return cur.fetchone() is not None

    def _lot_exists(lot_id: int) -> bool:
        cur.execute("SELECT 1 FROM parking_lots WHERE id = ? LIMIT 1", (lot_id,))
        return cur.fetchone() is not None

    def _get_vehicle_info(veh_id: int):
        cur.execute("SELECT user_id, license_plate FROM vehicles WHERE vehicle_id = ? LIMIT 1", (veh_id,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else (None, None)

    sql = """
        INSERT OR REPLACE INTO reservation
            (id, vehicles_id, parking_lots_id, start_time, end_time, cost, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        # Get start_time and end_time from the reservation data
        start_time = r.get("start_time", "")
        end_time = r.get("end_time", "")

        cost = float(r.get("cost", 0)) if r.get("cost") is not None else 0.0

        cur.execute(
            sql,
            (
                rid,
                veh_id,
                lot_id,
                start_time,
                end_time,
                cost,
                _normalize_status(r.get("status")),
                r.get("created_at") or start_time,
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
