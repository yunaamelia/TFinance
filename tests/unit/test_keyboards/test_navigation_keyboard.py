"""Unit tests for navigation keyboard builder."""

from src.bot.keyboards.navigation import build_navigation_row


class TestNavigationKeyboard:
    """Test navigation keyboard builder."""

    def test_build_navigation_row_all_buttons(self):
        """Test building navigation row with all buttons."""
        row = build_navigation_row(show_back=True, show_home=True, show_help=True)

        assert row is not None
        assert len(row) == 3

        button_texts = [btn.text for btn in row]
        assert "⬅️ Back" in button_texts
        assert "🏠 Home" in button_texts
        assert "❓ Help" in button_texts

    def test_build_navigation_row_no_back(self):
        """Test building navigation row without back button."""
        row = build_navigation_row(show_back=False, show_home=True, show_help=True)

        assert row is not None
        assert len(row) == 2

        button_texts = [btn.text for btn in row]
        assert "⬅️ Back" not in button_texts
        assert "🏠 Home" in button_texts
        assert "❓ Help" in button_texts

    def test_build_navigation_row_only_home(self):
        """Test building navigation row with only home button."""
        row = build_navigation_row(show_back=False, show_home=True, show_help=False)

        assert row is not None
        assert len(row) == 1
        assert row[0].text == "🏠 Home"

    def test_build_navigation_row_empty(self):
        """Test building navigation row with no buttons."""
        row = build_navigation_row(show_back=False, show_home=False, show_help=False)

        assert row is None
