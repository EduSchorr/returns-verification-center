from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "returns.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
      CREATE TABLE IF NOT EXISTS cases(
        id INTEGER PRIMARY KEY,
        case_key TEXT NOT NULL UNIQUE,
        status TEXT NOT NULL,
        confidence REAL,
        source TEXT,
        details TEXT,
        updated_at TEXT NOT NULL
      )
    """)
    return conn

def upsert_case(case_key: str, status: str, confidence: float, source: str, details: str):
    now = datetime.now().isoformat(timespec="seconds")
    with connect() as conn:
        conn.execute(
            """INSERT INTO cases(case_key,status,confidence,source,details,updated_at)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(case_key) DO UPDATE SET
               status=excluded.status,confidence=excluded.confidence,
               source=excluded.source,details=excluded.details,updated_at=excluded.updated_at""",
            (case_key, status, confidence, source, details, now),
        )

def list_cases(limit=200):
    with connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM cases ORDER BY updated_at DESC LIMIT ?", (limit,))]
