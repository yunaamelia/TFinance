"""Unit tests for formatter utilities."""

from datetime import datetime
from decimal import Decimal

from src.bot.models.transaction import Transaction
from src.bot.utils.formatters import (
    format_category_breakdown,
    format_currency,
    format_summary,
    format_transaction,
    format_transaction_list,
    format_transaction_list_paginated,
)


class TestFormatCurrency:
    """Test currency formatting."""

    def test_format_currency_idr(self):
        """Test IDR currency formatting."""
        result = format_currency(Decimal("50000.50"), "IDR")
        assert result.startswith("Rp")
        assert "50.000" in result or "50000" in result

    def test_format_currency_usd(self):
        """Test USD currency formatting."""
        result = format_currency(Decimal("100.50"), "USD")
        assert result.startswith("USD")
        assert "100.50" in result

    def test_format_currency_zero(self):
        """Test zero amount formatting."""
        result = format_currency(Decimal("0"), "IDR")
        assert "0" in result

    def test_format_currency_large_number(self):
        """Test large number formatting."""
        result = format_currency(Decimal("1000000"), "IDR")
        assert "1.000.000" in result or "1000000" in result


class TestFormatTransaction:
    """Test transaction formatting."""

    def test_format_transaction_income(self):
        """Test formatting income transaction."""
        transaction = Transaction(
            id=1,
            user_id=123,
            amount=Decimal("50000"),
            type="income",
            category="Salary",
            description="Monthly salary",
            timestamp=datetime(2024, 1, 15, 10, 30),
        )

        result = format_transaction(transaction)
        assert "INCOME" in result
        assert "Salary" in result
        assert "Monthly salary" in result
        assert "💰" in result

    def test_format_transaction_expense(self):
        """Test formatting expense transaction."""
        transaction = Transaction(
            id=2,
            user_id=123,
            amount=Decimal("25000"),
            type="expense",
            category="Food",
            timestamp=datetime(2024, 1, 15, 12, 0),
        )

        result = format_transaction(transaction)
        assert "EXPENSE" in result
        assert "Food" in result
        assert "💸" in result

    def test_format_transaction_no_description(self):
        """Test formatting transaction without description."""
        transaction = Transaction(
            id=3,
            user_id=123,
            amount=Decimal("10000"),
            type="expense",
            category="Transport",
            timestamp=datetime(2024, 1, 15, 8, 0),
        )

        result = format_transaction(transaction)
        assert "Description" not in result


class TestFormatTransactionList:
    """Test transaction list formatting."""

    def test_format_transaction_list_empty(self):
        """Test formatting empty transaction list."""
        result = format_transaction_list([])
        assert "No transactions found" in result

    def test_format_transaction_list_with_transactions(self):
        """Test formatting transaction list with items."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="income",
                category="Salary",
                timestamp=datetime(2024, 1, 15, 10, 30),
            ),
            Transaction(
                id=2,
                user_id=123,
                amount=Decimal("25000"),
                type="expense",
                category="Food",
                timestamp=datetime(2024, 1, 15, 12, 0),
            ),
        ]

        result = format_transaction_list(transactions, page=1, total_pages=1)
        assert "Transaction History" in result
        assert "1." in result
        assert "2." in result

    def test_format_transaction_list_pagination(self):
        """Test formatting transaction list with pagination."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="income",
                category="Salary",
                timestamp=datetime(2024, 1, 15, 10, 30),
            ),
        ]

        result = format_transaction_list(transactions, page=1, total_pages=3)
        assert "Page 1 of 3" in result


class TestFormatSummary:
    """Test summary formatting."""

    def test_format_summary_basic(self):
        """Test basic summary formatting."""
        summary = {
            "total_income": Decimal("100000"),
            "total_expenses": Decimal("50000"),
            "net_balance": Decimal("50000"),
            "transaction_count": 5,
            "period": "month",
        }

        result = format_summary(summary)
        assert "Financial Summary" in result
        assert "Total Income" in result
        assert "Total Expenses" in result
        assert "Net Balance" in result
        assert "Transactions" in result

    def test_format_summary_today(self):
        """Test summary formatting for today period."""
        summary = {
            "total_income": Decimal("0"),
            "total_expenses": Decimal("10000"),
            "net_balance": Decimal("-10000"),
            "transaction_count": 2,
            "period": "today",
        }

        result = format_summary(summary)
        assert "Today" in result

    def test_format_summary_week(self):
        """Test summary formatting for week period."""
        summary = {
            "total_income": Decimal("50000"),
            "total_expenses": Decimal("30000"),
            "net_balance": Decimal("20000"),
            "transaction_count": 3,
            "period": "week",
        }

        result = format_summary(summary)
        assert "This Week" in result


class TestFormatCategoryBreakdown:
    """Test category breakdown formatting."""

    def test_format_category_breakdown_empty(self):
        """Test formatting empty category breakdown."""
        result = format_category_breakdown({})
        assert "No expense categories found" in result

    def test_format_category_breakdown_with_categories(self):
        """Test formatting category breakdown with items."""
        breakdown = {
            "Food": Decimal("50000"),
            "Transport": Decimal("30000"),
            "Entertainment": Decimal("20000"),
        }

        result = format_category_breakdown(breakdown)
        assert "Category Breakdown" in result
        assert "Food" in result
        assert "Transport" in result
        assert "Entertainment" in result

    def test_format_category_breakdown_limit(self):
        """Test category breakdown with limit."""
        breakdown = {f"Category{i}": Decimal(f"{i * 1000}") for i in range(15)}

        result = format_category_breakdown(breakdown, limit=10)
        # Should only show top 10
        assert "Category14" in result  # Highest value
        assert "Category5" in result  # Should be in top 10
        # Category0 might not be in top 10


class TestFormatTransactionListPaginated:
    """Test paginated transaction list formatting."""

    def test_format_transaction_list_paginated_empty(self):
        """Test formatting empty paginated list."""
        result = format_transaction_list_paginated([], page=1, per_page=10, total_count=0)
        assert "No transactions found" in result

    def test_format_transaction_list_paginated_with_items(self):
        """Test formatting paginated list with items."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="income",
                category="Salary",
                timestamp=datetime(2024, 1, 15, 10, 30),
            ),
        ]

        result = format_transaction_list_paginated(transactions, page=1, per_page=10, total_count=1)
        assert "Transaction History" in result
        assert "Page 1/1" in result
        assert "1." in result

    def test_format_transaction_list_paginated_multiple_pages(self):
        """Test formatting paginated list with multiple pages."""
        transactions = [
            Transaction(
                id=i,
                user_id=123,
                amount=Decimal("10000"),
                type="expense",
                category="Food",
                timestamp=datetime(2024, 1, 15, 10, 30),
            )
            for i in range(5)
        ]

        result = format_transaction_list_paginated(
            transactions, page=2, per_page=10, total_count=25
        )
        assert "Page 2/3" in result
        assert "Showing 5 of 25 transactions" in result
