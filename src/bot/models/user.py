"""User model for Telegram bot users."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from src.bot.models import Base


class User(Base):
    """Represents a Telegram bot user and their preferences."""

    __tablename__ = "users"

    # Primary key: Telegram user ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # User information from Telegram
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # User preferences
    language_code: Mapped[str] = mapped_column(String(10), default="id", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Jakarta", nullable=False)
    default_currency: Mapped[str] = mapped_column(String(3), default="IDR", nullable=False)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    # Use text() for SQLite compatibility (SQLite uses CURRENT_TIMESTAMP, not now())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Relationships
    transactions: Mapped[list] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",  # Prevents unexpected N+1 queries
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username={self.username}, first_name={self.first_name})>"
