"""Unit tests for navigation service edge cases."""

from unittest.mock import AsyncMock

import pytest

from src.bot.services.navigation_service import NavigationService


class TestNavigationServiceEdgeCases:
    """Test navigation service edge cases."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def navigation_service(self, mock_redis):
        """Create navigation service instance."""
        return NavigationService(mock_redis)

    @pytest.mark.asyncio
    async def test_navigate_to_no_redis(self, navigation_service):
        """Test navigate_to when Redis is None."""
        navigation_service.redis = None

        # Should not raise exception
        await navigation_service.navigate_to(123, "test_screen")

    @pytest.mark.asyncio
    async def test_navigate_to_already_at_screen(self, navigation_service, mock_redis):
        """Test navigate_to when already at target screen."""
        # Mock get_navigation_state to return current screen
        mock_redis.get = AsyncMock(
            return_value='{"stack": ["main_menu", "test_screen"], "current": "test_screen"}'
        )

        await navigation_service.navigate_to(123, "test_screen")

        # Should not call set (already at screen)
        mock_redis.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_navigate_to_stack_limit(self, navigation_service, mock_redis):
        """Test navigate_to when stack exceeds limit."""
        # Mock get_navigation_state to return large stack
        large_stack = ["main_menu"] + [f"screen_{i}" for i in range(15)]
        mock_redis.get = AsyncMock(
            return_value=f'{{"stack": {large_stack}, "current": "screen_14"}}'
        )

        await navigation_service.navigate_to(123, "new_screen")

        # Should limit stack to 10
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        state_data = eval(call_args[0][1])  # Parse JSON string
        assert len(state_data["stack"]) <= 10

    @pytest.mark.asyncio
    async def test_navigate_to_exception(self, navigation_service, mock_redis):
        """Test navigate_to when exception occurs."""
        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

        # Should not raise exception
        await navigation_service.navigate_to(123, "test_screen")

    @pytest.mark.asyncio
    async def test_navigate_back_empty_stack(self, navigation_service, mock_redis):
        """Test navigate_back with empty stack."""
        from src.bot.utils.errors import NavigationError

        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu"], "current": "main_menu"}')

        # Should raise NavigationError when already at main menu
        with pytest.raises(NavigationError):
            await navigation_service.navigate_back(123)

    @pytest.mark.asyncio
    async def test_navigate_back_exception(self, navigation_service, mock_redis):
        """Test navigate_back when exception occurs."""
        from src.bot.utils.errors import NavigationError

        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

        with pytest.raises(NavigationError):
            await navigation_service.navigate_back(123)

    @pytest.mark.asyncio
    async def test_build_keyboard_with_back(self, navigation_service, mock_redis):
        """Test build_keyboard with back button."""
        mock_redis.get = AsyncMock(
            return_value='{"stack": ["main_menu", "test_screen"], "current": "test_screen"}'
        )

        keyboard = await navigation_service.build_keyboard(123, "test_screen")

        assert keyboard is not None
        # Check that keyboard has buttons
        assert hasattr(keyboard, "inline_keyboard")

    @pytest.mark.asyncio
    async def test_build_keyboard_without_back(self, navigation_service, mock_redis):
        """Test build_keyboard without back button."""
        mock_redis.get = AsyncMock(return_value='{"stack": ["main_menu"], "current": "main_menu"}')

        keyboard = await navigation_service.build_keyboard(123, "main_menu")

        assert keyboard is not None

    @pytest.mark.asyncio
    async def test_reset_navigation(self, navigation_service, mock_redis):
        """Test reset_navigation."""
        await navigation_service.reset_navigation(123)

        # reset_navigation sets the navigation state to main_menu
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == "navigation:123"

    @pytest.mark.asyncio
    async def test_reset_navigation_no_redis(self, navigation_service):
        """Test reset_navigation when Redis is None."""
        navigation_service.redis = None

        # Should not raise exception
        await navigation_service.reset_navigation(123)
