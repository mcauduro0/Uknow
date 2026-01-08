"""
Configuration management using Pydantic Settings.
Loads from environment variables and .env files.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_secret_key: SecretStr = Field(default=SecretStr("change-me-in-production"))

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/uknow"
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI (Sparring Partner & Packagers)
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    openai_model: str = "gpt-4-turbo-preview"

    # Anthropic (Debate Analyst - Claude)
    anthropic_api_key: SecretStr = Field(default=SecretStr(""))
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Google AI (Deep Researcher - Gemini)
    google_api_key: SecretStr = Field(default=SecretStr(""))
    gemini_model: str = "gemini-2.0-flash-exp"

    # WhatsApp Business API
    whatsapp_phone_number_id: str = ""
    whatsapp_access_token: SecretStr = Field(default=SecretStr(""))
    whatsapp_verify_token: str = ""
    whatsapp_webhook_secret: SecretStr = Field(default=SecretStr(""))

    # Rate Limiting & Costs
    max_tokens_per_task: int = 100000
    max_debate_rounds: int = 2
    enable_quick_mode: bool = False

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
