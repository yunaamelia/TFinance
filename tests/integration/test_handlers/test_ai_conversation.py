"""Integration tests for AI conversation flow."""

from unittest.mock import MagicMock

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
    async def test_start_ai_chat(self, mock_update, mock_context, mocker):
        """Test starting AI chat conversation."""
        from telegram import CallbackQuery

        # Create proper callback query mock using mocker
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
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
    async def test_handle_ai_message(
        self,
        mock_update,
        mock_context,
        mocker,
    ):
        """Test handling AI message."""
        # Mock AI service using mocker - patch the function that returns the service
        mock_ai_service = mocker.MagicMock()
        mock_ai_service.generate_response = mocker.AsyncMock(
            return_value="Good day, Sir. How may I assist you today?",
        )
        # Patch the get_ai_service function to return our mock
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

        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "Hello JARVIS"
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        # Mock processing message (returned by reply_text)
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = mocker.AsyncMock()
        mock_processing_msg.delete = mocker.AsyncMock()

        # Mock reply_text using mocker's AsyncMock
        mock_message.reply_text = mocker.AsyncMock(return_value=mock_processing_msg)

        # Mock context.bot.send_chat_action
        mock_context.bot = MagicMock()
        mock_context.bot.send_chat_action = mocker.AsyncMock()

        # Mock User model query
        mock_user_result = MagicMock()
        # scalar_one_or_none() is synchronous, not async
        mock_user_result.scalar_one_or_none.return_value = None  # User doesn't exist

        # execute() is async, use mocker's AsyncMock
        mock_db_session.execute = mocker.AsyncMock(return_value=mock_user_result)
        # Also mock commit and add for user creation
        mock_db_session.commit = mocker.AsyncMock()
        mock_db_session.add = mocker.MagicMock()  # add() is synchronous

        await handle_ai_message(mock_update, mock_context)

        # Verify typing indicator was sent
        mock_context.bot.send_chat_action.assert_called_once()

        # Verify processing message was sent
        mock_message.reply_text.assert_called()

        # Verify AI service was called
        mock_ai_service.generate_response.assert_called_once()

        # Verify processing message was edited with response
        mock_processing_msg.edit_text.assert_called_once()
