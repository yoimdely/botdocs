import asyncio
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..config import settings

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "usage_limits.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_document_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_user_document_usage_month
        ON user_document_usage (user_id, created_at)
        """
    )
    return conn


def get_month_start(now: Optional[datetime] = None) -> datetime:
    current = now or datetime.now(timezone.utc)
    return current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _fetch_count_since(user_id: int, created_from: str) -> int:
    with closing(_get_connection()) as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM user_document_usage WHERE user_id = ? AND created_at >= ?",
            (user_id, created_from),
        )
        row = cursor.fetchone()
        return row[0] if row else 0


def _insert_usage(user_id: int, created_at: str) -> None:
    with closing(_get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO user_document_usage (user_id, created_at)
            VALUES (?, ?)
            """,
            (user_id, created_at),
        )
        conn.commit()


async def get_user_doc_count(user_id: int, month_start: Optional[datetime] = None) -> int:
    start = month_start or get_month_start()
    return await asyncio.to_thread(_fetch_count_since, user_id, start.isoformat())


async def register_document_usage(user_id: int, created_at: Optional[datetime] = None) -> None:
    timestamp = (created_at or datetime.now(timezone.utc)).isoformat()
    await asyncio.to_thread(_insert_usage, user_id, timestamp)


async def can_create_document(user_id: int, limit: Optional[int] = None) -> bool:
    monthly_limit = limit or settings.monthly_document_limit
    count = await get_user_doc_count(user_id)
    return count < monthly_limit
