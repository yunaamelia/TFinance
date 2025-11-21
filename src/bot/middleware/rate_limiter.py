"""Rate limiting middleware for Telegram bot."""

import logging
import time
from collections import defaultdict

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.config.settings import get_redis_client

logger = logging.getLogger(__name__)

# Rate limit configuration
MESSAGES_PER_SECOND = 30  # Telegram Bot API limit
WINDOW_SECONDS = 1


class RateLimiter:
    """Rate limiter to prevent abuse and respect Telegram API limits."""

    def __init__(self, max_requests: int = MESSAGES_PER_SECOND, window: int = WINDOW_SECONDS):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = window
        self._in_memory_store: dict[int, list[float]] = defaultdict(list)

    async def check_rate_limit(self, user_id: int) -> tuple[bool, str | None]:
        """Check if user has exceeded rate limit.

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (allowed, error_message)
        """
        try:
            # Try Redis first (production)
            redis_client = await get_redis_client()
            if redis_client:
                return await self._check_redis_rate_limit(redis_client, user_id)

            # Fallback to in-memory (development)
            return self._check_memory_rate_limit(user_id)
        except Exception as e:
            logger.warning(f"Rate limit check failed, allowing request: {e}")
            # Fail open - allow request if rate limiting fails
            return True, None

    async def _check_redis_rate_limit(self, redis_client, user_id: int) -> tuple[bool, str | None]:
        """Check rate limit using Redis.

        Args:
            redis_client: Redis client
            user_id: Telegram user ID

        Returns:
            Tuple of (allowed, error_message)
        """
        key = f"rate_limit:{user_id}"

        # Get current count
        count = await redis_client.get(key)
        if count is None:
            # First request in window
            await redis_client.setex(key, self.window, "1")
            return True, None

        count = int(count)
        if count >= self.max_requests:
            # Rate limit exceeded
            ttl = await redis_client.ttl(key)
            return False, f"Rate limit exceeded. Please wait {ttl} seconds."

        # Increment counter
        await redis_client.incr(key)
        return True, None

    def _check_memory_rate_limit(self, user_id: int) -> tuple[bool, str | None]:
        """Check rate limit using in-memory store (fallback).

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (allowed, error_message)
        """
        current_time = time.time()
        window_start = current_time - self.window

        # Clean old entries
        user_requests = self._in_memory_store[user_id]
        user_requests[:] = [req_time for req_time in user_requests if req_time > window_start]

        # Check limit
        if len(user_requests) >= self.max_requests:
            oldest_request = min(user_requests)
            wait_time = int(self.window - (current_time - oldest_request))
            return False, f"Rate limit exceeded. Please wait {wait_time} seconds."

        # Add current request
        user_requests.append(current_time)
        return True, None


# Global rate limiter instance
_rate_limiter = RateLimiter()


async def check_rate_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check rate limit before processing update.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        True if request should proceed, False if rate limited
    """
    if not update.effective_user:
        return True

    user_id = update.effective_user.id
    allowed, error_message = await _rate_limiter.check_rate_limit(user_id)

    if not allowed:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        if update.effective_message:
            try:
                await update.effective_message.reply_text(
                    f"⚠️ {error_message}\n\nPlease slow down and try again in a moment."
                )
            except Exception as e:
                logger.error(f"Failed to send rate limit message: {e}")
        return False

    return True
