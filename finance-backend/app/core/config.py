"""
core/config.py
--------------
Centralized configuration using environment variables via Pydantic Settings.
All settings are loaded once at startup and shared across the app.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App metadata
    app_name: str = "Finance Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = True

    # JWT / Security
    secret_key: str = "fallback-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Database
    database_url: str = "sqlite:///./finance.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cache settings so .env is only read once."""
    return Settings()
