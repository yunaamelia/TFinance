"""Navigation handlers for Home, Back, and Help buttons."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.config.settings import get_redis_client
from src.bot.keyboards.main_menu import build_main_menu_keyboard
from src.bot.services.navigation_service import NavigationService
from src.bot.utils.errors import NavigationError

logger = logging.getLogger(__name__)

# Help messages for different screens
HELP_MESSAGES: dict[str, str] = {
    "main_menu": (
        "📖 *Help - Main Menu*\n\n"
        "Welcome to FinancialAssist! Here's what you can do:\n\n"
        "• 💰 *Add Transaction*: Record income or expense transactions\n"
        "• 📊 *View Summary*: See your financial summary and transaction history\n"
        "• 🤖 *Ask JARVIS*: Get AI-powered financial insights and advice\n\n"
        "Use the buttons below to navigate or type /start to return here."
    ),
    "add_transaction": (
        "📖 *Help - Add Transaction*\n\n"
        "To record a transaction:\n\n"
        "1. Select transaction type (Income or Expense)\n"
        "2. Enter the amount (e.g., 50000 or 50,000.00)\n"
        "3. Choose a category or create a custom one\n"
        "4. Optionally add a description\n\n"
        "The transaction will be saved and you'll see a confirmation."
    ),
    "view_summary": (
        "📖 *Help - View Summary*\n\n"
        "View your financial summary:\n\n"
        "• Select a time period (Today, This Week, This Month)\n"
        "• See total income, expenses, and net balance\n"
        "• View category breakdown\n"
        "• Browse transaction history with pagination\n\n"
        "Use navigation buttons to go back or return home."
    ),
    "ask_jarvis": (
        "📖 *Help - Ask JARVIS*\n\n"
        "JARVIS is your AI financial assistant:\n\n"
        "• Ask questions about your spending patterns\n"
        "• Get personalized financial recommendations\n"
        "• Analyze your transaction history\n"
        "• Receive budgeting advice\n\n"
        "JARVIS uses your transaction data to provide contextual insights."
    ),
    "default": (
        "📖 *Help*\n\n"
        "Need assistance? Here are some tips:\n\n"
        "• Use 🏠 *Home* to return to the main menu\n"
        "• Use ⬅️ *Back* to go to the previous screen\n"
        "• Use ❓ *Help* to see contextual help\n\n"
        "For more information, type /start to return to the main menu."
    ),
}


def get_help_message(screen: str) -> str:
    """Get help message for a screen.

    Args:
        screen: Screen identifier

    Returns:
        Help message string
    """
    return HELP_MESSAGES.get(screen, HELP_MESSAGES["default"])


async def handle_home(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle Home button - return to main menu.

    Args:
        update: Telegram update
        context: Bot context
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Reset navigation state
    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)
        await navigation_service.reset_navigation(user.id)
    except Exception as e:
        logger.error(f"Error resetting navigation: {e}", exc_info=True)

    # Clear user data
    context.user_data.clear()

    # Show main menu
    keyboard = build_main_menu_keyboard()
    welcome_message = f"👋 Welcome back, {user.first_name}!\n\nChoose an option below:"

    await query.edit_message_text(
        welcome_message,
        reply_markup=keyboard,
    )


async def handle_back(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle Back button - navigate to previous screen.

    Args:
        update: Telegram update
        context: Bot context
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)

        # Navigate back
        previous_screen = await navigation_service.navigate_back(user.id)

        # Route to appropriate handler based on previous screen
        if previous_screen == "main_menu":
            await handle_home(update, context)
        elif previous_screen == "add_transaction":
            from src.bot.handlers.transaction import start_transaction

            await start_transaction(update, context)
        elif previous_screen == "view_summary":
            from src.bot.handlers.summary import start_summary

            await start_summary(update, context)
        elif previous_screen == "ask_jarvis":
            from src.bot.handlers.ai_chat import start_ai_chat

            await start_ai_chat(update, context)
        else:
            # Default: go to main menu
            await handle_home(update, context)

    except NavigationError as e:
        # Already at main menu or error
        await query.answer(str(e.message), show_alert=True)
        await handle_home(update, context)
    except Exception as e:
        logger.error(f"Error navigating back: {e}", exc_info=True)
        await query.answer("Error navigating back. Returning to main menu.", show_alert=True)
        await handle_home(update, context)


async def handle_help(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle Help button - show contextual help.

    Args:
        update: Telegram update
        context: Bot context
    """
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Get current screen from navigation state
    try:
        redis_client = await get_redis_client()
        navigation_service = NavigationService(redis_client)
        state = await navigation_service.get_navigation_state(user.id)
        current_screen = state.get("current", "main_menu")
    except Exception:
        current_screen = "main_menu"

    # Get help message
    help_message = get_help_message(current_screen)

    # Build keyboard with navigation
    from telegram import InlineKeyboardMarkup

    from src.bot.keyboards.navigation import build_navigation_row

    buttons = []
    nav_row = build_navigation_row(show_back=True, show_home=True, show_help=False)
    if nav_row:
        buttons.append(nav_row)

    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        help_message,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
