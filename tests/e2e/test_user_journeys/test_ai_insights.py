"""E2E tests for AI insights user journey."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.ai_chat import handle_ai_message, start_ai_chat


class TestAIInsightsJourney:
    """E2E test for complete AI insights user journey."""

    @pytest.mark.asyncio
    async def test_complete_ai_insights_flow(self, mocker):
        """Test complete flow from asking JARVIS to getting insights."""
        # Mock AI service using mocker - patch the function that returns the service
        mock_ai_service = mocker.MagicMock()
        mock_ai_service.generate_response = mocker.AsyncMock(
            return_value=(
                "Good day, Sir. Based on your recent transactions, "
                "I've noticed you've spent 50,000 on Food & Dining this month. "
                "I recommend reviewing your dining expenses."
            ),
        )
        mocker.patch(
            "src.bot.handlers.ai_chat.get_ai_service",
            return_value=mock_ai_service,
        )

        # Mock database session
        mock_db_session = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_db_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.ai_chat.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock TransactionService
        mock_transaction_service_instance = mocker.AsyncMock()
        mock_transaction_service_instance.get_transactions = mocker.AsyncMock(return_value=[])
        mocker.patch(
            "src.bot.handlers.ai_chat.TransactionService",
            return_value=mock_transaction_service_instance,
        )

        # Mock Redis - get_redis_client is async function
        mock_redis_client = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis_client

        mocker.patch(
            "src.bot.handlers.ai_chat.get_redis_client",
            side_effect=get_redis_mock,
        )

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
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
        callback_query.from_user = telegram_user
        callback_query.data = "ask_jarvis"

        object.__setattr__(update, "callback_query", callback_query)
        await start_ai_chat(update, context)

        # Step 2: Send message to AI
        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "What did I spend most on this month?"
        mock_message.chat = chat
        mock_message.from_user = telegram_user
        object.__setattr__(update, "message", mock_message)

        # Mock processing message (returned by reply_text)
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = mocker.AsyncMock()
        mock_processing_msg.delete = mocker.AsyncMock()

        # Mock reply_text using mocker's AsyncMock
        mock_message.reply_text = mocker.AsyncMock(return_value=mock_processing_msg)

        # Mock context.bot.send_chat_action
        context.bot = MagicMock()
        context.bot.send_chat_action = mocker.AsyncMock()

        # Mock User model query
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none.return_value = None  # User doesn't exist
        mock_db_session.execute = mocker.AsyncMock(return_value=mock_user_result)
        mock_db_session.commit = mocker.AsyncMock()
        mock_db_session.add = mocker.MagicMock()  # add() is synchronous

        await handle_ai_message(update, context)

        # Verify typing indicator was sent
        context.bot.send_chat_action.assert_called_once()

        # Verify processing message was sent
        mock_message.reply_text.assert_called()

        # Verify AI service was called with correct context
        mock_ai_service.generate_response.assert_called()
        call_args = mock_ai_service.generate_response.call_args
        assert "What did I spend most" in call_args[0][0]

        # Verify processing message was edited with response
        mock_processing_msg.edit_text.assert_called_once()
