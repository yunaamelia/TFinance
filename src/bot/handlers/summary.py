"""Summary viewing handlers."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.config.settings import get_async_session_maker, get_redis_client
from src.bot.keyboards.builder import build_pagination_keyboard, build_period_selector_keyboard
from src.bot.keyboards.main_menu import build_main_menu_keyboard
from src.bot.keyboards.navigation import build_navigation_row
from src.bot.services.navigation_service import NavigationService
from src.bot.services.summary_service import SummaryService
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import DatabaseError
from src.bot.utils.formatters import (
    format_category_breakdown,
    format_summary,
    format_transaction_list_paginated,
)

logger = logging.getLogger(__name__)

# Conversation states
(SUMMARY_PERIOD, SUMMARY_VIEW, TRANSACTION_LIST) = range(3)


async def start_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start summary viewing flow.

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
        await navigation_service.navigate_to(user.id, "view_summary")
    except Exception as e:
        logger.error(f"Error updating navigation: {e}", exc_info=True)

    keyboard = build_period_selector_keyboard(show_back=True)

    await query.edit_message_text(
        "📊 *Financial Summary*\n\nSelect time period:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )

    return SUMMARY_PERIOD


async def handle_period_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle period selection.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    period = query.data.split(":")[1]  # Extract period from "period:month"
    context.user_data["selected_period"] = period

    user = update.effective_user
    async_session_maker = get_async_session_maker()
    redis_client = await get_redis_client()

    try:
        async with async_session_maker() as session:
            # Get financial summary
            summary_service = SummaryService(session, redis_client)
            summary = await summary_service.get_financial_summary(user.id, period)

            # Format summary message
            summary_text = format_summary(summary)
            category_breakdown = summary.get("category_breakdown", {})
            if category_breakdown:
                summary_text += "\n\n" + format_category_breakdown(category_breakdown)

            # Build keyboard with options
            buttons = [
                [
                    InlineKeyboardButton(
                        "📋 View Transactions",
                        callback_data="view_transactions",
                    ),
                ],
            ]
            nav_row = build_navigation_row(show_back=True, show_home=True, show_help=True)
            if nav_row:
                buttons.append(nav_row)

            keyboard = InlineKeyboardMarkup(buttons)

            await query.edit_message_text(
                summary_text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            return SUMMARY_VIEW

    except DatabaseError as e:
        logger.error(f"Database error in summary: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ Error retrieving summary. Please try again.",
        )
        return SUMMARY_PERIOD
    except Exception as e:
        logger.error(f"Error in summary: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ An error occurred. Please try again.",
        )
        return SUMMARY_PERIOD


async def handle_view_transactions(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle viewing transaction list.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    period = context.user_data.get("selected_period", "month")
    page = context.user_data.get("transaction_page", 1)
    per_page = 10

    async_session_maker = get_async_session_maker()

    try:
        async with async_session_maker() as session:
            # Get period dates for filtering
            summary_service = SummaryService(session, None)
            start_date, end_date = summary_service._get_period_dates(period)

            # Get transactions with filters
            transaction_service = TransactionService(session)
            filters = {
                "start_date": start_date,
                "end_date": end_date,
            }

            transactions = await transaction_service.get_transactions(
                user.id,
                filters=filters,
                page=page,
                per_page=per_page,
            )

            # Calculate total count (simplified - would need count query in production)
            # For now, estimate based on current page
            total_count = len(transactions) * page if transactions else 0

            # Format transaction list
            transaction_text = format_transaction_list_paginated(
                transactions,
                page=page,
                per_page=per_page,
                total_count=total_count,
            )

            # Build pagination keyboard
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
            keyboard = build_pagination_keyboard(page, total_pages, show_back=True)

            await query.edit_message_text(
                transaction_text,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            return TRANSACTION_LIST

    except Exception as e:
        logger.error(f"Error viewing transactions: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ Error retrieving transactions. Please try again.",
        )
        return SUMMARY_VIEW


async def handle_pagination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handle pagination navigation.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[1])  # Extract page from "page:2"
    context.user_data["transaction_page"] = page

    # Re-display transactions with new page
    return await handle_view_transactions(update, context)


async def cancel_summary(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Cancel summary viewing.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        ConversationHandler.END
    """
    from telegram.ext import ConversationHandler

    context.user_data.clear()
    keyboard = build_main_menu_keyboard()

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "❌ Summary view cancelled.",
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text(
            "❌ Summary view cancelled.",
            reply_markup=keyboard,
        )

    return ConversationHandler.END


# Conversation handler for summary viewing
summary_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_summary, pattern="^view_summary$"),
    ],
    states={
        SUMMARY_PERIOD: [
            CallbackQueryHandler(handle_period_selection, pattern="^period:"),
        ],
        SUMMARY_VIEW: [
            CallbackQueryHandler(handle_view_transactions, pattern="^view_transactions$"),
            CallbackQueryHandler(handle_period_selection, pattern="^period:"),
        ],
        TRANSACTION_LIST: [
            CallbackQueryHandler(handle_pagination, pattern="^page:"),
            CallbackQueryHandler(handle_view_transactions, pattern="^view_transactions$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_summary, pattern="^nav:"),
        MessageHandler(filters.COMMAND, cancel_summary),
    ],
    per_chat=True,
)
