"""Unit tests for telegram helpers complete coverage."""

import pytest
from telegram.error import RetryAfter

from src.bot.utils.telegram_helpers import handle_telegram_retry_after, safe_telegram_call


class TestTelegramHelpersComplete:
    """Test telegram helpers for complete coverage."""

    @pytest.mark.asyncio
    async def test_handle_telegram_retry_after_success(self):
        """Test handle_telegram_retry_after with successful call."""

        async def mock_func():
            return "success"

        result = await handle_telegram_retry_after(mock_func)

        assert result == "success"

    @pytest.mark.asyncio
    async def test_handle_telegram_retry_after_retry_success(self):
        """Test handle_telegram_retry_after with retry that succeeds."""
        call_count = 0

        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RetryAfter(retry_after=0.1)
            return "success"

        result = await handle_telegram_retry_after(mock_func, max_retries=3)

        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_handle_telegram_retry_after_max_retries(self):
        """Test handle_telegram_retry_after when max retries exceeded."""

        async def mock_func():
            raise RetryAfter(retry_after=0.1)

        with pytest.raises(RetryAfter):
            await handle_telegram_retry_after(mock_func, max_retries=2)

    @pytest.mark.asyncio
    async def test_handle_telegram_retry_after_other_exception(self):
        """Test handle_telegram_retry_after with non-RetryAfter exception."""

        async def mock_func():
            raise ValueError("Other error")

        with pytest.raises(ValueError):
            await handle_telegram_retry_after(mock_func)

    @pytest.mark.asyncio
    async def test_safe_telegram_call(self):
        """Test safe_telegram_call alias."""

        async def mock_func():
            return "success"

        result = await safe_telegram_call(mock_func)

        assert result == "success"
