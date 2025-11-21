"""Message formatting utilities for FinancialAssist bot."""

from datetime import datetime
from decimal import Decimal
from typing import List

from src.bot.models.transaction import Transaction


def format_currency(amount: Decimal, currency: str = "IDR") -> str:
    """Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code (default: IDR)

    Returns:
        str: Formatted currency string
    """
    if currency == "IDR":
        # Format Indonesian Rupiah
        amount_str = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"Rp {amount_str}"
    else:
        # Generic format
        return f"{currency} {amount:,.2f}"


def format_transaction(transaction: Transaction, currency: str = "IDR") -> str:
    """Format a single transaction for display.

    Args:
        transaction: Transaction object
        currency: Currency code (default: IDR)

    Returns:
        str: Formatted transaction string
    """
    amount_str = format_currency(transaction.amount, currency)
    type_emoji = "💰" if transaction.type == "income" else "💸"
    timestamp_str = transaction.timestamp.strftime("%Y-%m-%d %H:%M")

    lines = [
        f"{type_emoji} {transaction.type.upper()}: {amount_str}",
        f"📁 Category: {transaction.category}",
        f"📅 Date: {timestamp_str}",
    ]

    if transaction.description:
        lines.append(f"📝 Description: {transaction.description}")

    return "\n".join(lines)


def format_transaction_list(
    transactions: List[Transaction],
    currency: str = "IDR",
    page: int = 1,
    total_pages: int = 1,
) -> str:
    """Format a list of transactions for display.

    Args:
        transactions: List of Transaction objects
        currency: Currency code (default: IDR)
        page: Current page number
        total_pages: Total number of pages

    Returns:
        str: Formatted transaction list string
    """
    if not transactions:
        return "📋 No transactions found."

    lines = ["📋 *Transaction History*\n"]

    for idx, transaction in enumerate(transactions, start=1):
        lines.append(f"*{idx}.* {format_transaction(transaction, currency)}")
        lines.append("")  # Empty line between transactions

    if total_pages > 1:
        lines.append(f"\n📄 Page {page} of {total_pages}")

    return "\n".join(lines)


def format_summary(
    summary: dict,
    currency: str = "IDR",
) -> str:
    """Format financial summary for display.

    Args:
        summary: Financial summary dictionary
            - total_income (Decimal)
            - total_expenses (Decimal)
            - net_balance (Decimal)
            - transaction_count (int)
            - period (str)
        currency: Currency code (default: IDR)

    Returns:
        str: Formatted summary string
    """
    from decimal import Decimal

    total_income = Decimal(str(summary.get("total_income", 0)))
    total_expenses = Decimal(str(summary.get("total_expenses", 0)))
    net_balance = Decimal(str(summary.get("net_balance", 0)))
    transaction_count = summary.get("transaction_count", 0)
    period = summary.get("period", "month")

    period_names = {
        "today": "Today",
        "week": "This Week",
        "month": "This Month",
    }
    period_display = period_names.get(period, period.capitalize())

    lines = [
        f"📊 *Financial Summary - {period_display}*\n",
        f"💰 Total Income: {format_currency(total_income, currency)}",
        f"💸 Total Expenses: {format_currency(total_expenses, currency)}",
        f"📈 Net Balance: {format_currency(net_balance, currency)}",
        f"📝 Transactions: {transaction_count}",
    ]

    return "\n".join(lines)


def format_category_breakdown(
    category_breakdown: dict,
    currency: str = "IDR",
    limit: int = 10,
) -> str:
    """Format category breakdown for display.

    Args:
        category_breakdown: Dictionary mapping category names to amounts
        currency: Currency code (default: IDR)
        limit: Maximum number of categories to display

    Returns:
        str: Formatted category breakdown string
    """
    from decimal import Decimal

    if not category_breakdown:
        return "📁 No expense categories found."

    # Sort by amount descending
    sorted_categories = sorted(
        category_breakdown.items(),
        key=lambda x: Decimal(str(x[1])),
        reverse=True,
    )[:limit]

    lines = ["📁 *Category Breakdown*\n"]

    for idx, (category, amount) in enumerate(sorted_categories, start=1):
        amount_decimal = Decimal(str(amount))
        lines.append(f"{idx}. {category}: {format_currency(amount_decimal, currency)}")

    return "\n".join(lines)


def format_transaction_list_paginated(
    transactions: List[Transaction],
    currency: str = "IDR",
    page: int = 1,
    per_page: int = 10,
    total_count: int = 0,
) -> str:
    """Format paginated transaction list for display.

    Args:
        transactions: List of Transaction objects for current page
        currency: Currency code (default: IDR)
        page: Current page number
        per_page: Items per page
        total_count: Total number of transactions

    Returns:
        str: Formatted paginated transaction list string
    """
    if not transactions:
        return "📋 No transactions found."

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    lines = [f"📋 *Transaction History* (Page {page}/{total_pages})\n"]

    start_idx = (page - 1) * per_page + 1
    for idx, transaction in enumerate(transactions, start=start_idx):
        lines.append(f"*{idx}.* {format_transaction(transaction, currency)}")
        lines.append("")  # Empty line between transactions

    if total_pages > 1:
        lines.append(f"\n📄 Showing {len(transactions)} of {total_count} transactions")

    return "\n".join(lines)

