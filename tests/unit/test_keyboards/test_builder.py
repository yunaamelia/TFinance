"""Unit tests for keyboard builder utilities."""

from src.bot.keyboards.builder import (
    build_category_keyboard,
    build_pagination_keyboard,
    build_period_selector_keyboard,
    build_transaction_type_keyboard,
)


class TestTransactionTypeKeyboard:
    """Test transaction type keyboard builder."""

    def test_build_transaction_type_keyboard(self):
        """Test building transaction type keyboard."""
        keyboard = build_transaction_type_keyboard(show_back=True)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) >= 1

        # Check transaction type buttons
        first_row = keyboard.inline_keyboard[0]
        assert len(first_row) == 2

        button_texts = [btn.text for btn in first_row]
        assert "💰 Income" in button_texts
        assert "💸 Expense" in button_texts

        # Check callback data
        callback_data = [btn.callback_data for btn in first_row]
        assert "transaction_type:income" in callback_data
        assert "transaction_type:expense" in callback_data

    def test_build_transaction_type_keyboard_no_back(self):
        """Test building transaction type keyboard without back button."""
        keyboard = build_transaction_type_keyboard(show_back=False)

        assert keyboard is not None
        # Should still have navigation row but without back
        nav_row = keyboard.inline_keyboard[-1]
        nav_texts = [btn.text for btn in nav_row]
        assert "⬅️ Back" not in nav_texts


class TestCategoryKeyboard:
    """Test category keyboard builder."""

    def test_build_category_keyboard(self):
        """Test building category keyboard."""
        categories = [
            {"name": "Food", "icon": "🍔"},
            {"name": "Transport", "icon": "🚗"},
            {"name": "Shopping", "icon": "🛒"},
        ]

        keyboard = build_category_keyboard(categories, "expense", show_back=True)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) >= 1

        # Check category buttons
        button_texts = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                button_texts.append(btn.text)

        assert any("Food" in text for text in button_texts)
        assert any("Transport" in text for text in button_texts)
        assert any("Shopping" in text for text in button_texts)

    def test_build_category_keyboard_empty(self):
        """Test building category keyboard with empty list."""
        keyboard = build_category_keyboard([], "expense", show_back=True)

        assert keyboard is not None
        # Should only have navigation row


class TestPeriodSelectorKeyboard:
    """Test period selector keyboard builder."""

    def test_build_period_selector_keyboard(self):
        """Test building period selector keyboard."""
        keyboard = build_period_selector_keyboard(show_back=True)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) >= 1

        # Check period buttons
        button_texts = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                button_texts.append(btn.text)

        assert any("Today" in text or "today" in text.lower() for text in button_texts)
        assert any("Week" in text or "week" in text.lower() for text in button_texts)
        assert any("Month" in text or "month" in text.lower() for text in button_texts)


class TestPaginationKeyboard:
    """Test pagination keyboard builder."""

    def test_build_pagination_keyboard_first_page(self):
        """Test building pagination keyboard for first page."""
        keyboard = build_pagination_keyboard(page=1, total_pages=5, show_back=True)

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) >= 1

        # Check pagination buttons
        button_texts = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                button_texts.append(btn.text)

        # Should have next button but not previous
        assert any("Next" in text or "next" in text.lower() for text in button_texts)

    def test_build_pagination_keyboard_middle_page(self):
        """Test building pagination keyboard for middle page."""
        keyboard = build_pagination_keyboard(page=3, total_pages=5, show_back=True)

        assert keyboard is not None

        # Should have both previous and next buttons
        button_texts = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                button_texts.append(btn.text)

        assert any(
            "Prev" in text or "prev" in text.lower() or "Previous" in text for text in button_texts
        )
        assert any("Next" in text or "next" in text.lower() for text in button_texts)

    def test_build_pagination_keyboard_last_page(self):
        """Test building pagination keyboard for last page."""
        keyboard = build_pagination_keyboard(page=5, total_pages=5, show_back=True)

        assert keyboard is not None

        # Should have previous button but not next
        button_texts = []
        for row in keyboard.inline_keyboard:
            for btn in row:
                button_texts.append(btn.text)

        assert any(
            "Prev" in text or "prev" in text.lower() or "Previous" in text for text in button_texts
        )

    def test_build_pagination_keyboard_single_page(self):
        """Test building pagination keyboard for single page."""
        keyboard = build_pagination_keyboard(page=1, total_pages=1, show_back=True)

        assert keyboard is not None
        # Should not have pagination buttons, only navigation
