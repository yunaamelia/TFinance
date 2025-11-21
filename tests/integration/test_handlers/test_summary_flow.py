"""Integration tests for summary viewing flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.summary import (
    handle_period_selection,
    start_summary,
)


class TestSummaryFlow:
    """Test summary viewing conversation flow."""

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
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    @patch("src.bot.handlers.summary.get_async_session_maker")
    @patch("src.bot.handlers.summary.get_redis_client")
    async def test_start_summary(self, mock_redis, mock_session, mock_update, mock_context):
        """Test starting summary view."""
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = mock_update.effective_user
        callback_query.data = "view_summary"

        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock database and Redis
        mock_db_session = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db_session
        mock_session.return_value.__aexit__.return_value = None
        mock_redis.return_value = AsyncMock()

        await start_summary(mock_update, mock_context)

        callback_query.edit_message_text.assert_called_once()
        call_args = callback_query.edit_message_text.call_args
        assert "Summary" in call_args[0][0] or "summary" in call_args[0][0].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.summary.get_async_session_maker")
    @patch("src.bot.handlers.summary.get_redis_client")
    async def test_period_selection(self, mock_redis, mock_session, mock_update, mock_context):
        """Test period selection."""
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = mock_update.effective_user
        callback_query.data = "period:month"

        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock database and Redis
        mock_db_session = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db_session
        mock_session.return_value.__aexit__.return_value = None
        mock_redis.return_value = AsyncMock()

        await handle_period_selection(mock_update, mock_context)

        assert mock_context.user_data.get("selected_period") == "month"
        callback_query.edit_message_text.assert_called_once()
