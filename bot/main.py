import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .config import load_settings
from .handlers import admin, commands, documents, feedback, payments
from .services.analytics import AnalyticsService
from .services.storage import StorageService


async def main() -> None:
    settings = load_settings()
    logging.basicConfig(level=logging.INFO if settings.enable_logging else logging.WARNING)

    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    analytics = AnalyticsService()
    storage_service = StorageService(settings=settings, analytics=analytics)

    dp.include_router(commands.setup_router(settings, analytics, storage_service))
    dp.include_router(feedback.router)
    dp.include_router(documents.setup_router(settings, analytics, storage_service))
    dp.include_router(payments.setup_router(settings, analytics, storage_service))
    dp.include_router(admin.setup_router(settings, analytics, storage_service))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
