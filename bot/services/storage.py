from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, List

from ..config import Settings
from .analytics import AnalyticsService


@dataclass
class UserProfile:
    user_id: int
    is_pro: bool = False
    documents_generated: int = 0
    last_generation_date: date | None = None
    history: List[str] | None = None


class StorageService:
    def __init__(self, settings: Settings, analytics: AnalyticsService) -> None:
        self.settings = settings
        self.analytics = analytics
        self.user_profiles: Dict[int, UserProfile] = {}
        self.document_counter: Dict[str, int] = defaultdict(int)

    def get_profile(self, user_id: int) -> UserProfile:
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(user_id=user_id, history=[])
        return self.user_profiles[user_id]

    def can_generate(self, user_id: int) -> bool:
        profile = self.get_profile(user_id)
        today = date.today()
        if profile.last_generation_date != today:
            profile.last_generation_date = today
            profile.documents_generated = 0
        return True

    def register_generation(self, user_id: int, document: str) -> None:
        profile = self.get_profile(user_id)
        profile.documents_generated += 1
        profile.history.append(document)
        self.document_counter[document] += 1
        self.analytics.log_event("document_generated", user_id, {"document": document})

    def activate_pro(self, user_id: int) -> None:
        profile = self.get_profile(user_id)
        profile.is_pro = True
        self.analytics.log_event("subscription_upgraded", user_id, {})

    def stats(self) -> Dict[str, int]:
        total_users = len(self.user_profiles)
        total_generations = sum(self.document_counter.values())
        return {
            "users": total_users,
            "generations": total_generations,
        }

    def top_documents(self, limit: int = 5) -> List[tuple[str, int]]:
        return sorted(self.document_counter.items(), key=lambda item: item[1], reverse=True)[:limit]
