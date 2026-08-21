import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Wealify Financial Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./wealify.db"
    
    # LLM - Pluggable, will be configured later
    LLM_PROVIDER: str = "anthropic"  # anthropic | openai | gemini
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-sonnet-20240229"
    
    # Email (IMAP)
    IMAP_HOST: str = ""
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    
    # Security: 64-byte default key for HMAC-SHA256
    SECRET_KEY: str = "wealify-ai-financial-guardian-secret-key-2026-hackathon-security-token-64bytes"
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
