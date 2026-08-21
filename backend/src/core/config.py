from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Wealify Financial Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./wealify.db"
    
    # LLM - Pluggable on-demand statement analysis
    LLM_PROVIDER: str = "anthropic"  # anthropic | openai | gemini
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-sonnet-20240229"
    
    # Email (IMAP)
    IMAP_HOST: str = ""
    IMAP_USER: str = ""
    IMAP_PASSWORD: str = ""
    
    # Security: 64-byte default key for HMAC-SHA256
    SECRET_KEY: str = "wealify-ai-financial-guardian-secret-key-2026-hackathon-security-token-64bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080"
    
    # Loads from root .env or local .env with extra fields ignored
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
