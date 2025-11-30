from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from ..config import Settings


@dataclass
class PaymentResult:
    success: bool
    message: str
    timestamp: datetime


class PaymentService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def create_checkout(self, user_id: int) -> PaymentResult:
        return PaymentResult(success=True, message="Оплата пока в демо-режиме", timestamp=datetime.utcnow())

    async def activate_subscription(self, user_id: int) -> PaymentResult:
        return PaymentResult(success=True, message="Подписка активирована (демо)", timestamp=datetime.utcnow())

    def pricing_info(self) -> Dict[str, str]:
        return {
            "free": f"Free: {self.settings.documents_per_day_free} документ в день",
            "pro": f"Pro: {self.settings.pro_price_rub}₽/мес за {self.settings.documents_per_day_pro} документов в день",
        }
