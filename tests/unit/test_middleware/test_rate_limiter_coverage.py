"""Unit tests for rate limiter to increase coverage."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.middleware.rate_limiter import RateLimiter, check_rate_limit


class TestRateLimiterCoverage:
    """Test rate limiter to increase coverage."""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(max_requests=5, window=1)

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_unavailable(self, rate_limiter, mocker):
        """Test check_rate_limit when Redis is unavailable."""
        # Mock get_redis_client to return None
        mocker.patch(
            "src.bot.middleware.rate_limiter.get_redis_client",
            new=AsyncMock(return_value=None),
        )

        # Should fall back to in-memory rate limiting
        allowed, error = await rate_limiter.check_rate_limit(123)

        # First request should be allowed
        assert allowed is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_error(self, rate_limiter, mocker):
        """Test check_rate_limit when Redis raises error."""
        # Mock get_redis_client to raise error
        mock_redis = AsyncMock()
        mock_redis.eval = AsyncMock(side_effect=Exception("Redis error"))
        mocker.patch(
            "src.bot.middleware.rate_limiter.get_redis_client",
            new=AsyncMock(return_value=mock_redis),
        )

        # Should fall back to in-memory rate limiting
        allowed, error = await rate_limiter.check_rate_limit(123)

        # First request should be allowed
        assert allowed is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_rate_limit_memory_exceeded(self, rate_limiter):
        """Test check_rate_limit when memory limit is exceeded."""
        # Send many requests quickly
        for _ in range(6):  # Exceed max_requests of 5
            allowed, error = await rate_limiter.check_rate_limit(123)

        # Should be rate limited
        assert allowed is False
        assert error is not None

    @pytest.mark.asyncio
    async def test_check_rate_limit_handler_no_user(self, mocker):
        """Test check_rate_limit handler when update has no user."""
        from telegram import Update

        update = Update(update_id=1)
        context = MagicMock()

        # Should not raise exception
        await check_rate_limit(update, context)

    @pytest.mark.asyncio
    async def test_check_rate_limit_handler_rate_limited(self, mocker):
        """Test check_rate_limit handler when rate limited."""
        from telegram import Chat, Message, Update
        from telegram import User as TelegramUser

        telegram_user = TelegramUser(
            id=123456789,
            first_name="Test",
            is_bot=False,
        )
        chat = Chat(id=123456789, type="private")
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=telegram_user,
        )
        update = Update(update_id=1, message=message)
        context = MagicMock()

        # Mock rate limiter to return rate limited
        mock_rate_limiter = MagicMock()
        mock_rate_limiter.check_rate_limit = AsyncMock(return_value=(False, "Rate limit exceeded"))
        mocker.patch(
            "src.bot.middleware.rate_limiter._rate_limiter",
            mock_rate_limiter,
        )

        # Mock reply_text
        message.reply_text = AsyncMock()

        await check_rate_limit(update, context)

        # Should send rate limit message
        message.reply_text.assert_called_once()
