#!/usr/bin/env python3
"""Load fake demo customers/entries for screenshots."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import DB_PATH
from app.db import connect, init_db, insert_entry, upsert_customer

DEMO = [
    ("Amit ji", "9876500001", "hindi", "credit_given", 340, "doodh ka packet"),
    ("Suresh bhai", "9876500002", "hindi", "credit_given", 250, None),
    ("Patil bhau", "9876500003", "marathi", "credit_given", 1500, "tel ki bottle"),
    ("Suresh bhai", None, "hindi", "payment_received", 200, None),
    ("Geeta tai", "9876500004", "hindi", "credit_given", 120, "sabun"),
]


def main() -> None:
    init_db(DB_PATH)
    with connect() as conn:
        for name, phone, dialect, etype, amount, note in DEMO:
            cid = upsert_customer(conn, name, phone, dialect)
            insert_entry(
                conn,
                customer_id=cid,
                amount=amount,
                entry_type=etype,
                note=note,
                raw_transcript=f"demo seed {name} {amount}",
            )
    print(f"Seeded demo data into {DB_PATH}")


if __name__ == "__main__":
    main()
