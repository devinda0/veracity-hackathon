from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Vector Agents"
    APP_ENV: Literal["dev", "prod", "test"] = "dev"
    DEBUG: bool = False

    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    JWT_SECRET: str = "dev-secret-change-in-prod-32-bytes"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    MONGO_URI: str = "mongodb://localhost:27017/vector-agents"
    MONGO_DATABASE: str = "vector-agents"
    QDRANT_URL: str = "http://localhost:6333"
    REDIS_URL: str = "redis://localhost:6379/0"
    POSTGRES_URL: str = "postgresql://postgres:postgres@localhost:5432/vector_agents"

    OPENAI_API_KEY: str = "sk-placeholder"
    GEMINI_API_KEY: str = ""
    FIRECRAWL_API_KEY: str = ""
    SERPAPI_API_KEY: str = ""

    OTEL_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return ["http://localhost:5173"]
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @property
    def API_V1_PREFIX(self) -> str:
        return f"{self.API_PREFIX}/{self.API_VERSION}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
