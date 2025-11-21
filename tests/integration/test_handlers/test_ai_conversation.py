"""Integration tests for AI conversation flow."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import Update, Message, User as TelegramUser, Chat
from telegram.ext import ContextTypes

from src.bot.handlers.ai_chat import start_ai_chat, handle_ai_message


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
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.edit_message_text = AsyncMock()

        result = await start_ai_chat(mock_update, mock_context)

        # Verify message was sent
        mock_update.callback_query.edit_message_text.assert_called_once()
        # Check that prompt message was sent
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "JARVIS" in call_args[0][0] or "assist" in call_args[0][0].lower()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.ai_chat.get_ai_service")
    async def test_handle_ai_message(self, mock_get_service, mock_update, mock_context):
        """Test handling AI message."""
        # Mock AI service
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response = AsyncMock(
            return_value="Good day, Sir. How may I assist you today?",
        )
        mock_get_service.return_value = mock_ai_service

        mock_update.message.reply_text = AsyncMock()

        result = await handle_ai_message(mock_update, mock_context)

        # Verify AI service was called
        mock_ai_service.generate_response.assert_called_once()

        # Verify response was sent
        mock_update.message.reply_text.assert_called_once()

