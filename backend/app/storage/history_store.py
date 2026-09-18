import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

DB_PATH = Path(__file__).parent.parent.parent/"data"/"history.db"

RiskLevel = Literal["low", "medium", "high"]
ResponseType = Literal["normal", "boundary", "crisis", "error"]

class HistoryEntry(TypedDict):
    id: int
    session_id: str
    user_message: str
    system_message: str
    response_type: ResponseType
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
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                system_message TEXT NOT NULL,
                response_type TEXT NOT NULL CHECK (response_type IN ('normal', 'boundary', 'crisis', 'error')),
                risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_session_id ON history(session_id)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                locked INTEGER NOT NULL DEFAULT 0,
                locked_at TEXT
            )
            """
        )


def add_entry(session_id: str, user_message: str, system_message: str, response_type: ResponseType, risk_level: RiskLevel) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO history (session_id, user_message, system_message, response_type, risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_message, system_message, response_type, risk_level, datetime.now(timezone.utc).isoformat()),
        )

def get_history(session_id: str) -> list[HistoryEntry]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, session_id, user_message, system_message, response_type, risk_level, created_at
            FROM history
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        ).fetchall()
        return [dict(row) for row in rows]
def delete_history(session_id: str) -> int:
    with get_connection() as conn:
        rows = conn.execute(
            "DELETE FROM history WHERE session_id = ?",
            (session_id,),
        )
        conn.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        return rows.rowcount

# Session lock function, treats the session as terminated regardless of frontend local state
def set_session_locked(session_id: str, locked: bool = True) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, locked, locked_at)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                locked = excluded.locked,
                locked_at = excluded.locked_at
            """,
            (
                session_id,
                1 if locked else 0,
                datetime.now(timezone.utc).isoformat() if locked else None,
            ),
        )
# Check if session locked, returns True if locked, False if unlocked or not found
def is_session_locked(session_id: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT locked FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return bool(row["locked"]) if row else False
# TODO: possible to perform foregin key to cross show which message specifically