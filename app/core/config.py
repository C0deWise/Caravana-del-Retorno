from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

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

    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_BUCKET: str = "multimedia-retornos"

    # ─────────────────────────────────────────
    #  Security
    # ─────────────────────────────────────────
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RECOVERY_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_COOKIE_NAME: str = "refresh_token"
    REFRESH_COOKIE_SECURE: bool = True
    REFRESH_COOKIE_SAMESITE: str = "lax"
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file = BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()