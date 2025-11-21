"""E2E tests for view summary user journey."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, Message, User as TelegramUser, Chat
from telegram.ext import Application, ContextTypes

from src.bot.handlers.summary import start_summary, handle_period_selection


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
        update.callback_query = MagicMock()
        update.callback_query.edit_message_text = AsyncMock()
        await start_summary(update, context)

        # Verify summary view started
        update.callback_query.edit_message_text.assert_called()

        # Step 2: Select period
        update.callback_query.data = "period:month"
        await handle_period_selection(update, context)

        # Verify period was selected
        assert context.user_data.get("selected_period") == "month"

