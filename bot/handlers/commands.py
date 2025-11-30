from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..config import Settings
from ..services.analytics import AnalyticsService
from ..services.legal import DISCLAIMER_TEXT
from ..services.storage import StorageService
from .documents import build_categories_keyboard
from .middleware import DependencyMiddleware

router = Router()


def legal_ack_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Ознакомлен", callback_data="legal_ack")]]
    )


def setup_router(settings: Settings, analytics: AnalyticsService, storage: StorageService) -> Router:
    router.message.middleware(
        DependencyMiddleware(settings=settings, analytics=analytics, storage=storage)
    )
    return router


@router.message(CommandStart())
async def cmd_start(message: Message, settings: Settings, analytics: AnalyticsService) -> None:
    analytics.log_event("start", message.from_user.id, {})
    await message.answer(
        "<b>Привет!</b> 👋\n"
        "Я — бот «Мой Юрист». Помогу подготовить простые договоры и документы на основе ваших ответов.\n\n"
        "Выберите категорию документов, с которой хотите начать:",
        reply_markup=build_categories_keyboard(),
    )
    await message.answer(DISCLAIMER_TEXT, reply_markup=legal_ack_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Как пользоваться ботом</b>\n"
        "1️⃣ Выберите документ из подходящей категории.\n"
        "2️⃣ Ответьте на вопросы — бот подставит данные в шаблон.\n"
        "3️⃣ Получите готовый файл в формате PDF или DOCX.\n\n"
        "Команды: /docs — категории, /profile — профиль, /legal — правовая информация, /cancel — отменить документ."
    )


@router.message(Command("legal", "terms"))
async def cmd_legal(message: Message) -> None:
    await message.answer(
        f"Правовая информация и условия использования:\n\n{DISCLAIMER_TEXT}",
        reply_markup=legal_ack_keyboard(),
    )


@router.message(Command("docs"))
async def cmd_docs(message: Message) -> None:
    await message.answer("Выберите категорию документов:", reply_markup=build_categories_keyboard())


@router.message(Command("profile"))
async def cmd_profile(message: Message, storage: StorageService) -> None:
    profile = storage.get_profile(message.from_user.id)
    history = ", ".join(profile.history[-5:]) if profile.history else "Документов пока нет"
    await message.answer(
        "<b>Ваш профиль</b>\n"
        f"Тариф: {'Pro' if profile.is_pro else 'Free'}\n"
        f"Документов создано: {profile.documents_generated}\n"
        f"Последние шаблоны: {history}"
    )


@router.callback_query(F.data == "legal_ack")
async def legal_acknowledged(callback: CallbackQuery) -> None:
    await callback.answer("Спасибо! Будьте внимательны при использовании документов.")
    if callback.message:
        await callback.message.delete()
