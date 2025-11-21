"""Configuration management for FinancialAssist bot."""

import logging
from pathlib import Path
from typing import Any

import redis.asyncio as redis
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.bot.config.logging_config import setup_logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Telegram Bot API token")

    # AI Service Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    ai_response_timeout: int = Field(default=3, description="AI API response timeout in seconds")

    # Database Configuration
    database_url: str = Field(..., description="Database connection URL")
    database_echo: bool = Field(default=False, description="Echo SQL queries (for debugging)")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds (5 minutes)")

    # Application Configuration
    environment: str = Field(
        default="development", description="Environment (development/production)"
    )
    log_level: str = Field(default="INFO", description="Logging level")
    bot_response_timeout: int = Field(default=2, description="Bot response timeout in seconds")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()

# Setup logging based on environment
_log_file = None
if settings.is_production:
    _log_file = Path("/var/log/financialassist/bot.log")

setup_logging(
    log_level=settings.log_level,
    environment=settings.environment,
    log_file=_log_file,
)

# Database engine and session
_async_engine: Any | None = None
_async_session_maker: Any | None = None
_sync_engine = None
_sync_session_maker = None


def get_async_engine():
    """Get or create async database engine."""
    global _async_engine
    if _async_engine is None:
        # Convert SQLite URL to async if needed
        db_url = settings.database_url
        if db_url.startswith("sqlite"):
            db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

        _async_engine = create_async_engine(
            db_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        logger.info("Async database engine created")
    return _async_engine


def get_async_session_maker():
    """Get or create async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_async_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Async session maker created")
    return _async_session_maker


def get_sync_engine():
    """Get or create sync database engine (for Alembic migrations)."""
    global _sync_engine
    if _sync_engine is None:
        # Use sync driver for migrations
        db_url = settings.database_url
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        elif db_url.startswith("sqlite+aiosqlite:///"):
            db_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")

        _sync_engine = create_engine(
            db_url,
            echo=settings.database_echo,
            pool_pre_ping=True,
        )
        logger.info("Sync database engine created")
    return _sync_engine


def get_sync_session_maker():
    """Get or create sync session maker (for Alembic migrations)."""
    global _sync_session_maker
    if _sync_session_maker is None:
        engine = get_sync_engine()
        _sync_session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        logger.info("Sync session maker created")
    return _sync_session_maker


# Redis client
_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info("Redis client created")
    return _redis_client


async def close_redis_client():
    """Close Redis client connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client closed")


# Logging is now configured via setup_logging() above
