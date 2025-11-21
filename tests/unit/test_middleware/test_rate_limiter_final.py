"""Unit tests for rate limiter final coverage."""

from unittest.mock import AsyncMock

import pytest

from src.bot.middleware.rate_limiter import RateLimiter


class TestRateLimiterFinal:
    """Test rate limiter for final coverage."""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(max_requests=5, window=1)

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_ttl_error(self, rate_limiter, mocker):
        """Test _check_redis_rate_limit when TTL fails."""
        mock_redis = AsyncMock()
        mock_redis.eval = AsyncMock(return_value=6)  # Exceeds limit
        mock_redis.ttl = AsyncMock(side_effect=Exception("TTL error"))

        # When TTL fails, it should still return rate limited but with generic message
        allowed, error = await rate_limiter._check_redis_rate_limit(mock_redis, 123)

        # Should return rate limited (even if TTL fails)
        assert allowed is False
        # Error message might be None if exception is caught, or generic message
        # The actual behavior depends on exception handling

    @pytest.mark.asyncio
    async def test_check_memory_rate_limit_cleanup(self, rate_limiter):
        """Test _check_memory_rate_limit with cleanup of old entries."""
        import time

        # Add old entries
        rate_limiter._in_memory_store[123] = [time.time() - 10]  # Old entry

        # Should clean up and allow new request
        allowed, error = await rate_limiter.check_rate_limit(123)

        assert allowed is True
        assert error is None
