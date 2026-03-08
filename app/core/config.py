from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # ─────────────────────────────────────────
    #  Application
    # ─────────────────────────────────────────
    APP_NAME: str = "FastAPI App"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = ""
    DEBUG: bool = False
    PORT: int = 8000

    # ─────────────────────────────────────────
    #  Database
    # ─────────────────────────────────────────
    DATABASE_URL: str

    # ─────────────────────────────────────────
    #  Security
    # ─────────────────────────────────────────
    SECRET_KEY: str = "supersecretkey"
    ALLOWED_HOSTS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file = BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()