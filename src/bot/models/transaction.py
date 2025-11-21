"""Transaction model for financial transactions."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, Integer, Numeric, String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.bot.models import Base


class TransactionType:
    """Transaction type constants."""

    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    """Represents a single financial transaction (income or expense)."""

    __tablename__ = "transactions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        Enum(TransactionType.INCOME, TransactionType.EXPENSE, name="transaction_type"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    # Additional metadata
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="transactions",
        lazy="select",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
        # Composite index for common queries
        {"mysql_engine": "InnoDB"},
    )

    def __repr__(self) -> str:
        """String representation of Transaction."""
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, "
            f"type={self.type}, amount={self.amount}, category={self.category})>"
        )

