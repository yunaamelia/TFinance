"""Input sanitization utilities for security."""

import re


def sanitize_text(text: str, max_length: int | None = None) -> str:
    """Sanitize user input text.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length (None for no limit)

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Strip whitespace
    sanitized = text.strip()

    # Remove control characters (except newline, tab, carriage return)
    sanitized = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", sanitized)

    # Limit length
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized


def sanitize_category_name(category: str) -> str:
    """Sanitize category name input.

    Args:
        category: Category name

    Returns:
        Sanitized category name
    """
    # Basic sanitization (no max_length - let validation handle it)
    sanitized = sanitize_text(category)

    # Remove HTML tags (but keep & for "Food & Dining" style names)
    # Remove only dangerous characters, keep safe punctuation
    # Allow: letters, numbers, spaces, hyphens, underscores, ampersands, emojis
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-_&😀-🙏🌀-🗿]", "", sanitized)

    # Normalize whitespace
    sanitized = " ".join(sanitized.split())

    return sanitized.strip()


def sanitize_description(description: str) -> str:
    """Sanitize transaction description.

    Args:
        description: Transaction description

    Returns:
        Sanitized description
    """
    if not description:
        return ""

    # Basic sanitization
    sanitized = sanitize_text(description, max_length=500)

    # Remove potential SQL injection patterns (defense in depth)
    # Note: SQLAlchemy already prevents SQL injection, this is extra safety
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)",
    ]

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def sanitize_amount_input(amount_str: str) -> str:
    """Sanitize amount input string.

    Args:
        amount_str: Amount as string

    Returns:
        Sanitized amount string
    """
    if not amount_str:
        return ""

    # Remove all characters except digits, decimal point, commas, and minus sign
    # Keep minus sign for validation to catch negative amounts
    sanitized = re.sub(r"[^\d.,-]", "", amount_str)

    # Ensure only one decimal point
    parts = sanitized.split(".")
    if len(parts) > 2:
        sanitized = parts[0] + "." + "".join(parts[1:])

    # Ensure minus sign is only at the start
    if "-" in sanitized:
        sanitized = "-" + sanitized.replace("-", "")

    return sanitized


def escape_markdown(text: str) -> str:
    """Escape Markdown special characters for safe display.

    Args:
        text: Text to escape

    Returns:
        Escaped text safe for Markdown
    """
    # Escape Markdown special characters
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text
