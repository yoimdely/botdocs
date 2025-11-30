from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..config import settings


def subscription_keyboard() -> InlineKeyboardMarkup:
    channel_username = settings.main_channel_username.lstrip('@')
    channel_url = f"https://t.me/{channel_username}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📣 Подписаться на канал", url=channel_url)],
            [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")],
        ]
    )


def result_keyboard(document_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬇️ Скачать .DOCX", callback_data=f"get_docx:{document_id}")],
            [InlineKeyboardButton(text="🔁 К категориям", callback_data="docs")],
            [InlineKeyboardButton(text="📄 DOCX (скоро)", callback_data="docx_placeholder")],
            [InlineKeyboardButton(text="🚀 Про-режим в разработке", callback_data="upgrade")],
        ]
    )
