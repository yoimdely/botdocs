from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from ..config import settings


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(settings.main_channel_id, user_id)
    except TelegramBadRequest:
        return False

    return member.status in ("member", "administrator", "creator")
