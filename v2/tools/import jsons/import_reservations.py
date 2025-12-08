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
