"""AI chat handlers for JARVIS conversation."""

import logging
import warnings

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.warnings import PTBUserWarning

from src.bot.config.persona import JARVIS_PERSONA_V1
from src.bot.config.settings import get_async_session_maker, get_redis_client
from src.bot.keyboards.main_menu import build_main_menu_keyboard
from src.bot.keyboards.navigation import build_navigation_row
from src.bot.models.user import User
from src.bot.services.ai_service import OpenAIService
from src.bot.services.navigation_service import NavigationService
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import AIServiceError

# Filter PTBUserWarning about CallbackQueryHandler in ConversationHandler
# This warning is informational and can be safely ignored
warnings.simplefilter("ignore", PTBUserWarning)

logger = logging.getLogger(__name__)

# Conversation state
AI_CHAT = 1


def get_ai_service() -> OpenAIService:
    """Get AI service instance.

    Returns:
        OpenAIService: Configured AI service
    """
    return OpenAIService(JARVIS_PERSONA_V1)


async def start_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start AI chat conversation.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Update navigation state
    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)
        await navigation_service.navigate_to(user.id, "ask_jarvis")
    except Exception as e:
        logger.error(f"Error updating navigation: {e}", exc_info=True)

    welcome_message = (
        "🤖 *JARVIS Financial Assistant*\n\n"
        "Good day! I'm JARVIS, your AI financial assistant.\n\n"
        "I can help you with:\n"
        "• 📊 Analyze your spending patterns\n"
        "• 💡 Provide financial recommendations\n"
        "• ❓ Answer questions about your finances\n"
        "• 📈 Track your financial goals\n\n"
        "What would you like to know?"
    )

    # Build keyboard with navigation
    buttons = [
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_ai_chat")],
    ]
    nav_row = build_navigation_row(show_back=True, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    keyboard = InlineKeyboardMarkup(buttons)

    logger.info(f"🤖 Starting AI chat for user {user.id}")

    await query.edit_message_text(
        welcome_message,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    logger.info(f"✅ AI chat started, waiting for user input. State: {AI_CHAT}")
    return AI_CHAT


async def handle_ai_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle user message to AI.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Conversation state (continue or end)
    """
    user = update.effective_user

    if not update.message or not update.message.text:
        logger.error("❌ No message or text found in AI chat update")
        return AI_CHAT

    user_message = update.message.text
    logger.info(f"🤖 Received AI chat message from user {user.id}: {user_message[:50]}")

    # Show typing indicator to let user know we're processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    # Send processing message
    processing_msg = None
    try:
        processing_msg = await update.message.reply_text(
            "🤖 *JARVIS is thinking...*\n\nPlease wait while I process your request.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning(f"Could not send processing message: {e}")

    async_session_maker = get_async_session_maker()

    try:
        async with async_session_maker() as session:
            # Get or create user
            from sqlalchemy import select

            user_query = select(User).where(User.id == user.id)
            result = await session.execute(user_query)
            db_user = result.scalar_one_or_none()

            if not db_user:
                db_user = User(
                    id=user.id,
                    first_name=user.first_name or "User",
                    username=user.username,
                )
                session.add(db_user)
                await session.commit()

            # Get recent transactions for context
            transaction_service = TransactionService(session)
            recent_transactions = await transaction_service.get_transactions(
                user.id,
                page=1,
                per_page=10,
            )

            # Build user context
            user_context = {
                "user_id": user.id,
                "recent_transactions": recent_transactions,
                "financial_summary": {},  # TODO: Get from SummaryService in Phase 5
                "conversation_history": context.user_data.get(
                    "conversation_history",
                    [],
                ),
            }

            # Get AI service and generate response
            logger.info(f"🤖 Calling AI service for user {user.id}")
            ai_service = get_ai_service()
            response = await ai_service.generate_response(
                user_message,
                user_context,
                stream=False,
            )
            logger.info(
                f"✅ AI response received: {response[:100] if response else 'Empty response'}..."
            )

            # Update conversation history
            if "conversation_history" not in context.user_data:
                context.user_data["conversation_history"] = []

            context.user_data["conversation_history"].append(
                {"role": "user", "content": user_message},
            )
            context.user_data["conversation_history"].append(
                {"role": "assistant", "content": response},
            )

            # Keep only last 10 messages
            if len(context.user_data["conversation_history"]) > 10:
                context.user_data["conversation_history"] = context.user_data[
                    "conversation_history"
                ][-10:]

            # Update processing message with actual response
            logger.info(f"📤 Sending AI response to user {user.id}")
            if processing_msg:
                try:
                    await processing_msg.edit_text(
                        response,
                        parse_mode="Markdown",
                    )
                    logger.info("✅ AI response sent successfully (edited processing message)")
                except Exception as e:
                    # If editing fails (e.g., message too long), send new message
                    logger.warning(
                        f"Could not edit processing message: {e}. Sending new message instead."
                    )
                    try:
                        await processing_msg.delete()
                    except Exception:  # nosec B110
                        pass  # Ignore delete errors
                    await update.message.reply_text(response, parse_mode="Markdown")
                    logger.info("✅ AI response sent successfully (new message)")
            else:
                # If processing message wasn't sent, send response directly
                await update.message.reply_text(response, parse_mode="Markdown")
                logger.info("✅ AI response sent successfully (direct message)")

            return AI_CHAT

    except AIServiceError as e:
        logger.error(f"AI service error: {e}", exc_info=True)
        error_message = (
            "🤖 I apologize, but I'm experiencing technical difficulties. "
            "Please try again in a moment."
        )
        if processing_msg:
            try:
                await processing_msg.edit_text(error_message, parse_mode="Markdown")
            except Exception:
                try:
                    await processing_msg.delete()
                except Exception:  # nosec B110
                    pass  # Ignore delete errors
                await update.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)
        return AI_CHAT

    except Exception as e:
        logger.error(f"Error in AI chat: {e}", exc_info=True)
        error_message = (
            "❌ An error occurred while processing your request. Please try again later."
        )
        if processing_msg:
            try:
                await processing_msg.edit_text(error_message, parse_mode="Markdown")
            except Exception:
                try:
                    await processing_msg.delete()
                except Exception:  # nosec B110
                    pass  # Ignore delete errors
                await update.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)
        return AI_CHAT


async def cancel_ai_chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel AI chat conversation.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        ConversationHandler.END
    """
    from telegram.ext import ConversationHandler

    context.user_data.pop("conversation_history", None)

    keyboard = build_main_menu_keyboard()

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "❌ AI chat cancelled.",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            "❌ AI chat cancelled.",
            reply_markup=keyboard,
        )

    return ConversationHandler.END


# Conversation handler for AI chat
ai_chat_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_ai_chat, pattern="^ask_jarvis$"),
    ],
    states={
        AI_CHAT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_ai_chat, pattern="^cancel_ai_chat$"),
        MessageHandler(filters.COMMAND, cancel_ai_chat),
    ],
    per_chat=True,
    per_user=True,
    per_message=False,  # Explicitly set to avoid warning (callback queries tracked per update, not per message)
)
