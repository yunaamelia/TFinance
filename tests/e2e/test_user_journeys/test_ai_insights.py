"""E2E tests for AI insights user journey."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.ai_chat import handle_ai_message, start_ai_chat


class TestAIInsightsJourney:
    """E2E test for complete AI insights user journey."""

    @pytest.mark.asyncio
    @patch("src.bot.handlers.ai_chat.get_ai_service")
    async def test_complete_ai_insights_flow(self, mock_get_service):
        """Test complete flow from asking JARVIS to getting insights."""
        # Mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response = AsyncMock(
            return_value=(
                "Good day, Sir. Based on your recent transactions, "
                "I've noticed you've spent 50,000 on Food & Dining this month. "
                "I recommend reviewing your dining expenses."
            ),
        )
        mock_get_service.return_value = mock_ai_service

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

        # Step 1: Start AI chat (via callback)
        update.callback_query = MagicMock()
        update.callback_query.edit_message_text = AsyncMock()
        await start_ai_chat(update, context)

        # Step 2: Send message to AI
        update.message = message
        update.message.text = "What did I spend most on this month?"
        update.message.reply_text = AsyncMock()
        await handle_ai_message(update, context)

        # Verify AI service was called with correct context
        mock_ai_service.generate_response.assert_called()
        call_args = mock_ai_service.generate_response.call_args
        assert "What did I spend most" in call_args[0][0]

        # Verify response was sent to user
        update.message.reply_text.assert_called()
