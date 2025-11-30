from __future__ import annotations

import logging
from typing import Set

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from ..config import Settings
from ..services.storage import StorageService
from .middleware import DependencyMiddleware


waiting_feedback_users: Set[int] = set()


def setup_router(settings: Settings, storage: StorageService) -> Router:
    router = Router()
    router.callback_query.middleware(
        DependencyMiddleware(settings=settings, storage=storage)
    )
    router.message.middleware(DependencyMiddleware(settings=settings, storage=storage))

    router.callback_query.register(feedback_start, F.data == "feedback_start")
    router.message.register(
        feedback_catcher,
        F.text,
        F.from_user.id.func(lambda user_id: user_id in waiting_feedback_users),
    )

    return router


async def feedback_start(callback: CallbackQuery, settings: Settings) -> None:
    if not callback.from_user:
        return

    waiting_feedback_users.add(callback.from_user.id)

    await callback.message.answer(
        "🙏 Спасибо, что хотите оставить отзыв!\n\n"
        "Пожалуйста, отправьте одним сообщением ваш отзыв — что понравилось, "
        "что можно улучшить, каких документов не хватает."
    )
    await callback.answer()


async def feedback_catcher(
    message: Message, settings: Settings, storage: StorageService
) -> None:
    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    if user_id not in waiting_feedback_users:
        return

    waiting_feedback_users.remove(user_id)

    admin_ids = settings.admin_ids or []
    username = message.from_user.username or "—"
    last_document = storage.get_last_document(user_id)
    operation = last_document.title if last_document else "Не указано"

    text = (
        "📝 Новый отзыв от пользователя\n"
        f"ID: <code>{user_id}</code>\n"
        f"Username: @{username}\n"
        f"Операция: {operation}\n\n"
        f"Текст:\n{message.text}"
    )

    if not admin_ids:
        logging.warning("Получен отзыв, но список ADMIN_IDS пуст")
    else:
        for admin_id in admin_ids:
            try:
                await message.bot.send_message(admin_id, text)
            except Exception:  # pragma: no cover - логирование ошибок отправки
                logging.exception("Не удалось отправить отзыв администратору %s", admin_id)

    await message.answer("Спасибо за отзыв! 💚 Очень ценим вашу помощь.")
