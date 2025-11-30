from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class AnalyticsEntry:
    event: str
    user_id: int
    payload: Dict[str, str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class AnalyticsService:
    def __init__(self) -> None:
        self.events: List[AnalyticsEntry] = []
        self.errors: List[str] = []

    def log_event(self, event: str, user_id: int, payload: Dict[str, str] | None = None) -> None:
        payload = payload or {}
        self.events.append(AnalyticsEntry(event=event, user_id=user_id, payload=payload))

    def log_error(self, message: str) -> None:
        self.errors.append(message)

    def summary(self) -> Dict[str, int]:
        return {
            "events": len(self.events),
            "errors": len(self.errors),
        }

    def top_documents(self, limit: int = 5) -> List[tuple[str, int]]:
        counter: Counter[str] = Counter(
            entry.payload.get("document", "unknown") for entry in self.events if entry.event == "document_generated"
        )
        return counter.most_common(limit)
