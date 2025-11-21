"""Unit tests for start handler final coverage."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.handlers.start import start_command


class TestStartHandlerFinal:
    """Test start handler for final coverage."""

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
        context = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_start_command_no_message(self, mock_update, mock_context, mocker):
        """Test start_command when update.message is None."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.start.get_redis_client",
            side_effect=get_redis_mock,
        )

        # Mock NavigationService
        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.reset_navigation = mocker.AsyncMock()
        mocker.patch(
            "src.bot.handlers.start.NavigationService",
            return_value=mock_nav_service,
        )

        # Create update without message but with effective_user
        from telegram import Update

        update_no_message = Update(update_id=2)
        # Set effective_user manually
        object.__setattr__(update_no_message, "effective_user", mock_update.effective_user)
        object.__setattr__(update_no_message, "message", None)

        # Should handle gracefully (will return early when message is None)
        await start_command(update_no_message, mock_context)
