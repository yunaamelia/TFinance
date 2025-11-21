"""Main entry point for FinancialAssist Telegram bot."""

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes

from src.bot.config.settings import settings
from src.bot.middleware.rate_limiter import check_rate_limit
from src.bot.utils.errors import (
    AIServiceError,
    DatabaseError,
    FinancialAssistError,
    NavigationError,
    ValidationError,
)

logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram application."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)

    # Determine error type and provide user-friendly message
    error = context.error
    user_message = "❌ An error occurred. Please try again later."

    if isinstance(error, ValidationError):
        user_message = f"⚠️ {error.message}"
        if error.field:
            user_message += f" (Field: {error.field})"
    elif isinstance(error, DatabaseError):
        user_message = "❌ Database error. Please try again."
        logger.error(f"Database error in operation: {error.operation}")
    elif isinstance(error, AIServiceError):
        user_message = "🤖 AI service temporarily unavailable. Please try again later."
        logger.error(f"AI service error: {error.message} (Status: {error.status_code})")
    elif isinstance(error, NavigationError):
        user_message = f"🧭 {error.message}"
    elif isinstance(error, FinancialAssistError):
        user_message = f"❌ {error.message}"

    # Try to send error message to user
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(user_message)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


def main():
    """Initialize and run the Telegram bot."""
    logger.info("Starting FinancialAssist bot...")

    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Register middleware (rate limiting)
    from telegram.ext import MessageHandler, filters

    application.add_handler(MessageHandler(filters.ALL, check_rate_limit), group=0)

    # Register error handler
    application.add_error_handler(error_handler)

    # Register handlers
    from telegram.ext import CallbackQueryHandler, CommandHandler

    from src.bot.handlers.ai_chat import ai_chat_conversation_handler
    from src.bot.handlers.health import health_check_command
    from src.bot.handlers.navigation import handle_back, handle_help, handle_home
    from src.bot.handlers.start import start_command
    from src.bot.handlers.summary import summary_conversation_handler
    from src.bot.handlers.transaction import transaction_conversation_handler

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("health", health_check_command))
    application.add_handler(transaction_conversation_handler)
    application.add_handler(ai_chat_conversation_handler)
    application.add_handler(summary_conversation_handler)

    # Register navigation handlers (high priority to catch nav: callbacks)
    application.add_handler(CallbackQueryHandler(handle_home, pattern="^nav:home$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^nav:back$"))
    application.add_handler(CallbackQueryHandler(handle_help, pattern="^nav:help$"))

    logger.info("Bot initialized. Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
