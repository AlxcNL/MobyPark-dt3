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
