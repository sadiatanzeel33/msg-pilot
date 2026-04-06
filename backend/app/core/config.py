"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://msgpilot:msgpilot_secret@localhost:5432/msgpilot"
    DATABASE_URL_SYNC: str = "postgresql://msgpilot:msgpilot_secret@localhost:5432/msgpilot"

    # ── Auth ──
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Redis / Celery ──
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── WhatsApp ──
    WA_SESSION_DIR: str = "./wa_sessions"
    WA_HEADLESS: bool = True

    # ── Uploads ──
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # ── Safety ──
    DEFAULT_MIN_DELAY: int = 8
    DEFAULT_MAX_DELAY: int = 25
    DAILY_SEND_LIMIT: int = 500

    # ── CORS ──
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
