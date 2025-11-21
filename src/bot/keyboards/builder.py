"""Keyboard builder utilities for dynamic inline keyboards."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.keyboards.navigation import build_navigation_row


def build_transaction_type_keyboard(show_back: bool = True) -> InlineKeyboardMarkup:
    """Build keyboard for transaction type selection.

    Args:
        show_back: Whether to show back button

    Returns:
        InlineKeyboardMarkup: Keyboard with Income/Expense options
    """
    buttons = [
        [
            InlineKeyboardButton("💰 Income", callback_data="transaction_type:income"),
            InlineKeyboardButton("💸 Expense", callback_data="transaction_type:expense"),
        ],
    ]

    # Add navigation row
    nav_row = build_navigation_row(show_back=show_back, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)


def build_category_keyboard(
    categories: list,
    transaction_type: str,
    show_back: bool = True,
) -> InlineKeyboardMarkup:
    """Build keyboard for category selection.

    Args:
        categories: List of category dictionaries with 'name' and 'icon'
        transaction_type: Transaction type ("income" or "expense")
        show_back: Whether to show back button

    Returns:
        InlineKeyboardMarkup: Keyboard with category options
    """
    buttons = []

    # Add category buttons (2 per row)
    for i in range(0, len(categories), 2):
        row = []
        if i < len(categories):
            cat = categories[i]
            label = f"{cat.get('icon', '📁')} {cat['name']}"
            row.append(
                InlineKeyboardButton(
                    label,
                    callback_data=f"category:{cat['name']}",
                ),
            )
        if i + 1 < len(categories):
            cat = categories[i + 1]
            label = f"{cat.get('icon', '📁')} {cat['name']}"
            row.append(
                InlineKeyboardButton(
                    label,
                    callback_data=f"category:{cat['name']}",
                ),
            )
        if row:
            buttons.append(row)

    # Add "Custom Category" option
    buttons.append(
        [InlineKeyboardButton("➕ Custom Category", callback_data="category:custom")],
    )

    # Add navigation row
    nav_row = build_navigation_row(show_back=show_back, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)


def build_period_selector_keyboard(show_back: bool = True) -> InlineKeyboardMarkup:
    """Build keyboard for time period selection.

    Args:
        show_back: Whether to show back button

    Returns:
        InlineKeyboardMarkup: Keyboard with period options
    """
    buttons = [
        [
            InlineKeyboardButton("📅 Today", callback_data="period:today"),
            InlineKeyboardButton("📆 This Week", callback_data="period:week"),
        ],
        [InlineKeyboardButton("📊 This Month", callback_data="period:month")],
    ]

    # Add navigation row
    nav_row = build_navigation_row(show_back=show_back, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)


def build_pagination_keyboard(
    page: int,
    total_pages: int,
    show_back: bool = True,
) -> InlineKeyboardMarkup:
    """Build keyboard for pagination controls.

    Args:
        page: Current page number
        total_pages: Total number of pages
        show_back: Whether to show back button

    Returns:
        InlineKeyboardMarkup: Keyboard with pagination buttons
    """
    buttons = []

    # Pagination row
    pagination_row = []
    if page > 1:
        pagination_row.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"page:{page - 1}"),
        )
    if page < total_pages:
        pagination_row.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"page:{page + 1}"),
        )

    if pagination_row:
        buttons.append(pagination_row)

    # Add navigation row
    nav_row = build_navigation_row(show_back=show_back, show_home=True, show_help=True)
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)
