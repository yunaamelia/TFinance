"""Navigation keyboard builders."""

from typing import Optional

from telegram import InlineKeyboardButton


def build_navigation_row(
    show_back: bool = False,
    show_home: bool = True,
    show_help: bool = True,
) -> Optional[list]:
    """Build navigation button row.

    Args:
        show_back: Whether to show back button
        show_home: Whether to show home button
        show_help: Whether to show help button

    Returns:
        List of InlineKeyboardButton or None if no buttons
    """
    buttons = []

    if show_back:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data="nav:back"))

    if show_home:
        buttons.append(InlineKeyboardButton("🏠 Home", callback_data="nav:home"))

    if show_help:
        buttons.append(InlineKeyboardButton("❓ Help", callback_data="nav:help"))

    return buttons if buttons else None

