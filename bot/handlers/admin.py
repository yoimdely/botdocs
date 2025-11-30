from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ..config import Settings
from ..services.analytics import AnalyticsService
from ..services.storage import StorageService
from .middleware import DependencyMiddleware

router = Router()


def setup_router(settings: Settings, analytics: AnalyticsService, storage: StorageService) -> Router:
    router.message.middleware(
        DependencyMiddleware(settings=settings, analytics=analytics, storage=storage)
    )
    return router


@router.message(Command("admin"))
async def admin_panel(message: Message, settings: Settings, analytics: AnalyticsService, storage: StorageService) -> None:
    if message.from_user.id not in settings.admin_ids:
        await message.answer("Доступ запрещен")
        return
    stats = storage.stats()
    top_docs = storage.top_documents()
    analytics_summary = analytics.summary()
    await message.answer(
        "Админ-панель:\n"
        f"Пользователей: {stats['users']}\n"
        f"Генераций: {stats['generations']}\n"
        f"TOP документов: {top_docs}\n"
        f"Ошибок: {analytics_summary['errors']}\n"
        f"Событий: {analytics_summary['events']}\n"
        f"Последнее обновление: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}"
    )
