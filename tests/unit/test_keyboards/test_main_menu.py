"""Unit tests for main menu keyboard builder."""

from src.bot.keyboards.main_menu import build_main_menu_keyboard


class TestMainMenuKeyboard:
    """Test main menu keyboard builder."""

    def test_build_main_menu_keyboard(self):
        """Test building main menu keyboard."""
        keyboard = build_main_menu_keyboard()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) >= 3  # At least 3 main buttons

        # Check main buttons
        buttons = keyboard.inline_keyboard
        button_texts = [btn[0].text for row in buttons for btn in [row]]

        assert "💰 Add Transaction" in button_texts
        assert "📊 View Summary" in button_texts
        assert "🤖 Ask JARVIS" in button_texts

        # Check navigation buttons
        nav_texts = [btn.text for row in buttons for btn in row]
        assert "🏠 Home" in nav_texts or "❓ Help" in nav_texts
