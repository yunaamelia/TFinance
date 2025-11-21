"""Transaction recording handlers."""

import logging
from datetime import datetime

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.config.settings import get_async_session_maker, get_redis_client
from src.bot.keyboards.builder import build_category_keyboard, build_transaction_type_keyboard
from src.bot.keyboards.main_menu import build_main_menu_keyboard
from src.bot.models.category import Category
from src.bot.models.user import User
from src.bot.services.navigation_service import NavigationService
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import ValidationError
from src.bot.utils.formatters import format_currency, format_transaction

logger = logging.getLogger(__name__)

# Conversation states
(
    TRANSACTION_TYPE,
    TRANSACTION_AMOUNT,
    TRANSACTION_CATEGORY,
    TRANSACTION_DESCRIPTION,
) = range(4)


async def start_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start transaction recording flow.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    user = update.effective_user

    # Update navigation state
    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)
        await navigation_service.navigate_to(user.id, "add_transaction")
    except Exception as e:
        logger.error(f"Error updating navigation: {e}", exc_info=True)

    keyboard = build_transaction_type_keyboard(show_back=True)
    await update.callback_query.edit_message_text(
        "💰 *Add Transaction*\n\nSelect transaction type:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    return TRANSACTION_TYPE


async def handle_transaction_type(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle transaction type selection.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    transaction_type = query.data.split(":")[1]  # Extract "income" or "expense"
    context.user_data["transaction_type"] = transaction_type

    await query.edit_message_text(
        f"📝 *{transaction_type.upper()} Transaction*\n\n"
        "Enter the amount (e.g., 50000 or 50,000.00):",
        parse_mode="Markdown",
    )

    return TRANSACTION_AMOUNT


async def handle_transaction_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle transaction amount input.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state or current state on error
    """
    from src.bot.utils.validators import validate_amount

    try:
        amount_str = update.message.text.strip()
        amount = validate_amount(amount_str)
        context.user_data["amount"] = amount

        # Get categories for this transaction type
        transaction_type = context.user_data.get("transaction_type")
        async_session_maker = get_async_session_maker()

        async with async_session_maker() as session:
            from sqlalchemy import select

            query = select(Category).where(
                Category.type == transaction_type,
                Category.is_system,
            )
            result = await session.execute(query)
            categories = result.scalars().all()

            category_list = [{"name": cat.name, "icon": cat.icon or "📁"} for cat in categories]

        keyboard = build_category_keyboard(
            category_list,
            transaction_type,
            show_back=True,
        )

        amount_str = format_currency(amount)
        await update.message.reply_text(
            f"✅ Amount: {amount_str}\n\nSelect a category:",
            reply_markup=keyboard,
        )

        return TRANSACTION_CATEGORY

    except ValidationError as e:
        await update.message.reply_text(
            f"❌ {e.message}\n\nPlease enter a valid amount:",
        )
        return TRANSACTION_AMOUNT


async def handle_transaction_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle category selection or custom category input.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    if query.data.startswith("category:custom"):
        await query.edit_message_text(
            "📁 *Custom Category*\n\nEnter category name:",
            parse_mode="Markdown",
        )
        return TRANSACTION_CATEGORY

    category_name = query.data.split(":")[1]
    context.user_data["category"] = category_name

    await query.edit_message_text(
        f"✅ Category: {category_name}\n\nEnter description (optional, or send /skip):",
    )

    return TRANSACTION_DESCRIPTION


async def handle_custom_category(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle custom category input.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    from src.bot.utils.validators import validate_category

    try:
        category = update.message.text.strip()
        transaction_type = context.user_data.get("transaction_type")
        validated_category = validate_category(category, transaction_type)
        context.user_data["category"] = validated_category

        await update.message.reply_text(
            f"✅ Category: {validated_category}\n\nEnter description (optional, or send /skip):",
        )

        return TRANSACTION_DESCRIPTION

    except ValidationError as e:
        await update.message.reply_text(
            f"❌ {e.message}\n\nPlease enter a valid category name:",
        )
        return TRANSACTION_CATEGORY


async def handle_transaction_description(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle transaction description input.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        ConversationHandler.END to end conversation
    """
    from src.bot.utils.sanitizer import sanitize_description

    # Sanitize description input
    description = sanitize_description(update.message.text)

    if description.lower() in ("/skip", "skip", "-"):
        description = None

    context.user_data["description"] = description

    return await confirm_transaction(update, context)


async def confirm_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Confirm and save transaction.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        ConversationHandler.END
    """
    user = update.effective_user
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

            # Create transaction
            service = TransactionService(session)
            transaction_data = {
                "amount": context.user_data["amount"],
                "type": context.user_data["transaction_type"],
                "category": context.user_data["category"],
                "description": context.user_data.get("description"),
                "timestamp": datetime.now(),
            }

            transaction = await service.create_transaction(user.id, transaction_data)

            # Format confirmation message
            confirmation = (
                "✅ *Transaction Recorded!*\n\n"
                f"{format_transaction(transaction)}\n\n"
                "What would you like to do next?"
            )

            keyboard = build_main_menu_keyboard()
            await update.message.reply_text(
                confirmation,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            # Clear user data
            context.user_data.clear()

            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error saving transaction: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Error saving transaction. Please try again.",
        )
        return ConversationHandler.END


async def cancel_transaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel transaction recording.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        ConversationHandler.END
    """
    context.user_data.clear()
    keyboard = build_main_menu_keyboard()

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "❌ Transaction cancelled.",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            "❌ Transaction cancelled.",
            reply_markup=keyboard,
        )

    return ConversationHandler.END


# Conversation handler for transaction recording
transaction_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_transaction, pattern="^add_transaction$"),
    ],
    states={
        TRANSACTION_TYPE: [
            CallbackQueryHandler(handle_transaction_type, pattern="^transaction_type:"),
        ],
        TRANSACTION_AMOUNT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_amount),
        ],
        TRANSACTION_CATEGORY: [
            CallbackQueryHandler(handle_transaction_category, pattern="^category:"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_category),
        ],
        TRANSACTION_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_description),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_transaction, pattern="^nav:"),
        MessageHandler(filters.COMMAND, cancel_transaction),
    ],
)
