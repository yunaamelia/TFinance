"""Unit tests for sanitizer final coverage."""

from src.bot.utils.sanitizer import escape_markdown, sanitize_text


class TestSanitizerFinal:
    """Test sanitizer for final coverage."""

    def test_sanitize_text_with_max_length(self):
        """Test sanitize_text with max_length."""
        text = "A" * 200
        result = sanitize_text(text, max_length=100)

        assert len(result) == 100

    def test_escape_markdown(self):
        """Test escape_markdown function."""
        text = "Hello *world* _test_ [link](url)"
        result = escape_markdown(text)

        # escape_markdown escapes special characters with backslash
        assert "\\*" in result or "\\_" in result or "\\[" in result
        # Result should be different from original
        assert result != text
