import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, TypedDict

DB_PATH = Path(__file__).parent.parent.parent/"data"/"history.db"

RiskLevel = Literal["low", "medium", "high"]
ResponseType = Literal["normal", "boundary", "crisis", "error", "non-english"]

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
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        _ensure_reminder_columns(conn)


##Reminder-counter functions. 
# turn_count tracks how many turns a session has had
# last_reminder_turn records the turn_count value at which a reminder was last shown

def _ensure_reminder_columns(conn: sqlite3.Connection) -> None:
    # CREATE TABLE IF NOT EXISTS in schema.sql only takes effect for a brand-new database. An existing sessions table from before this change needs these two
    # columns added explicitly
    existing = {row["name"] for row in conn.execute("PRAGMA table_info(sessions)")}
    if "turn_count" not in existing:
        conn.execute("ALTER TABLE sessions ADD COLUMN turn_count INTEGER NOT NULL DEFAULT 0")
    if "last_reminder_turn" not in existing:
        conn.execute("ALTER TABLE sessions ADD COLUMN last_reminder_turn INTEGER NOT NULL DEFAULT 0")

def increment_turn_count(session_id: str) -> int:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, turn_count) VALUES (?, 1)
            ON CONFLICT(session_id) DO UPDATE SET
                turn_count = turn_count + 1
            """,
            (session_id,),
        )
        row = conn.execute(
            "SELECT turn_count FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["turn_count"]


def get_last_reminder_turn(session_id: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT last_reminder_turn FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["last_reminder_turn"] if row else 0


def set_last_reminder_turn(session_id: str, turn: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, last_reminder_turn)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                last_reminder_turn = excluded.last_reminder_turn
            """,
            (session_id, turn),
        )





def add_entry(session_id: str, user_message: str, system_message: str, response_type: ResponseType, risk_level: RiskLevel) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id) VALUES (?)
            ON CONFLICT(session_id) DO NOTHING;
            """,
            (session_id,),
        )
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
            """
            SELECT COUNT(*) FROM history WHERE session_id = ?;
            """,
            (session_id,),
        ).fetchone()
        deleted_count = rows[0]
        conn.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        return deleted_count

#Stage functions to for traching which CBT conversation stage a session is in (706c)
def get_session_stage(session_id: str) -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT stage FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return row["stage"] if row else "Start"   # "If no stage is supplied, stay in start"


def set_session_stage(session_id: str, stage: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, stage)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                stage = excluded.stage
            """,
            (session_id, stage),
        )

# Feedback functions to store user feedback on flagged messages
def add_feedback(session_id: str, message_id: str, flagged_message: str, category: str, comment: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id) VALUES (?)
            ON CONFLICT(session_id) DO NOTHING;
            """,
            (session_id,),
        )
        conn.execute(
            """
            INSERT INTO feedback (session_id, message_id, flagged_message, category, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, message_id, flagged_message, json.dumps(category), comment, datetime.now(timezone.utc).isoformat()),
        )

# Session lock function, treats the session as terminated regardless of frontend local state
# TODO: apply session lock
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