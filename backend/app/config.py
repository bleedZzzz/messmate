"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for Tiffin Optimizer backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "local"
    database_url: str = "sqlite:///./tiffin.db"
    frontend_origin: str = "http://localhost:3000"
    llm_provider: str = "none"
    llm_model: str = ""
    llm_timeout_seconds: float = 20.0
    llm_max_retries: int = 2
    groq_api_key: str = ""
    together_api_key: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = ""
    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
