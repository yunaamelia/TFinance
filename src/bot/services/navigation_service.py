"""Navigation service for managing navigation state and keyboard building."""

import json
import logging
from typing import Dict, List, Optional

import redis.asyncio as redis
from telegram import InlineKeyboardMarkup

from src.bot.keyboards.navigation import build_navigation_row
from src.bot.utils.errors import NavigationError

logger = logging.getLogger(__name__)


class NavigationService:
    """Service for navigation state management."""

    def __init__(self, redis_client: redis.Redis):
        """Initialize NavigationService.

        Args:
            redis_client: Redis client for state persistence
        """
        self.redis = redis_client
        self.ttl = 3600  # 1 hour TTL for navigation state

    async def get_navigation_state(self, user_id: int) -> Dict:
        """Get user's current navigation state.

        Args:
            user_id: User ID

        Returns:
            Dictionary with navigation state (stack, current screen)
        """
        try:
            if self.redis:
                cache_key = f"navigation:{user_id}"
                state_data = await self.redis.get(cache_key)
                if state_data:
                    return json.loads(state_data)

            # Return default state
            return {
                "stack": ["main_menu"],
                "current": "main_menu",
            }
        except Exception as e:
            logger.error(f"Error getting navigation state: {e}", exc_info=True)
            return {
                "stack": ["main_menu"],
                "current": "main_menu",
            }

    async def navigate_to(self, user_id: int, screen: str) -> None:
        """Navigate to a new screen.

        Args:
            user_id: User ID
            screen: Screen identifier (e.g., "add_transaction", "view_summary")

        Side Effects:
            Updates navigation stack in Redis
        """
        try:
            if not self.redis:
                return

            cache_key = f"navigation:{user_id}"
            state = await self.get_navigation_state(user_id)

            stack: List[str] = state.get("stack", ["main_menu"])

            # Don't add if already at this screen
            if stack and stack[-1] == screen:
                return

            # Add new screen to stack
            stack.append(screen)

            # Limit stack size (keep last 10 screens)
            if len(stack) > 10:
                stack = stack[-10:]

            # Update state
            new_state = {
                "stack": stack,
                "current": screen,
            }

            await self.redis.set(
                cache_key,
                json.dumps(new_state),
                ex=self.ttl,
            )

            logger.debug(f"Navigation: user {user_id} -> {screen}")

        except Exception as e:
            logger.error(f"Error navigating to screen: {e}", exc_info=True)

    async def navigate_back(self, user_id: int) -> str:
        """Navigate back to previous screen.

        Args:
            user_id: User ID

        Returns:
            Previous screen identifier

        Raises:
            NavigationError: If already at main menu
        """
        try:
            if not self.redis:
                raise NavigationError("Navigation service not available")

            cache_key = f"navigation:{user_id}"
            state = await self.get_navigation_state(user_id)

            stack: List[str] = state.get("stack", ["main_menu"])

            # Can't go back from main menu
            if len(stack) <= 1:
                raise NavigationError("Already at main menu")

            # Remove current screen
            stack.pop()

            # Get previous screen
            previous_screen = stack[-1] if stack else "main_menu"

            # Update state
            new_state = {
                "stack": stack,
                "current": previous_screen,
            }

            await self.redis.set(
                cache_key,
                json.dumps(new_state),
                ex=self.ttl,
            )

            logger.debug(f"Navigation back: user {user_id} -> {previous_screen}")

            return previous_screen

        except NavigationError:
            raise
        except Exception as e:
            logger.error(f"Error navigating back: {e}", exc_info=True)
            raise NavigationError(f"Failed to navigate back: {str(e)}") from e

    async def build_keyboard(
        self,
        user_id: int,
        screen: str,
        additional_buttons: Optional[List] = None,
    ) -> InlineKeyboardMarkup:
        """Build inline keyboard for a screen with navigation buttons.

        Args:
            user_id: User ID
            screen: Screen identifier
            additional_buttons: Additional button rows to include

        Returns:
            InlineKeyboardMarkup with contextually appropriate buttons
        """
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup

        buttons = []

        # Add additional buttons if provided
        if additional_buttons:
            buttons.extend(additional_buttons)

        # Get navigation state to determine if back button should be shown
        state = await self.get_navigation_state(user_id)
        stack = state.get("stack", ["main_menu"])
        can_go_back = len(stack) > 1 and stack[-1] != "main_menu"

        # Add navigation row
        show_back = can_go_back and screen != "main_menu"
        nav_row = build_navigation_row(
            show_back=show_back,
            show_home=True,
            show_help=True,
        )
        if nav_row:
            buttons.append(nav_row)

        return InlineKeyboardMarkup(buttons)

    async def reset_navigation(self, user_id: int) -> None:
        """Reset navigation state to main menu.

        Args:
            user_id: User ID
        """
        try:
            if self.redis:
                cache_key = f"navigation:{user_id}"
                state = {
                    "stack": ["main_menu"],
                    "current": "main_menu",
                }
                await self.redis.set(
                    cache_key,
                    json.dumps(state),
                    ex=self.ttl,
                )
                logger.debug(f"Navigation reset: user {user_id}")
        except Exception as e:
            logger.error(f"Error resetting navigation: {e}", exc_info=True)

