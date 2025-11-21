"""Integration tests for navigation flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.navigation import handle_back, handle_help, handle_home


class TestNavigationFlow:
    """Test navigation handler flow."""

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
    @patch("src.bot.handlers.navigation.get_redis_client")
    async def test_handle_home(self, mock_get_redis, mock_update, mock_context):
        """Test Home button handler."""
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.answer = AsyncMock()
        mock_update.callback_query.edit_message_text = AsyncMock()

        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        await handle_home(mock_update, mock_context)

        # Verify message was updated
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Welcome" in call_args[0][0] or "Welcome back" in call_args[0][0]

    @pytest.mark.asyncio
    @patch("src.bot.handlers.navigation.get_redis_client")
    async def test_handle_back(self, mock_get_redis, mock_update, mock_context):
        """Test Back button handler."""
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.answer = AsyncMock()
        mock_update.callback_query.edit_message_text = AsyncMock()

        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        # Mock navigation state with previous screen
        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu", "add_transaction"]}')

        await handle_back(mock_update, mock_context)

        # Verify navigation occurred
        mock_update.callback_query.edit_message_text.assert_called()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.navigation.get_redis_client")
    async def test_handle_help(self, mock_get_redis, mock_update, mock_context):
        """Test Help button handler."""
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.answer = AsyncMock()
        mock_update.callback_query.edit_message_text = AsyncMock()

        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis
        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu"], "current": "main_menu"}')

        await handle_help(mock_update, mock_context)

        # Verify help message was sent
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Help" in call_args[0][0]
