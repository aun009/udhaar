"""SQLite ledger storage."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.config import DB_PATH


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db(path: Path | None = None) -> None:
    db = path or DB_PATH
    with connect(db) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                phone TEXT,
                dialect TEXT DEFAULT 'hindi',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL REFERENCES customers(id),
                amount INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('credit_given','payment_received')),
                note TEXT,
                raw_transcript TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_entries_customer ON entries(customer_id);
            """
        )


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    db = path or DB_PATH
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_customer(conn: sqlite3.Connection, name: str, phone: str | None = None, dialect: str = "hindi") -> int:
    row = conn.execute("SELECT id FROM customers WHERE name = ?", (name,)).fetchone()
    if row:
        return int(row["id"])
    cur = conn.execute(
        "INSERT INTO customers (name, phone, dialect, created_at) VALUES (?, ?, ?, ?)",
        (name, phone, dialect, _utc_now()),
    )
    return int(cur.lastrowid)


def insert_entry(
    conn: sqlite3.Connection,
    *,
    customer_id: int,
    amount: int,
    entry_type: str,
    note: str | None,
    raw_transcript: str | None,
) -> int:
    cur = conn.execute(
        """INSERT INTO entries (customer_id, amount, type, note, raw_transcript, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (customer_id, amount, entry_type, note, raw_transcript, _utc_now()),
    )
    return int(cur.lastrowid)


def customer_balance(conn: sqlite3.Connection, customer_id: int) -> int:
    row = conn.execute(
        """
        SELECT COALESCE(SUM(
            CASE WHEN type = 'credit_given' THEN amount ELSE -amount END
        ), 0) AS bal
        FROM entries WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()
    return int(row["bal"])


def list_customers(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT c.id, c.name, c.phone, c.dialect,
               COALESCE(SUM(CASE WHEN e.type='credit_given' THEN e.amount ELSE -e.amount END), 0) AS balance
        FROM customers c
        LEFT JOIN entries e ON e.customer_id = c.id
        GROUP BY c.id
        ORDER BY balance DESC, c.name
        """
    ).fetchall()
    return [dict(r) for r in rows]


def overdue_customers(conn: sqlite3.Connection, days: int) -> list[dict[str, Any]]:
    """Customers with positive balance whose oldest unpaid credit is older than N days."""
    rows = conn.execute(
        """
        WITH credits AS (
            SELECT customer_id, created_at,
                   SUM(amount) OVER (
                       PARTITION BY customer_id ORDER BY created_at, id
                   ) AS cumulative_credit
            FROM entries
            WHERE type = 'credit_given'
        ), payments AS (
            SELECT customer_id, COALESCE(SUM(amount), 0) AS total_paid
            FROM entries
            WHERE type = 'payment_received'
            GROUP BY customer_id
        ), balances AS (
            SELECT customer_id,
                   COALESCE(SUM(CASE WHEN type='credit_given' THEN amount ELSE -amount END), 0) AS balance
            FROM entries
            GROUP BY customer_id
        ), oldest_unpaid AS (
            SELECT cr.customer_id, MIN(cr.created_at) AS oldest_credit
            FROM credits cr
            LEFT JOIN payments p ON p.customer_id = cr.customer_id
            WHERE cr.cumulative_credit > COALESCE(p.total_paid, 0)
            GROUP BY cr.customer_id
        )
        SELECT c.id, c.name, c.phone, c.dialect, b.balance, o.oldest_credit
        FROM customers c
        JOIN balances b ON b.customer_id = c.id
        JOIN oldest_unpaid o ON o.customer_id = c.id
        WHERE b.balance > 0
          AND datetime(o.oldest_credit) <= datetime('now', ?)
        """
        , (f"-{days} days",)
    ).fetchall()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "phone": r["phone"],
            "dialect": r["dialect"],
            "balance": int(r["balance"]),
            "oldest_credit": r["oldest_credit"],
            "overdue_days": days,
        }
        for r in rows
    ]


def monthly_summary(conn: sqlite3.Connection) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    month_prefix = now.strftime("%Y-%m")
    total_out = conn.execute(
        """
        SELECT COALESCE(SUM(
            CASE WHEN type='credit_given' THEN amount ELSE -amount END
        ), 0) FROM entries
        """
    ).fetchone()[0]
    received = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0) FROM entries
        WHERE type='payment_received' AND created_at LIKE ?
        """,
        (f"{month_prefix}%",),
    ).fetchone()[0]
    top = conn.execute(
        """
        SELECT c.name,
               COALESCE(SUM(CASE WHEN e.type='credit_given' THEN e.amount ELSE -e.amount END), 0) AS balance
        FROM customers c
        LEFT JOIN entries e ON e.customer_id = c.id
        GROUP BY c.id
        HAVING balance > 0
        ORDER BY balance DESC
        LIMIT 5
        """
    ).fetchall()
    return {
        "total_outstanding": int(total_out),
        "received_this_month": int(received),
        "top_dues": [{"name": r["name"], "balance": int(r["balance"])} for r in top],
        "month": month_prefix,
    }
