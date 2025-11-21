"""Unit tests for navigation service final coverage."""

from unittest.mock import AsyncMock

import pytest

from src.bot.services.navigation_service import NavigationService
from src.bot.utils.errors import NavigationError


class TestNavigationServiceFinal:
    """Test navigation service for final coverage."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def navigation_service(self, mock_redis):
        """Create navigation service instance."""
        return NavigationService(mock_redis)

    @pytest.mark.asyncio
    async def test_navigate_to_no_redis_set_error(self, navigation_service, mock_redis):
        """Test navigate_to when Redis set fails."""
        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu"], "current": "main_menu"}')
        mock_redis.set = AsyncMock(side_effect=Exception("Set error"))

        # Should not raise exception
        await navigation_service.navigate_to(123, "test_screen")

    @pytest.mark.asyncio
    async def test_navigate_back_no_previous_screen(self, navigation_service, mock_redis):
        """Test navigate_back when no previous screen."""
        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu"], "current": "main_menu"}')

        with pytest.raises(NavigationError, match="Already at main menu"):
            await navigation_service.navigate_back(123)

    @pytest.mark.asyncio
    async def test_build_keyboard_no_redis(self, navigation_service):
        """Test build_keyboard when Redis is None."""
        navigation_service.redis = None

        keyboard = await navigation_service.build_keyboard(123, "test_screen")

        assert keyboard is not None
