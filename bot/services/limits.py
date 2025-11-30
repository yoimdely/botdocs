import asyncio
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "usage_limits.db"
_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            year_month TEXT NOT NULL,
            doc_count INTEGER NOT NULL DEFAULT 0,
            UNIQUE(user_id, year_month)
        )
        """
    )
    return conn


def get_current_year_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def _fetch_count(user_id: int, year_month: str) -> int:
    with closing(_get_connection()) as conn:
        cursor = conn.execute(
            "SELECT doc_count FROM usage_limits WHERE user_id = ? AND year_month = ?",
            (user_id, year_month),
        )
        row = cursor.fetchone()
        return row[0] if row else 0


def _increment(user_id: int, year_month: str) -> None:
    with closing(_get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO usage_limits (user_id, year_month, doc_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, year_month) DO UPDATE SET doc_count = doc_count + 1
            """,
            (user_id, year_month),
        )
        conn.commit()


async def get_user_doc_count(user_id: int, year_month: Optional[str] = None) -> int:
    ym = year_month or get_current_year_month()
    return await asyncio.to_thread(_fetch_count, user_id, ym)


async def increment_user_doc_count(user_id: int, year_month: Optional[str] = None) -> None:
    ym = year_month or get_current_year_month()
    await asyncio.to_thread(_increment, user_id, ym)


async def can_create_document(user_id: int, limit: Optional[int] = None) -> bool:
    monthly_limit = limit or settings.monthly_document_limit
    count = await get_user_doc_count(user_id)
    return count < monthly_limit
