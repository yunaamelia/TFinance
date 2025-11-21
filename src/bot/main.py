"""Main entry point for FinancialAssist Telegram bot."""

import logging
from warnings import filterwarnings

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.warnings import PTBUserWarning

from src.bot.config.settings import settings
from src.bot.middleware.rate_limiter import check_rate_limit
from src.bot.utils.errors import (
    AIServiceError,
    DatabaseError,
    FinancialAssistError,
    NavigationError,
    ValidationError,
)

# Filter PTBUserWarning about CallbackQueryHandler in ConversationHandler
# This warning is informational - callback queries are tracked per update, not per message,
# which is the correct behavior for our use case.
filterwarnings(
    action="ignore",
    message=r".*CallbackQueryHandler.*per_message",
    category=PTBUserWarning,
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

    # Add logging for incoming updates
    async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log incoming updates for debugging."""
        if update.message:
            # Check if this is part of a conversation
            conversation_state = context.user_data.get("_conversation_state")
            state_info = f" [state: {conversation_state}]" if conversation_state else ""
            logger.info(
                f"📨 Received message from user {update.effective_user.id} "
                f"({update.effective_user.first_name}): "
                f"{update.message.text[:50] if update.message.text else 'non-text'}{state_info}"
            )
        elif update.callback_query:
            logger.info(
                f"🔘 Received callback query from user {update.effective_user.id} "
                f"({update.effective_user.first_name}): {update.callback_query.data}"
            )
        else:
            logger.info(f"📥 Received update (type: {update.update_id})")

    # Add update logging handler (lowest priority, runs first)
    application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)
    application.add_handler(CallbackQueryHandler(log_update), group=-1)

    # Register error handler
    application.add_error_handler(error_handler)

    # Register handlers
    from src.bot.handlers.ai_chat import ai_chat_conversation_handler
    from src.bot.handlers.health import health_check_command
    from src.bot.handlers.navigation import handle_back, handle_help, handle_home
    from src.bot.handlers.start import start_command
    from src.bot.handlers.summary import summary_conversation_handler
    from src.bot.handlers.transaction import transaction_conversation_handler

    # Register command handlers FIRST (they have highest priority by default)
    logger.info("Registering command handlers...")
    logger.info(f"  - /start handler function: {start_command}")
    logger.info(f"  - /health handler function: {health_check_command}")
    start_handler = CommandHandler("start", start_command)
    health_handler = CommandHandler("health", health_check_command)
    application.add_handler(start_handler)
    application.add_handler(health_handler)
    logger.info(
        f"✅ Command handlers registered: {len(application.handlers[0])} handlers in group 0"
    )

    # Register conversation handlers BEFORE rate limiting
    # Conversation handlers need to process messages first to maintain state
    logger.info("Registering conversation handlers...")
    application.add_handler(transaction_conversation_handler)
    logger.info("✅ Transaction conversation handler registered")

    # Register conversation handlers (AI chat and summary)
    application.add_handler(ai_chat_conversation_handler)
    logger.info("✅ AI chat conversation handler registered")
    application.add_handler(summary_conversation_handler)
    logger.info("✅ Summary conversation handler registered")

    # Register middleware (rate limiting) AFTER conversation handlers
    # Only apply to non-command, non-conversation messages
    logger.info("Registering rate limiting middleware...")
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, check_rate_limit), group=0
    )
    logger.info("✅ Rate limiting middleware registered")

    # Register navigation handlers (high priority to catch nav: callbacks)
    application.add_handler(CallbackQueryHandler(handle_home, pattern="^nav:home$"))
    application.add_handler(CallbackQueryHandler(handle_back, pattern="^nav:back$"))
    application.add_handler(CallbackQueryHandler(handle_help, pattern="^nav:help$"))

    logger.info("Bot initialized. Starting polling...")
    logger.info("=" * 60)
    logger.info("🤖 Bot is ready and waiting for updates...")
    logger.info("   Try sending /start to your bot in Telegram")
    logger.info("=" * 60)

    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # Clear pending updates on start
        )
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in polling: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
