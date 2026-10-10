from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Aereo Task API"
    database_url: str = "postgresql+asyncpg://aereo:aereo@db:5432/aereo"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit: str = "100/minute"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("jwt_secret")
    @classmethod
    def validate_secret(cls, value: str) -> str:
        if len(value) < 32 and value != "change-me-in-production":
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()