"""Category model for transaction categories."""

from sqlalchemy import Boolean, Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.bot.models import Base


class CategoryType:
    """Category type constants."""

    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):
    """Represents a transaction category (system-defined or user-defined)."""

    __tablename__ = "categories"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Category details
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[str] = mapped_column(
        Enum(CategoryType.INCOME, CategoryType.EXPENSE, name="category_type"),
        nullable=False,
    )
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("name", name="uq_category_name"),
        {"mysql_engine": "InnoDB"},
    )

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name={self.name}, type={self.type}, is_system={self.is_system})>"

