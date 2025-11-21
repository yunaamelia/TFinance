"""Start command handler."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.config.settings import get_redis_client
from src.bot.keyboards.main_menu import build_main_menu_keyboard
from src.bot.services.navigation_service import NavigationService

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command.

    Args:
        update: Telegram update object
        context: Bot context
    """
    user = update.effective_user

    # Reset navigation state
    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)
        await navigation_service.reset_navigation(user.id)
    except Exception as e:
        logger.error(f"Error resetting navigation: {e}", exc_info=True)

    welcome_message = (
        f"👋 Welcome, {user.first_name}!\n\n"
        "I'm your AI Financial Assistant powered by JARVIS.\n"
        "I can help you:\n"
        "• 💰 Record income and expenses\n"
        "• 📊 View financial summaries\n"
        "• 🤖 Get AI-powered financial insights\n\n"
        "Choose an option below to get started:"
    )

    keyboard = build_main_menu_keyboard()

    await update.message.reply_text(
        welcome_message,
        reply_markup=keyboard,
    )
