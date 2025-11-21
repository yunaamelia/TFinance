"""Unit tests for main bot entry point."""

from unittest.mock import MagicMock, patch

import pytest
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.main import error_handler, main


class TestErrorHandler:
    """Test error handler."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        from telegram import Chat, Message
        from telegram import User as TelegramUser

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
        return context

    @pytest.mark.asyncio
    async def test_error_handler_validation_error(self, mock_update, mock_context, mocker):
        """Test error handler with ValidationError."""
        from src.bot.utils.errors import ValidationError

        mock_context.error = ValidationError("Invalid amount", field="amount")
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "Invalid amount" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_error_handler_database_error(self, mock_update, mock_context, mocker):
        """Test error handler with DatabaseError."""
        from src.bot.utils.errors import DatabaseError

        mock_context.error = DatabaseError("Connection failed", operation="query")
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "Database error" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_error_handler_ai_service_error(self, mock_update, mock_context, mocker):
        """Test error handler with AIServiceError."""
        from src.bot.utils.errors import AIServiceError

        mock_context.error = AIServiceError("Service unavailable", status_code=503)
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "AI service" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_error_handler_generic_error(self, mock_update, mock_context, mocker):
        """Test error handler with generic error."""
        mock_context.error = Exception("Generic error")
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "error occurred" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_error_handler_no_message(self, mock_update, mock_context, mocker):
        """Test error handler when update has no message."""
        from telegram import Update

        from src.bot.utils.errors import ValidationError

        mock_context.error = ValidationError("Test error")
        # Create update without message
        update_no_message = Update(update_id=2)

        # Should not raise exception
        await error_handler(update_no_message, mock_context)

    @pytest.mark.asyncio
    async def test_error_handler_navigation_error(self, mock_update, mock_context, mocker):
        """Test error handler with NavigationError."""
        from src.bot.utils.errors import NavigationError

        mock_context.error = NavigationError("No back history")
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "No back history" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_error_handler_financial_assist_error(self, mock_update, mock_context, mocker):
        """Test error handler with FinancialAssistError."""
        from src.bot.utils.errors import FinancialAssistError

        mock_context.error = FinancialAssistError("Custom error")
        # Mock effective_message.reply_text
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        await error_handler(mock_update, mock_context)

        reply_text_mock.assert_called_once()
        call_args = reply_text_mock.call_args
        assert "Custom error" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_error_handler_reply_fails(self, mock_update, mock_context, mocker):
        """Test error handler when reply fails."""
        from src.bot.utils.errors import ValidationError

        mock_context.error = ValidationError("Test error")
        # Mock effective_message.reply_text to raise error
        reply_text_mock = mocker.AsyncMock(side_effect=Exception("Send failed"))
        mocker.patch(
            "telegram.Update.effective_message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        # Should handle error gracefully
        await error_handler(mock_update, mock_context)

        # Should have attempted to send message
        reply_text_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handler_no_update(self, mock_context, mocker):
        """Test error handler when update is None."""
        from src.bot.utils.errors import ValidationError

        mock_context.error = ValidationError("Test error")

        # Should handle None update gracefully
        await error_handler(None, mock_context)


class TestMain:
    """Test main function."""

    @patch("src.bot.main.Application")
    @patch("src.bot.main.settings")
    def test_main_initialization(self, mock_settings, mock_application_class, mocker):
        """Test main function initialization."""
        # Mock settings
        mock_settings.telegram_bot_token = "test_token"

        # Mock Application builder
        mock_application = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_application
        mock_application_class.builder.return_value = mock_builder

        # Mock run_polling to avoid actually starting the bot
        mock_application.run_polling = MagicMock(side_effect=KeyboardInterrupt())

        # Call main
        try:
            main()
        except KeyboardInterrupt:
            pass  # Expected

        # Verify application was created
        mock_application_class.builder.assert_called_once()

    @patch("src.bot.main.Application")
    @patch("src.bot.main.settings")
    def test_main_exception_handling(self, mock_settings, mock_application_class, mocker):
        """Test main function exception handling."""
        # Mock settings
        mock_settings.telegram_bot_token = "test_token"

        # Mock Application
        mock_application = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_application
        mock_application_class.builder.return_value = mock_builder

        # Mock run_polling to raise exception
        mock_application.run_polling = MagicMock(side_effect=Exception("Fatal error"))

        # Mock logger
        logger_mock = mocker.patch("src.bot.main.logger")

        # Call main - should handle exception
        with pytest.raises(Exception, match="Fatal error"):
            main()

        # Verify error was logged
        logger_mock.error.assert_called()

    @patch("src.bot.main.Application")
    @patch("src.bot.main.settings")
    def test_main_keyboard_interrupt(self, mock_settings, mock_application_class, mocker):
        """Test main function KeyboardInterrupt handling."""
        # Mock settings
        mock_settings.telegram_bot_token = "test_token"

        # Mock Application
        mock_application = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_application
        mock_application_class.builder.return_value = mock_builder

        # Mock run_polling to raise KeyboardInterrupt
        mock_application.run_polling = MagicMock(side_effect=KeyboardInterrupt())

        # Mock logger
        logger_mock = mocker.patch("src.bot.main.logger")

        # Call main - should handle KeyboardInterrupt gracefully
        try:
            main()
        except KeyboardInterrupt:
            pass  # Expected

        # Verify info was logged
        logger_mock.info.assert_called()
