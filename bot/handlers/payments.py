from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..config import Settings
from ..services.analytics import AnalyticsService
from ..services.payments import PaymentService
from ..services.storage import StorageService
from .middleware import DependencyMiddleware

router = Router()


def setup_router(settings: Settings, analytics: AnalyticsService, storage: StorageService) -> Router:
    payment_service = PaymentService(settings)
    router.message.middleware(
        DependencyMiddleware(
            settings=settings, analytics=analytics, storage=storage, payments=payment_service
        )
    )
    router.callback_query.middleware(
        DependencyMiddleware(
            settings=settings, analytics=analytics, storage=storage, payments=payment_service
        )
    )
    return router


@router.message(Command("upgrade"))
async def upgrade(message: Message, payments: PaymentService, storage: StorageService) -> None:
    result = await payments.create_checkout(message.from_user.id)
    await message.answer(
        f"Оформляем Pro (демо). {result.message}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Активировать Pro", callback_data="activate_pro")]]
        ),
    )


@router.callback_query(lambda c: c.data == "activate_pro")
async def activate_pro(callback: CallbackQuery, payments: PaymentService, storage: StorageService) -> None:
    await callback.answer()
    result = await payments.activate_subscription(callback.from_user.id)
    storage.activate_pro(callback.from_user.id)
    await callback.message.answer(result.message)


@router.message(Command("pricing"))
async def pricing(message: Message, payments: PaymentService) -> None:
    info = payments.pricing_info()
    await message.answer(f"Тарифы:\n{info['free']}\n{info['pro']}")
