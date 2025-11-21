"""Unit tests for rate limiter middleware."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.middleware.rate_limiter import RateLimiter, check_rate_limit


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_init(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(max_requests=10, window=5)
        assert limiter.max_requests == 10
        assert limiter.window == 5

    @pytest.mark.asyncio
    async def test_check_memory_rate_limit_allowed(self):
        """Test in-memory rate limit check when allowed."""
        limiter = RateLimiter(max_requests=5, window=60)

        # Make 4 requests (under limit)
        for _ in range(4):
            allowed, error = limiter._check_memory_rate_limit(123)
            assert allowed is True
            assert error is None

    @pytest.mark.asyncio
    async def test_check_memory_rate_limit_exceeded(self):
        """Test in-memory rate limit check when exceeded."""
        limiter = RateLimiter(max_requests=3, window=60)

        # Make requests up to limit
        for _ in range(3):
            allowed, error = limiter._check_memory_rate_limit(123)
            assert allowed is True

        # Next request should be blocked
        allowed, error = limiter._check_memory_rate_limit(123)
        assert allowed is False
        assert error is not None
        assert "Rate limit exceeded" in error

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_allowed(self, mocker):
        """Test Redis rate limit check when allowed."""
        limiter = RateLimiter(max_requests=5, window=60)

        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value=None)  # First request
        mock_redis.setex = mocker.AsyncMock()

        allowed, error = await limiter._check_redis_rate_limit(mock_redis, 123)

        assert allowed is True
        assert error is None
        mock_redis.setex.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_exceeded(self, mocker):
        """Test Redis rate limit check when exceeded."""
        limiter = RateLimiter(max_requests=5, window=60)

        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value="5")  # At limit
        mock_redis.ttl = mocker.AsyncMock(return_value=30)

        allowed, error = await limiter._check_redis_rate_limit(mock_redis, 123)

        assert allowed is False
        assert error is not None
        assert "Rate limit exceeded" in error
        assert "30" in error

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_increment(self, mocker):
        """Test Redis rate limit increment."""
        limiter = RateLimiter(max_requests=5, window=60)

        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value="3")  # Under limit
        mock_redis.incr = mocker.AsyncMock()

        allowed, error = await limiter._check_redis_rate_limit(mock_redis, 123)

        assert allowed is True
        assert error is None
        mock_redis.incr.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_available(self, mocker):
        """Test check_rate_limit with Redis available."""
        limiter = RateLimiter()

        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value=None)
        mock_redis.setex = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.middleware.rate_limiter.get_redis_client",
            side_effect=get_redis_mock,
        )

        allowed, error = await limiter.check_rate_limit(123)

        assert allowed is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_rate_limit_redis_unavailable(self, mocker):
        """Test check_rate_limit with Redis unavailable (fallback to memory)."""
        limiter = RateLimiter()

        async def get_redis_mock():
            return None

        mocker.patch(
            "src.bot.middleware.rate_limiter.get_redis_client",
            side_effect=get_redis_mock,
        )

        allowed, error = await limiter.check_rate_limit(123)

        # Should fallback to memory and allow
        assert allowed is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_rate_limit_exception(self, mocker):
        """Test check_rate_limit with exception (fail open)."""
        limiter = RateLimiter()

        async def get_redis_mock():
            raise Exception("Connection error")

        mocker.patch(
            "src.bot.middleware.rate_limiter.get_redis_client",
            side_effect=get_redis_mock,
        )

        # Should fail open (allow request)
        allowed, error = await limiter.check_rate_limit(123)

        assert allowed is True
        assert error is None


class TestCheckRateLimitHandler:
    """Test check_rate_limit handler function."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
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
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, mock_update, mock_context, mocker):
        """Test rate limit check when allowed."""
        # Mock rate limiter to allow
        mocker.patch(
            "src.bot.middleware.rate_limiter._rate_limiter.check_rate_limit",
            return_value=(True, None),
        )

        await check_rate_limit(mock_update, mock_context)

        # Should not send any message - just verify it completed without error
        # (no assertion needed as function returns None)

    @pytest.mark.asyncio
    async def test_check_rate_limit_exceeded(self, mock_update, mock_context, mocker):
        """Test rate limit check when exceeded."""
        # Mock rate limiter to block
        mocker.patch(
            "src.bot.middleware.rate_limiter._rate_limiter.check_rate_limit",
            return_value=(False, "Rate limit exceeded. Please wait 30 seconds."),
        )

        # Mock effective_message.reply_text (effective_message returns message)
        reply_text_mock = mocker.AsyncMock()
        # Use patch to replace the method
        mocker.patch(
            "src.bot.middleware.rate_limiter.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await check_rate_limit(mock_update, mock_context)

        # Should send rate limit message
        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "Rate limit exceeded" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_check_rate_limit_no_user(self, mock_update, mock_context, mocker):
        """Test rate limit check when no effective user."""
        # Create update without effective_user (no message means no effective_user)
        from telegram import Update

        update_no_user = Update(update_id=2)  # No message, so no effective_user

        await check_rate_limit(update_no_user, mock_context)

        # Should return early without checking (no error should be raised)

    @pytest.mark.asyncio
    async def test_check_rate_limit_reply_error(self, mock_update, mock_context, mocker):
        """Test rate limit check when reply fails."""
        # Mock rate limiter to block
        mocker.patch(
            "src.bot.middleware.rate_limiter._rate_limiter.check_rate_limit",
            return_value=(False, "Rate limit exceeded. Please wait 30 seconds."),
        )

        # Mock effective_message.reply_text to raise error
        reply_text_mock = mocker.AsyncMock(side_effect=Exception("Send failed"))
        effective_message_mock = MagicMock()
        effective_message_mock.reply_text = reply_text_mock

        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=effective_message_mock,
        )

        # Should handle error gracefully
        await check_rate_limit(mock_update, mock_context)

        # Should have attempted to send message
        reply_text_mock.assert_called_once()
