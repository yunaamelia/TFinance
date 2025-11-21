"""Unit tests for navigation service complete coverage."""

from unittest.mock import AsyncMock

import pytest

from src.bot.services.navigation_service import NavigationService
from src.bot.utils.errors import NavigationError


class TestNavigationServiceComplete:
    """Test navigation service for complete coverage."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def navigation_service(self, mock_redis):
        """Create navigation service instance."""
        return NavigationService(mock_redis)

    @pytest.mark.asyncio
    async def test_navigate_back_with_previous_screen(self, navigation_service, mock_redis):
        """Test navigate_back with valid previous screen."""
        mock_redis.get = AsyncMock(
            return_value='{"stack": ["main_menu", "view_summary", "test_screen"], "current": "test_screen"}'
        )
        mock_redis.set = AsyncMock()

        result = await navigation_service.navigate_back(123)

        assert result == "view_summary"
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_navigate_back_redis_error(self, navigation_service, mock_redis):
        """Test navigate_back when Redis raises error."""
        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

        with pytest.raises(NavigationError):
            await navigation_service.navigate_back(123)

    @pytest.mark.asyncio
    async def test_build_keyboard_with_additional_buttons(self, navigation_service, mock_redis):
        """Test build_keyboard with additional buttons."""
        from telegram import InlineKeyboardButton

        mock_redis.get = AsyncMock(
            return_value='{"stack": ["main_menu", "test_screen"], "current": "test_screen"}'
        )

        additional_buttons = [[InlineKeyboardButton("Test", callback_data="test")]]
        keyboard = await navigation_service.build_keyboard(123, "test_screen", additional_buttons)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0
