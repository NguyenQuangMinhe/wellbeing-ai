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
