from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskForge API"
    environment: str = "development"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://taskforge:taskforge@localhost:5432/taskforge"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="dev-only-change-me-please-32-characters", min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rate_limit_per_minute: int = 60
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
