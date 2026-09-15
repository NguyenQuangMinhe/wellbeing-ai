import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

DB_PATH = Path(__file__).parent.parent.parent/"data"/"history.db"

RiskLevel = Literal["low", "medium", "high"]

class HistoryEntry(TypedDict):
    id: int
    session_id: str
    role: str
    message: str
    risk_level: RiskLevel
    created_at: str

@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'system')),
                message TEXT NOT NULL,
                risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_session_id ON history(session_id)"
        )