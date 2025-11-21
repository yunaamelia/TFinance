"""Unit tests for rate limiter complete coverage."""

from unittest.mock import AsyncMock

import pytest

from src.bot.middleware.rate_limiter import RateLimiter


class TestRateLimiterComplete:
    """Test rate limiter for complete coverage."""

    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance."""
        return RateLimiter(max_requests=5, window=1)

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_with_count(self, rate_limiter, mocker):
        """Test _check_redis_rate_limit with count from Redis."""
        mock_redis = AsyncMock()
        # Mock get to return count string
        mock_redis.get = AsyncMock(return_value="3")
        mock_redis.set = AsyncMock()
        mock_redis.expire = AsyncMock()

        allowed, error = await rate_limiter._check_redis_rate_limit(mock_redis, 123)

        # Should be allowed (3 < 5)
        assert allowed is True
        assert error is None

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_exceeded(self, rate_limiter, mocker):
        """Test _check_redis_rate_limit when limit exceeded."""
        mock_redis = AsyncMock()
        # Mock get to return count that exceeds limit
        mock_redis.get = AsyncMock(return_value="6")
        mock_redis.ttl = AsyncMock(return_value=30)

        allowed, error = await rate_limiter._check_redis_rate_limit(mock_redis, 123)

        # Should be rate limited
        assert allowed is False
        assert error is not None
        assert "wait" in error.lower() or "limit" in error.lower()

    @pytest.mark.asyncio
    async def test_check_redis_rate_limit_no_count(self, rate_limiter, mocker):
        """Test _check_redis_rate_limit when no count exists."""
        mock_redis = AsyncMock()
        # Mock get to return None (no count)
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()
        mock_redis.expire = AsyncMock()

        allowed, error = await rate_limiter._check_redis_rate_limit(mock_redis, 123)

        # Should be allowed (first request)
        assert allowed is True
        assert error is None
