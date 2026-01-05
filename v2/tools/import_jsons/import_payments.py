import json
import sqlite3
from datetime import datetime

PAYMENTS_JSON = "./tools/import_jsons/data/payments.json"


def _parse_datetime(date_str: str | None) -> str | None:
    """Payments timestamps are like '22-05-2025 09:09:1747898315'.
    We drop the trailing unix digits and keep day + hour:minute.
    """
    if not date_str:
        return None

    trimmed = date_str.strip()
    for fmt, slice_len in (("%d-%m-%Y %H:%M", 16), ("%d-%m-%Y %H:%M:%S", 19)):
        try:
            dt = datetime.strptime(trimmed[:slice_len], fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return None


def _get_user_id_by_username(cur: sqlite3.Cursor, username: str | None):
    if not username:
        return None
    cur.execute("SELECT id FROM users WHERE username = ? LIMIT 1", (username,))
    row = cur.fetchone()
    return row[0] if row else None


def _session_exists(cur: sqlite3.Cursor, session_id: int) -> bool:
    cur.execute("SELECT 1 FROM parking_sessions WHERE session_id = ? LIMIT 1", (session_id,))
    return cur.fetchone() is not None


def run(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    with open(PAYMENTS_JSON, "r", encoding="utf-8") as f:
        payments = json.load(f)

    sql = """
        INSERT OR REPLACE INTO payments
            (payment_id, user_id, session_id, reservation_id, amount, currency,
             payment_method, transaction_id, status, payment_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    inserted = skipped_user = skipped_session = 0
    for idx, p in enumerate(payments, start=1):
        user_id = _get_user_id_by_username(cur, p.get("initiator"))
        if not user_id:
            skipped_user += 1
            print(f"[payments] skip id={idx} (user '{p.get('initiator')}' not found)")
            continue

        session_id = p.get("session_id")
        if not session_id or not _session_exists(cur, session_id):
            skipped_session += 1
            print(f"[payments] skip id={idx} (session {session_id} missing)")
            continue

        t_data = p.get("t_data") or {}
        completed_at = _parse_datetime(p.get("completed"))

        # Determine status based on whether payment was completed
        status = "COMPLETED" if completed_at else "PENDING"

        # Convert amount from whatever format to float
        amount = float(p.get("amount", 0)) if p.get("amount") is not None else 0.0

        cur.execute(
            sql,
            (
                idx,
                user_id,
                int(session_id),
                None,  # reservation_id - not in source data
                amount,
                "EUR",  # currency - default
                t_data.get("method"),
                p.get("hash"),
                status,
                completed_at,
                _parse_datetime(p.get("created_at")),
            ),
        )
        inserted += 1

    conn.commit()
    total = len(payments)
    print(
        f"[payments] imported={inserted} "
        f"skipped_user={skipped_user} skipped_session={skipped_session} total={total}"
    )
