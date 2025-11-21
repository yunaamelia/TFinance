"""Unit tests for health check handler."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.handlers.health import get_health_status, health_check_command


class TestHealthCheck:
    """Test health check handler."""

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
    async def test_health_check_command_success(self, mock_update, mock_context, mocker):
        """Test health check command with all services healthy."""
        # Mock database session
        mock_session = mocker.AsyncMock()
        mock_session.execute = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.health.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.ping = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.health.get_redis_client",
            side_effect=get_redis_mock,
        )

        # Mock message reply
        mock_message = MagicMock()
        mock_message.reply_text = mocker.AsyncMock()
        object.__setattr__(mock_update, "message", mock_message)

        await health_check_command(mock_update, mock_context)

        # Verify message was sent
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "Health Check" in call_args[0][0]
        assert "healthy" in call_args[0][0].lower() or "✅" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_health_check_command_database_failure(self, mock_update, mock_context, mocker):
        """Test health check command with database failure."""
        # Mock database session to raise error
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        mocker.patch(
            "src.bot.handlers.health.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.ping = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.health.get_redis_client",
            side_effect=get_redis_mock,
        )

        # Mock message reply
        mock_message = MagicMock()
        mock_message.reply_text = mocker.AsyncMock()
        object.__setattr__(mock_update, "message", mock_message)

        await health_check_command(mock_update, mock_context)

        # Verify message was sent with degraded status
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        assert "degraded" in call_args[0][0].lower() or "⚠️" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_health_check_command_redis_failure(self, mock_update, mock_context, mocker):
        """Test health check command with Redis failure."""
        # Mock database session
        mock_session = mocker.AsyncMock()
        mock_session.execute = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.health.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock Redis to raise error
        async def get_redis_mock():
            raise Exception("Redis connection failed")

        mocker.patch(
            "src.bot.handlers.health.get_redis_client",
            side_effect=get_redis_mock,
        )

        # Mock message reply
        mock_message = MagicMock()
        mock_message.reply_text = mocker.AsyncMock()
        object.__setattr__(mock_update, "message", mock_message)

        await health_check_command(mock_update, mock_context)

        # Verify message was sent (Redis failure doesn't degrade status)
        mock_message.reply_text.assert_called_once()

    def test_get_health_status(self, mocker):
        """Test get_health_status function."""
        mocker.patch("src.bot.handlers.health.settings.environment", "test")

        status = get_health_status()

        assert status["status"] == "healthy"
        assert "timestamp" in status
        assert "uptime_seconds" in status
        assert status["environment"] == "test"
        assert isinstance(status["uptime_seconds"], int)
        assert status["uptime_seconds"] >= 0
