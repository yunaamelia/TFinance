"""Transaction service for handling transaction CRUD operations."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.models.transaction import Transaction, TransactionType
from src.bot.utils.errors import DatabaseError, ValidationError
from src.bot.utils.validators import validate_amount, validate_category, validate_transaction_type


class TransactionService:
    """Service for transaction operations."""

    def __init__(self, session: AsyncSession):
        """Initialize TransactionService with database session.

        Args:
            session: Async database session
        """
        self.session = session

    async def create_transaction(
        self,
        user_id: int,
        transaction_data: dict,
    ) -> Transaction:
        """Create a new transaction for a user.

        Args:
            user_id: Telegram user ID
            transaction_data: Transaction data dictionary
                - amount (Decimal): Transaction amount (required, > 0)
                - type (str): "income" or "expense" (required)
                - category (str): Category name (required, 1-100 chars)
                - description (str, optional): Transaction description
                - timestamp (datetime, optional): Transaction timestamp (defaults to now)

        Returns:
            Transaction: Created transaction object

        Raises:
            ValidationError: If input validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate amount
            if isinstance(transaction_data.get("amount"), str):
                amount = validate_amount(transaction_data["amount"])
            elif isinstance(transaction_data.get("amount"), Decimal):
                amount = transaction_data["amount"]
                if amount <= 0:
                    raise ValidationError("Amount must be positive", field="amount")
            else:
                raise ValidationError("Amount must be Decimal or string", field="amount")

            # Validate type
            transaction_type = validate_transaction_type(transaction_data.get("type", ""))

            # Validate category
            category = validate_category(
                transaction_data.get("category", ""),
                transaction_type,
            )

            # Get optional fields
            description = transaction_data.get("description")
            timestamp = transaction_data.get("timestamp", datetime.now())

            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                type=transaction_type,
                category=category,
                description=description,
                timestamp=timestamp,
            )

            self.session.add(transaction)
            await self.session.commit()
            await self.session.refresh(transaction)

            return transaction

        except ValidationError:
            raise
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(
                f"Failed to create transaction: {str(e)}",
                operation="create_transaction",
            ) from e

    async def get_transactions(
        self,
        user_id: int,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> List[Transaction]:
        """Get paginated list of user transactions.

        Args:
            user_id: Telegram user ID
            filters: Filter criteria dictionary
                - type (str, optional): "income" or "expense"
                - category (str, optional): Category name
                - start_date (datetime, optional): Start date
                - end_date (datetime, optional): End date
            page: Page number (default: 1)
            per_page: Items per page (default: 20)

        Returns:
            List[Transaction]: List of transaction objects

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Build query
            query = select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.deleted_at.is_(None),
                ),
            )

            # Apply filters
            if filters:
                if filters.get("type"):
                    query = query.where(Transaction.type == filters["type"])
                if filters.get("category"):
                    query = query.where(Transaction.category == filters["category"])
                if filters.get("start_date"):
                    query = query.where(Transaction.timestamp >= filters["start_date"])
                if filters.get("end_date"):
                    query = query.where(Transaction.timestamp <= filters["end_date"])

            # Order by timestamp descending
            query = query.order_by(Transaction.timestamp.desc())

            # Apply pagination
            query = query.offset((page - 1) * per_page).limit(per_page)

            # Execute query
            result = await self.session.execute(query)
            transactions = result.scalars().all()

            return list(transactions)

        except Exception as e:
            raise DatabaseError(
                f"Failed to get transactions: {str(e)}",
                operation="get_transactions",
            ) from e

    async def get_transaction_by_id(
        self,
        user_id: int,
        transaction_id: int,
    ) -> Optional[Transaction]:
        """Get a specific transaction by ID.

        Args:
            user_id: Telegram user ID
            transaction_id: Transaction ID

        Returns:
            Transaction: Transaction object or None if not found

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            query = select(Transaction).where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id,
                    Transaction.deleted_at.is_(None),
                ),
            )

            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            raise DatabaseError(
                f"Failed to get transaction: {str(e)}",
                operation="get_transaction_by_id",
            ) from e

