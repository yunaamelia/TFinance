"""Integration tests for transaction recording flow."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.transaction import (
    TRANSACTION_AMOUNT,
    TRANSACTION_CATEGORY,
    handle_transaction_amount,
    handle_transaction_type,
)


class TestTransactionFlow:
    """Test transaction recording conversation flow."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        telegram_user = TelegramUser(
            id=123456789,
            first_name="Test",
            is_bot=False,
        )
        chat = Chat(id=123456789, type="private")
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=telegram_user,
        )
        update = Update(update_id=1, message=message)
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_transaction_type_selection_income(self, mock_update, mock_context):
        """Test selecting income transaction type."""
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.data = "income"
        mock_update.callback_query.edit_message_text = AsyncMock()

        result = await handle_transaction_type(mock_update, mock_context)

        assert result == TRANSACTION_AMOUNT
        assert mock_context.user_data["transaction_type"] == "income"
        mock_update.callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_type_selection_expense(self, mock_update, mock_context):
        """Test selecting expense transaction type."""
        mock_update.callback_query = MagicMock()
        mock_update.callback_query.data = "expense"
        mock_update.callback_query.edit_message_text = AsyncMock()

        result = await handle_transaction_type(mock_update, mock_context)

        assert result == TRANSACTION_AMOUNT
        assert mock_context.user_data["transaction_type"] == "expense"

    @pytest.mark.asyncio
    async def test_transaction_amount_valid(self, mock_update, mock_context):
        """Test valid amount input."""
        mock_context.user_data["transaction_type"] = "expense"
        mock_update.message.reply_text = AsyncMock()

        result = await handle_transaction_amount(mock_update, mock_context)

        assert result == TRANSACTION_CATEGORY
        assert "amount" in mock_context.user_data
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_amount_invalid(self, mock_update, mock_context):
        """Test invalid amount input."""
        mock_context.user_data["transaction_type"] = "expense"
        mock_update.message.text = "invalid"
        mock_update.message.reply_text = AsyncMock()

        result = await handle_transaction_amount(mock_update, mock_context)

        # Should stay in same state on error
        assert result == TRANSACTION_AMOUNT
        mock_update.message.reply_text.assert_called()
