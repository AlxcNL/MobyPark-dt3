import json
import sqlite3

USERS_JSON = "./tools/import_jsons/data/users.json"

def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(USERS_JSON, "r", encoding="utf-8") as f:
        users = json.load(f)

    sql = """
        INSERT OR REPLACE INTO users
            (id, username, email, password_hash, name, phone, birth_year, role, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for u in users:
        cur.execute(sql, (
            int(u["id"]),
            u["username"],
            u["email"],
            u["password"],
            u["name"],
            u.get("phone"),
            u.get("birth_year", 1990),
            u["role"].upper(),
            1 if u.get("active", True) else 0,
            u.get("created_at"),
        ))
        conn.commit()

    print(f"[users] imported {len(users)} records")
