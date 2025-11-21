"""Main menu keyboard builder."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.keyboards.navigation import build_navigation_row


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build main menu keyboard with primary actions.

    Returns:
        InlineKeyboardMarkup: Main menu keyboard
    """
    buttons = [
        [InlineKeyboardButton("💰 Add Transaction", callback_data="add_transaction")],
        [InlineKeyboardButton("📊 View Summary", callback_data="view_summary")],
        [InlineKeyboardButton("🤖 Ask JARVIS", callback_data="ask_jarvis")],
    ]

    # Add navigation row (only Home and Help, no Back on main menu)
    nav_row = build_navigation_row(show_back=False, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)

