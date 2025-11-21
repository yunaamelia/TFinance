"""E2E tests for view summary user journey."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.summary import handle_period_selection, start_summary


class TestViewSummaryJourney:
    """E2E test for complete view summary user journey."""

    @pytest.mark.asyncio
    @patch("src.bot.handlers.summary.get_async_session_maker")
    @patch("src.bot.handlers.summary.get_redis_client")
    async def test_complete_view_summary_flow(self, mock_redis, mock_session_maker):
        """Test complete flow from main menu to viewing summary."""
        # Mock database and Redis
        mock_session = AsyncMock()
        mock_session_maker.return_value.__aenter__.return_value = mock_session
        mock_redis_client = AsyncMock()
        mock_redis.return_value = mock_redis_client

        # Create update and context
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
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}

        # Step 1: Start summary view (via callback)
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = telegram_user
        callback_query.data = "view_summary"

        object.__setattr__(update, "callback_query", callback_query)
        await start_summary(update, context)

        # Verify summary view started
        callback_query.edit_message_text.assert_called()

        # Step 2: Select period
        object.__setattr__(callback_query, "data", "period:month")
        await handle_period_selection(update, context)

        # Verify period was selected
        assert context.user_data.get("selected_period") == "month"
