"""Unit tests for settings configuration."""

import pytest

from src.bot.config.settings import (
    get_async_session_maker,
    get_redis_client,
    settings,
)


class TestSettings:
    """Test settings configuration."""

    def test_settings_attributes(self):
        """Test that settings has required attributes."""
        assert hasattr(settings, "telegram_bot_token")
        assert hasattr(settings, "openai_api_key")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "redis_url")
        assert hasattr(settings, "environment")
        assert hasattr(settings, "log_level")

    def test_settings_environment(self):
        """Test environment setting."""
        # Should have a default or be set
        assert settings.environment in ["development", "production", "test"]

    def test_get_async_session_maker(self):
        """Test getting async session maker."""
        session_maker = get_async_session_maker()

        # Should return a callable (session maker)
        assert callable(session_maker)

    @pytest.mark.asyncio
    async def test_get_redis_client(self):
        """Test getting Redis client."""
        redis_client = await get_redis_client()

        # Should return Redis client or None (if Redis not available)
        # In test environment, might be None
        assert redis_client is None or hasattr(redis_client, "ping")

    def test_get_async_engine(self):
        """Test getting async database engine."""
        from src.bot.config.settings import get_async_engine

        engine = get_async_engine()

        # Should return an engine
        assert engine is not None

    def test_get_sync_engine(self):
        """Test getting sync database engine."""
        from src.bot.config.settings import get_sync_engine

        engine = get_sync_engine()

        # Should return an engine
        assert engine is not None

    def test_get_sync_session_maker(self):
        """Test getting sync session maker."""
        from src.bot.config.settings import get_sync_session_maker

        session_maker = get_sync_session_maker()

        # Should return a callable (session maker)
        assert callable(session_maker)

    @pytest.mark.asyncio
    async def test_close_redis_client(self, mocker):
        """Test closing Redis client."""
        from src.bot.config.settings import close_redis_client

        # Mock Redis client
        mock_redis = mocker.AsyncMock()
        mock_redis.close = mocker.AsyncMock()
        mocker.patch("src.bot.config.settings._redis_client", mock_redis)

        # Should close client
        await close_redis_client()

        # Verify close was called
        mock_redis.close.assert_called_once()

    def test_settings_is_production(self):
        """Test is_production property."""
        # Should return boolean
        assert isinstance(settings.is_production, bool)

    def test_settings_is_development(self):
        """Test is_development property."""
        # Should return boolean
        assert isinstance(settings.is_development, bool)
