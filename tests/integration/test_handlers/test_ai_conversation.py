"""Integration tests for AI conversation flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.ai_chat import handle_ai_message, start_ai_chat


class TestAIConversationFlow:
    """Test AI conversation handler flow."""

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
    async def test_start_ai_chat(self, mock_update, mock_context):
        """Test starting AI chat conversation."""
        from telegram import CallbackQuery

        # Create proper callback query mock
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = mock_update.effective_user
        callback_query.data = "ask_jarvis"

        # Use object.__setattr__ to set readonly attribute
        object.__setattr__(mock_update, "callback_query", callback_query)

        await start_ai_chat(mock_update, mock_context)

        # Verify message was sent
        callback_query.edit_message_text.assert_called_once()
        # Check that prompt message was sent
        call_args = callback_query.edit_message_text.call_args
        assert "JARVIS" in call_args[0][0] or "assist" in call_args[0][0].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.ai_chat.get_ai_service")
    @patch("src.bot.handlers.ai_chat.get_async_session_maker")
    @patch("src.bot.handlers.ai_chat.TransactionService")
    async def test_handle_ai_message(
        self,
        mock_transaction_service,
        mock_session,
        mock_get_service,
        mock_update,
        mock_context,
    ):
        """Test handling AI message."""
        # Mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response = AsyncMock(
            return_value="Good day, Sir. How may I assist you today?",
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

        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "Hello JARVIS"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        # Mock context.bot.send_chat_action
        mock_context.bot = MagicMock()
        mock_context.bot.send_chat_action = AsyncMock()

        # Mock processing message (returned by reply_text)
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = AsyncMock()
        mock_processing_msg.delete = AsyncMock()
        mock_message.reply_text.return_value = mock_processing_msg

        # Mock User model query

        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none = AsyncMock(return_value=None)  # User doesn't exist
        # Ensure execute returns the result synchronously (not a coroutine)
        mock_db_session.execute = AsyncMock(return_value=mock_user_result)
        # Also mock commit for user creation
        mock_db_session.commit = AsyncMock()

        await handle_ai_message(mock_update, mock_context)

        # Verify typing indicator was sent
        mock_context.bot.send_chat_action.assert_called_once()

        # Verify processing message was sent
        mock_message.reply_text.assert_called()

        # Verify AI service was called
        mock_ai_service.generate_response.assert_called_once()

        # Verify processing message was edited with response
        mock_processing_msg.edit_text.assert_called_once()
