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
    logger.info(f"🚀 /start command received from user {update.effective_user.id}")
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

    try:
        logger.info(f"📤 Sending welcome message to user {user.id}")
        if not update.message:
            logger.error("❌ update.message is None!")
            return

        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
        )
        logger.info(f"✅ Welcome message sent successfully to user {user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send welcome message: {e}", exc_info=True)
        # Try to send error message
        try:
            if update.message:
                await update.message.reply_text("❌ An error occurred. Please try again later.")
        except Exception as e2:
            logger.error(f"❌ Failed to send error message: {e2}", exc_info=True)
