"""Input validation utilities for FinancialAssist bot."""

from decimal import Decimal, InvalidOperation

from src.bot.utils.errors import ValidationError


def validate_amount(amount_str: str) -> Decimal:
    """Validate and parse transaction amount.

    Args:
        amount_str: Amount as string (can include commas)

    Returns:
        Decimal: Validated amount

    Raises:
        ValidationError: If amount is invalid, negative, zero, or has > 2 decimal places
    """
    try:
        # Remove commas and whitespace
        cleaned = amount_str.replace(",", "").strip()

        value = Decimal(cleaned)

        if value <= 0:
            raise ValidationError("Amount must be positive", field="amount")

        # Check decimal places
        if value.as_tuple().exponent < -2:
            raise ValidationError(
                "Amount cannot have more than 2 decimal places",
                field="amount",
            )

        return value.quantize(Decimal("0.01"))

    except (ValueError, InvalidOperation) as e:
        raise ValidationError(f"Invalid amount format: {str(e)}", field="amount") from e


def validate_category(category: str, transaction_type: str) -> str:
    """Validate transaction category.

    Args:
        category: Category name
        transaction_type: Transaction type ("income" or "expense")

    Returns:
        str: Validated and trimmed category name

    Raises:
        ValidationError: If category is invalid
    """
    category = category.strip()

    if len(category) == 0:
        raise ValidationError("Category must be 1-100 characters", field="category")

    if len(category) > 100:
        raise ValidationError("Category must be 1-100 characters", field="category")

    # TODO: Check if system category exists and matches type
    # This will be implemented when Category model is available in service layer

    return category


def validate_transaction_type(transaction_type: str) -> str:
    """Validate transaction type.

    Args:
        transaction_type: Transaction type string

    Returns:
        str: Validated transaction type (lowercase)

    Raises:
        ValidationError: If type is not "income" or "expense"
    """
    normalized = transaction_type.lower().strip()

    if normalized not in ("income", "expense"):
        raise ValidationError(
            "Transaction type must be 'income' or 'expense'",
            field="type",
        )

    return normalized
