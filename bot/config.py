from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(..., description="Telegram bot token")
    admin_ids: List[int] = Field(default_factory=list, env="ADMIN_IDS")
    enable_logging: bool = True
    monthly_document_limit: int = Field(default=10, description="Documents per month limit")
    main_channel_id: int = Field(..., description="ID обязательного канала")
    main_channel_username: str = Field(..., description="Username канала без https://t.me/")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()


def load_settings() -> Settings:
    return settings
