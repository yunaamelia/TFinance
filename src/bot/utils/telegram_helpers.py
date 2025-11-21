"""Helper utilities for Telegram API interactions with flood control handling."""

import asyncio
import logging
from collections.abc import Callable
from typing import Any, TypeVar

from telegram.error import RetryAfter

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def handle_telegram_retry_after(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """Handle Telegram RetryAfter errors with exponential backoff.

    This function automatically retries Telegram API calls that fail due to
    flood control (rate limiting) with exponential backoff.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retries (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        **kwargs: Keyword arguments for func

    Returns:
        Result of func execution

    Raises:
        RetryAfter: If all retries fail and we still hit flood control
        Exception: Other exceptions from func are re-raised

    Example:
        ```python
        from telegram import Bot

        bot = Bot(token="...")
        result = await handle_telegram_retry_after(
            bot.send_message,
            chat_id=123,
            text="Hello"
        )
        ```
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except RetryAfter as e:
            wait_time = e.retry_after
            if attempt < max_retries - 1:
                # Add exponential backoff: wait_time + (base_delay * 2^attempt)
                backoff_delay = base_delay * (2**attempt)
                total_wait = wait_time + backoff_delay

                logger.warning(
                    f"Flood control hit: Waiting {total_wait:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(total_wait)
            else:
                logger.error(
                    f"Flood control: Max retries ({max_retries}) exceeded. "
                    f"Last wait time: {wait_time}s"
                )
                raise
        except Exception as e:
            # Re-raise non-RetryAfter exceptions immediately
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise


async def safe_telegram_call(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    **kwargs: Any,
) -> Any:
    """Safely call Telegram API function with automatic retry on flood control.

    Alias for handle_telegram_retry_after for convenience.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retries
        **kwargs: Keyword arguments for func

    Returns:
        Result of func execution
    """
    return await handle_telegram_retry_after(func, *args, max_retries=max_retries, **kwargs)
