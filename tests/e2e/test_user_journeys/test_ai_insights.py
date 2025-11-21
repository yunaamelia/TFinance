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
    @patch("src.bot.handlers.ai_chat.get_async_session_maker")
    @patch("src.bot.handlers.ai_chat.get_redis_client")
    @patch("src.bot.handlers.ai_chat.TransactionService")
    async def test_complete_ai_insights_flow(
        self, mock_transaction_service, mock_redis, mock_session, mock_get_service
    ):
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

        # Mock database session
        mock_db_session = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db_session
        mock_session.return_value.__aexit__.return_value = None

        # Mock TransactionService
        mock_transaction_service_instance = AsyncMock()
        mock_transaction_service_instance.get_transactions = AsyncMock(return_value=[])
        mock_transaction_service.return_value = mock_transaction_service_instance

        # Mock Redis - get_redis_client is async function, so make it return AsyncMock
        mock_redis_client = AsyncMock()

        # get_redis_client is async, so we need to make the mock return the client directly
        async def get_redis_mock():
            return mock_redis_client

        mock_redis.side_effect = get_redis_mock

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
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = telegram_user
        callback_query.data = "ask_jarvis"

        object.__setattr__(update, "callback_query", callback_query)
        await start_ai_chat(update, context)

        # Step 2: Send message to AI
        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "What did I spend most on this month?"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = chat
        mock_message.from_user = telegram_user
        object.__setattr__(update, "message", mock_message)

        await handle_ai_message(update, context)

        # Verify AI service was called with correct context
        mock_ai_service.generate_response.assert_called()
        call_args = mock_ai_service.generate_response.call_args
        assert "What did I spend most" in call_args[0][0]

        # Verify response was sent to user
        mock_message.reply_text.assert_called()
