"""Unit tests for start command error cases."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.handlers.start import start_command


class TestStartCommandErrorCases:
    """Test start command error handling."""

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
    async def test_start_command_send_error(self, mock_update, mock_context, mocker):
        """Test start command when sending message fails."""
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

        # Mock message reply_text to raise error
        reply_text_mock = mocker.AsyncMock(side_effect=Exception("Send failed"))
        mocker.patch(
            "telegram.Update.message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await start_command(mock_update, mock_context)

        # Should have attempted to send welcome message (may fail and try error message)
        # The function handles errors gracefully

    @pytest.mark.asyncio
    async def test_start_command_error_message_fails(self, mock_update, mock_context, mocker):
        """Test start command when both welcome and error messages fail."""
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

        # Mock message reply_text to always raise error
        reply_text_mock = mocker.AsyncMock(side_effect=Exception("Send failed"))
        mocker.patch(
            "telegram.Update.message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        # Should handle gracefully without raising
        await start_command(mock_update, mock_context)
