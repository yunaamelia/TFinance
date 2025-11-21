"""Unit tests for navigation handler error cases."""

from unittest.mock import MagicMock

import pytest
from telegram import CallbackQuery, Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.handlers.navigation import handle_back, handle_help
from src.bot.utils.errors import NavigationError


class TestNavigationErrorCases:
    """Test navigation handler error cases."""

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
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_handle_back_navigation_error(self, mock_update, mock_context, mocker):
        """Test handle_back when NavigationError is raised."""

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
        callback_query.from_user = mock_update.effective_user
        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock NavigationService to raise NavigationError
        mock_redis = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.navigation.get_redis_client",
            side_effect=get_redis_mock,
        )

        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(
            side_effect=NavigationError("No back history")
        )
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock handle_home
        mocker.patch(
            "src.bot.handlers.navigation.handle_home",
            new=mocker.AsyncMock(),
        )

        await handle_back(mock_update, mock_context)

        # Should call handle_home as fallback
        callback_query.answer.assert_called()

    @pytest.mark.asyncio
    async def test_handle_back_generic_error(self, mock_update, mock_context, mocker):
        """Test handle_back when generic exception is raised."""

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
        callback_query.from_user = mock_update.effective_user
        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock NavigationService to raise generic exception
        mock_redis = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.navigation.get_redis_client",
            side_effect=get_redis_mock,
        )

        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.navigate_back = mocker.AsyncMock(side_effect=Exception("Database error"))
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock handle_home
        mocker.patch(
            "src.bot.handlers.navigation.handle_home",
            new=mocker.AsyncMock(),
        )

        await handle_back(mock_update, mock_context)

        # Should call handle_home as fallback
        callback_query.answer.assert_called()

    @pytest.mark.asyncio
    async def test_handle_back_to_summary(self, mock_update, mock_context, mocker):
        """Test handle_back navigating to summary screen."""

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.from_user = mock_update.effective_user
        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock NavigationService
        mock_redis = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.navigation.get_redis_client",
            side_effect=get_redis_mock,
        )

        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.navigate_back = mocker.AsyncMock()
        # Mock navigate_back to return previous screen
        mock_nav_service.navigate_back = mocker.AsyncMock(return_value="view_summary")
        # Mock get_navigation_state to return state with previous screen
        mock_nav_service.get_navigation_state = mocker.AsyncMock(
            return_value={"stack": ["main_menu", "view_summary"], "current": "view_summary"}
        )
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock start_summary - it's imported inside the function
        mock_start_summary = mocker.AsyncMock()
        mocker.patch(
            "src.bot.handlers.summary.start_summary",
            new=mock_start_summary,
        )

        await handle_back(mock_update, mock_context)

        # Should call start_summary
        mock_start_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_back_to_ai_chat(self, mock_update, mock_context, mocker):
        """Test handle_back navigating to AI chat screen."""

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.from_user = mock_update.effective_user
        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock NavigationService
        mock_redis = mocker.AsyncMock()

        async def get_redis_mock():
            return mock_redis

        mocker.patch(
            "src.bot.handlers.navigation.get_redis_client",
            side_effect=get_redis_mock,
        )

        mock_nav_service = mocker.AsyncMock()
        mock_nav_service.navigate_back = mocker.AsyncMock()
        # Mock navigate_back to return previous screen
        mock_nav_service.navigate_back = mocker.AsyncMock(return_value="ask_jarvis")
        # Mock get_navigation_state to return state with previous screen
        mock_nav_service.get_navigation_state = mocker.AsyncMock(
            return_value={"stack": ["main_menu", "ask_jarvis"], "current": "ask_jarvis"}
        )
        mocker.patch(
            "src.bot.handlers.navigation.NavigationService",
            return_value=mock_nav_service,
        )

        # Mock start_ai_chat - it's imported inside the function
        mock_start_ai_chat = mocker.AsyncMock()
        mocker.patch(
            "src.bot.handlers.ai_chat.start_ai_chat",
            new=mock_start_ai_chat,
        )

        await handle_back(mock_update, mock_context)

        # Should call start_ai_chat
        mock_start_ai_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_help_exception(self, mock_update, mock_context, mocker):
        """Test handle_help when exception occurs."""

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = mocker.AsyncMock()
        callback_query.edit_message_text = mocker.AsyncMock()
        callback_query.from_user = mock_update.effective_user
        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock NavigationService to raise exception
        async def get_redis_mock():
            raise Exception("Redis error")

        mocker.patch(
            "src.bot.handlers.navigation.get_redis_client",
            side_effect=get_redis_mock,
        )

        await handle_help(mock_update, mock_context)

        # Should still send help message with default screen
        callback_query.edit_message_text.assert_called_once()
