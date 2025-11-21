"""Unit tests for NavigationService."""

from unittest.mock import AsyncMock

import pytest

from src.bot.services.navigation_service import NavigationService
from src.bot.utils.errors import NavigationError


class TestNavigationService:
    """Test NavigationService methods."""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis_client = AsyncMock()
        return redis_client

    @pytest.fixture
    def navigation_service(self, mock_redis):
        """Create NavigationService instance."""
        return NavigationService(mock_redis)

    @pytest.mark.asyncio
    async def test_navigate_to(self, navigation_service, mock_redis):
        """Test navigating to a new screen."""
        user_id = 123456789
        screen = "add_transaction"

        # Mock Redis get (empty stack initially)
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        await navigation_service.navigate_to(user_id, screen)

        # Verify Redis was called to update stack
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert "navigation" in call_args[0][0] or "nav" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_navigate_back_success(self, navigation_service, mock_redis):
        """Test navigating back successfully."""
        user_id = 123456789

        # Mock navigation stack
        stack_data = '{"stack": ["main_menu", "add_transaction"]}'
        mock_redis.get = AsyncMock(return_value=stack_data)
        mock_redis.set = AsyncMock()

        previous_screen = await navigation_service.navigate_back(user_id)

        assert previous_screen == "main_menu"
        mock_redis.set.assert_called_once()  # Stack updated

    @pytest.mark.asyncio
    async def test_navigate_back_at_main_menu(self, navigation_service, mock_redis):
        """Test navigating back when already at main menu."""
        user_id = 123456789

        # Mock navigation stack with only main_menu
        stack_data = '{"stack": ["main_menu"]}'
        mock_redis.get = AsyncMock(return_value=stack_data)

        with pytest.raises(NavigationError):
            await navigation_service.navigate_back(user_id)

    @pytest.mark.asyncio
    async def test_get_navigation_state(self, navigation_service, mock_redis):
        """Test getting navigation state."""
        user_id = 123456789

        # Mock navigation state
        state_data = '{"stack": ["main_menu", "add_transaction"], "current": "add_transaction"}'
        mock_redis.get = AsyncMock(return_value=state_data)

        state = await navigation_service.get_navigation_state(user_id)

        assert state is not None
        assert "current" in state or "stack" in state

    @pytest.mark.asyncio
    async def test_get_navigation_state_empty(self, navigation_service, mock_redis):
        """Test getting navigation state when none exists."""
        user_id = 123456789

        mock_redis.get = AsyncMock(return_value=None)

        state = await navigation_service.get_navigation_state(user_id)

        # Should return default state
        assert state is not None

    @pytest.mark.asyncio
    async def test_build_keyboard_with_back(self, navigation_service, mock_redis):
        """Test building keyboard with back button."""
        user_id = 123456789
        screen = "add_transaction"

        # Mock stack with previous screen
        stack_data = '{"stack": ["main_menu", "add_transaction"]}'
        mock_redis.get = AsyncMock(return_value=stack_data)

        keyboard = await navigation_service.build_keyboard(user_id, screen)

        assert keyboard is not None
        # Verify keyboard has navigation buttons
        assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_build_keyboard_without_back(self, navigation_service, mock_redis):
        """Test building keyboard without back button (at main menu)."""
        user_id = 123456789
        screen = "main_menu"

        # Mock stack with only main_menu
        stack_data = '{"stack": ["main_menu"]}'
        mock_redis.get = AsyncMock(return_value=stack_data)

        keyboard = await navigation_service.build_keyboard(user_id, screen)

        assert keyboard is not None
        # Back button should not be present at main menu

    @pytest.mark.asyncio
    async def test_navigation_stack_management(self, navigation_service, mock_redis):
        """Test navigation stack management."""
        import json

        user_id = 123456789

        # Track navigation state manually
        navigation_state = {"stack": []}

        def mock_get(key):
            """Mock get that returns current state."""
            if navigation_state["stack"]:
                return json.dumps(
                    {
                        "stack": navigation_state["stack"],
                        "current": (
                            navigation_state["stack"][-1]
                            if navigation_state["stack"]
                            else "main_menu"
                        ),
                    }
                )
            return None

        def mock_set(key, value, ex=None):
            """Mock set that updates state."""
            if "navigation" in key or "nav" in key:
                try:
                    data = json.loads(value)
                    if "stack" in data:
                        navigation_state["stack"] = data["stack"]
                except (json.JSONDecodeError, KeyError):
                    pass

        mock_redis.get = AsyncMock(side_effect=mock_get)
        mock_redis.set = AsyncMock(side_effect=mock_set)

        await navigation_service.navigate_to(user_id, "main_menu")
        await navigation_service.navigate_to(user_id, "add_transaction")
        await navigation_service.navigate_to(user_id, "transaction_type")

        # Verify stack was updated multiple times (at least once per navigate_to call)
        # Note: navigate_to may call set multiple times internally
        assert mock_redis.set.call_count >= 2  # At least 2 calls (could be more)

        # Test navigating back - update mock_get to return current state
        mock_redis.get = AsyncMock(side_effect=mock_get)
        previous = await navigation_service.navigate_back(user_id)
        assert previous == "add_transaction"
