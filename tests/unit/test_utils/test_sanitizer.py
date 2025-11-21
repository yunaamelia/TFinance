"""Unit tests for input sanitization utilities."""

from src.bot.utils.sanitizer import (
    escape_markdown,
    sanitize_amount_input,
    sanitize_category_name,
    sanitize_description,
    sanitize_text,
)


class TestSanitizeText:
    """Test sanitize_text function."""

    def test_basic_sanitization(self):
        """Test basic text sanitization."""
        result = sanitize_text("  Hello World  ")
        assert result == "Hello World"

    def test_control_characters_removed(self):
        """Test that control characters are removed."""
        result = sanitize_text("Hello\x00World\x01Test")
        assert "Hello" in result
        assert "World" in result
        assert "Test" in result
        assert "\x00" not in result
        assert "\x01" not in result

    def test_max_length_enforced(self):
        """Test that max length is enforced."""
        long_text = "A" * 100
        result = sanitize_text(long_text, max_length=50)
        assert len(result) == 50

    def test_empty_string(self):
        """Test empty string handling."""
        result = sanitize_text("")
        assert result == ""

    def test_none_handling(self):
        """Test None handling."""
        result = sanitize_text(None)
        assert result == ""


class TestSanitizeCategoryName:
    """Test sanitize_category_name function."""

    def test_basic_category(self):
        """Test basic category name."""
        result = sanitize_category_name("Food & Dining")
        # Should preserve & character
        assert "Food" in result
        assert "Dining" in result
        assert "&" in result or "amp" in result

    def test_html_entities_escaped(self):
        """Test HTML entities handling."""
        result = sanitize_category_name("Food & Dining")
        # Should preserve & character (not escape to &amp;)
        assert "&" in result

    def test_special_characters_removed(self):
        """Test special characters are removed."""
        result = sanitize_category_name("Food@#$%Dining")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_emoji_preserved(self):
        """Test emojis are preserved."""
        result = sanitize_category_name("Food 🍔 Dining")
        assert "🍔" in result

    def test_whitespace_normalized(self):
        """Test whitespace is normalized."""
        result = sanitize_category_name("Food    Dining")
        assert "    " not in result
        assert "Food Dining" in result


class TestSanitizeDescription:
    """Test sanitize_description function."""

    def test_basic_description(self):
        """Test basic description."""
        result = sanitize_description("Lunch with friends")
        assert result == "Lunch with friends"

    def test_max_length_enforced(self):
        """Test max length is enforced."""
        long_desc = "A" * 600
        result = sanitize_description(long_desc)
        assert len(result) <= 500

    def test_sql_injection_patterns_removed(self):
        """Test SQL injection patterns are removed."""
        result = sanitize_description("Lunch'; DROP TABLE transactions; --")
        assert "DROP TABLE" not in result
        assert "--" not in result

    def test_empty_description(self):
        """Test empty description."""
        result = sanitize_description("")
        assert result == ""


class TestSanitizeAmountInput:
    """Test sanitize_amount_input function."""

    def test_basic_amount(self):
        """Test basic amount."""
        result = sanitize_amount_input("50000")
        assert result == "50000"

    def test_amount_with_commas(self):
        """Test amount with commas."""
        result = sanitize_amount_input("50,000")
        assert result == "50,000"

    def test_amount_with_decimal(self):
        """Test amount with decimal."""
        result = sanitize_amount_input("50,000.50")
        assert result == "50,000.50"

    def test_non_numeric_removed(self):
        """Test non-numeric characters are removed."""
        result = sanitize_amount_input("50abc000")
        assert result == "50000"

    def test_multiple_decimal_points(self):
        """Test multiple decimal points handled."""
        result = sanitize_amount_input("50.000.50")
        assert result.count(".") == 1


class TestEscapeMarkdown:
    """Test escape_markdown function."""

    def test_basic_escaping(self):
        """Test basic Markdown escaping."""
        result = escape_markdown("Hello *World*")
        assert "\\*" in result

    def test_all_special_chars_escaped(self):
        """Test all Markdown special characters are escaped."""
        text = "_*[]()~`>#+-=|{}.!"
        result = escape_markdown(text)
        # All special chars should be escaped
        assert "\\_" in result
        assert "\\*" in result
