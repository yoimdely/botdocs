from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from ..config import settings

router = Router()

# Простое in-memory хранилище id тех, от кого ждём отзыв
waiting_feedback_users: set[int] = set()


@router.callback_query(F.data == "feedback_start")
async def feedback_start(callback: CallbackQuery):
    user = callback.from_user
    waiting_feedback_users.add(user.id)

    await callback.message.answer(
        "🙏 Спасибо, что хотите оставить отзыв!\n\n"
        "Пожалуйста, отправьте одним сообщением ваш отзыв — что понравилось, "
        "что можно улучшить, каких документов не хватает."
    )
    await callback.answer()


@router.message(
    F.text,
    F.from_user.id.func(lambda user_id: user_id in waiting_feedback_users),
)
async def feedback_catcher(message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id

    # Если ждём отзыв от этого пользователя — обрабатываем отзыв
    if user_id in waiting_feedback_users and message.text:
        waiting_feedback_users.remove(user_id)

        admin_ids = settings.admin_ids or []

        text = (
            "📝 Новый отзыв от пользователя\n"
            f"ID: <code>{user_id}</code>\n"
            f"Username: @{message.from_user.username or '—'}\n\n"
            f"Текст:\n{message.text}"
        )

        # Отправляем отзыв только администраторам
        for admin_id in admin_ids:
            try:
                await message.bot.send_message(admin_id, text)
            except Exception:
                pass

        await message.answer("Спасибо за отзыв! 💚 Очень ценим вашу помощь.")
        return
