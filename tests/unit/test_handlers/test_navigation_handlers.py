"""Unit tests for navigation handlers."""

from unittest.mock import MagicMock

import pytest
from telegram import CallbackQuery, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.navigation import get_help_message, handle_back, handle_help, handle_home


class TestGetHelpMessage:
    """Test get_help_message function."""

    def test_get_help_message_main_menu(self):
        """Test getting help message for main menu."""
        message = get_help_message("main_menu")

        assert "Main Menu" in message or "main menu" in message.lower()
        assert "Add Transaction" in message or "add transaction" in message.lower()

    def test_get_help_message_add_transaction(self):
        """Test getting help message for add transaction."""
        message = get_help_message("add_transaction")

        assert "Add Transaction" in message or "add transaction" in message.lower()
        assert "amount" in message.lower()

    def test_get_help_message_view_summary(self):
        """Test getting help message for view summary."""
        message = get_help_message("view_summary")

        assert "View Summary" in message or "view summary" in message.lower()
        assert "period" in message.lower() or "time" in message.lower()

    def test_get_help_message_ask_jarvis(self):
        """Test getting help message for ask jarvis."""
        message = get_help_message("ask_jarvis")

        assert "JARVIS" in message or "jarvis" in message.lower()
        assert "AI" in message or "ai" in message.lower()

    def test_get_help_message_default(self):
        """Test getting default help message."""
        message = get_help_message("unknown_screen")

        assert "Help" in message or "help" in message.lower()
        assert "Home" in message or "home" in message.lower()


class TestNavigationHandlers:
    """Test navigation handlers."""

    @pytest.fixture
    def mock_update(self, mocker):
        """Create mock Telegram update."""
        telegram_user = TelegramUser(
            id=123456789,
            first_name="Test",
            is_bot=False,
        )
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.from_user = telegram_user
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
        update = Update(update_id=1, callback_query=callback_query)
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        return MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    @pytest.mark.asyncio
    async def test_handle_home(self, mock_update, mock_context, mocker):
        """Test handle_home function."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        # Mock NavigationService
        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.reset_navigation = mocker.AsyncMock()
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        await handle_home(mock_update, mock_context)

        # Verify callback was answered
        mock_update.callback_query.answer.assert_called_once()
        # Verify message was edited
        mock_update.callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_back_success(self, mock_update, mock_context, mocker):
        """Test handle_back function with navigation history."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(
            return_value='{"stack": ["main_menu", "add_transaction"], "current": "add_transaction"}'
        )
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        # Mock NavigationService - navigate_back should return previous screen
        mock_nav_service = mocker.MagicMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(return_value="main_menu")
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock build_main_menu_keyboard
        mock_keyboard = MagicMock()
        mocker.patch(
            "src.bot.handlers.navigation.build_main_menu_keyboard",
            return_value=mock_keyboard,
        )

        await handle_back(mock_update, mock_context)

        # Verify callback was answered (may be called multiple times if handle_home is called)
        assert mock_update.callback_query.answer.call_count >= 1
        # Verify message was edited
        assert mock_update.callback_query.edit_message_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_handle_back_no_history(self, mock_update, mock_context, mocker):
        """Test handle_back function with no navigation history."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value=None)
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        # Mock NavigationService - navigate_back returns None when no history
        mock_nav_service = mocker.MagicMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock build_main_menu_keyboard
        mock_keyboard = MagicMock()
        mocker.patch(
            "src.bot.handlers.navigation.build_main_menu_keyboard",
            return_value=mock_keyboard,
        )

        await handle_back(mock_update, mock_context)

        # Verify callback was answered (may be called multiple times if handle_home is called)
        assert mock_update.callback_query.answer.call_count >= 1
        # Should still edit message (to main menu)
        assert mock_update.callback_query.edit_message_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_handle_help(self, mock_update, mock_context, mocker):
        """Test handle_help function."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value='{"current": "main_menu"}')
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        await handle_help(mock_update, mock_context)

        # Verify callback was answered
        mock_update.callback_query.answer.assert_called_once()
        # Verify message was edited with help text
        mock_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_update.callback_query.edit_message_text.call_args
        assert "Help" in call_args[0][0] or "help" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_handle_back_with_different_screens(self, mock_update, mock_context, mocker):
        """Test handle_back function routing to different screens."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value='{"current": "add_transaction"}')
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        # Mock NavigationService
        mock_nav_service = mocker.MagicMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(return_value="add_transaction")
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock start_transaction handler (imported inside function)
        mock_start_transaction = mocker.AsyncMock()
        mocker.patch(
            "src.bot.handlers.transaction.start_transaction",
            mock_start_transaction,
        )

        await handle_back(mock_update, mock_context)

        # Verify callback was answered
        assert mock_update.callback_query.answer.call_count >= 1
        # Verify start_transaction was called
        mock_start_transaction.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_back_with_navigation_error(self, mock_update, mock_context, mocker):
        """Test handle_back function with NavigationError."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        # Mock NavigationService to raise NavigationError
        from src.bot.utils.errors import NavigationError

        mock_nav_service = mocker.MagicMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(
            side_effect=NavigationError("No back history")
        )
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock build_main_menu_keyboard
        mock_keyboard = MagicMock()
        mocker.patch(
            "src.bot.handlers.navigation.build_main_menu_keyboard",
            return_value=mock_keyboard,
        )

        await handle_back(mock_update, mock_context)

        # Verify callback was answered (with alert)
        assert mock_update.callback_query.answer.call_count >= 1
        # Should still edit message (to main menu)
        assert mock_update.callback_query.edit_message_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_handle_help_unknown_screen(self, mock_update, mock_context, mocker):
        """Test handle_help function with unknown screen."""
        # Mock Redis
        mock_redis = mocker.AsyncMock()
        mock_redis.get = mocker.AsyncMock(return_value='{"current": "unknown_screen"}')
        mocker.patch("src.bot.handlers.navigation.get_redis_client", return_value=mock_redis)

        await handle_help(mock_update, mock_context)

        # Verify callback was answered
        mock_update.callback_query.answer.assert_called_once()
        # Verify message was edited with default help text
        mock_update.callback_query.edit_message_text.assert_called_once()
