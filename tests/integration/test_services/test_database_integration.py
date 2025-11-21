"""Integration tests for database operations."""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.bot.models import Base, User
from src.bot.services.transaction_service import TransactionService


@pytest.fixture
async def test_db():
    """Create test database."""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    yield async_session_maker

    await engine.dispose()


@pytest.mark.asyncio
async def test_transaction_persistence(test_db):
    """Test transaction persistence in database."""
    async_session_maker = test_db

    async with async_session_maker() as session:
        # Create user
        user = User(
            id=123456789,
            first_name="Test User",
            username="testuser",
        )
        session.add(user)
        await session.commit()

        # Create transaction
        service = TransactionService(session)
        transaction_data = {
            "amount": Decimal("50000.00"),
            "type": "expense",
            "category": "Food & Dining",
            "description": "Test transaction",
            "timestamp": datetime.now(),
        }

        transaction = await service.create_transaction(user.id, transaction_data)

        assert transaction.id is not None
        assert transaction.user_id == user.id
        assert transaction.amount == Decimal("50000.00")
        assert transaction.type == "expense"

        # Retrieve transaction (refresh user to avoid relationship access issues)
        await session.refresh(user)

        retrieved = await service.get_transaction_by_id(user.id, transaction.id)

        assert retrieved is not None
        assert retrieved.id == transaction.id
        assert retrieved.amount == transaction.amount


@pytest.mark.asyncio
async def test_summary_database_queries(test_db):
    """Test summary service database queries."""
    from unittest.mock import AsyncMock

    from src.bot.services.summary_service import SummaryService

    async_session_maker = test_db
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    async with async_session_maker() as session:
        # Create user
        user = User(
            id=123456789,
            first_name="Test User",
            username="testuser",
        )
        session.add(user)
        await session.commit()

        # Create transactions
        from src.bot.models.transaction import Transaction, TransactionType

        transactions = [
            Transaction(
                user_id=user.id,
                amount=Decimal("1000000.00"),
                type=TransactionType.INCOME,
                category="Salary",
                timestamp=datetime.now(),
            ),
            Transaction(
                user_id=user.id,
                amount=Decimal("50000.00"),
                type=TransactionType.EXPENSE,
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
        ]

        for transaction in transactions:
            session.add(transaction)
        await session.commit()

        # Test summary service
        summary_service = SummaryService(session, mock_redis)
        summary = await summary_service.get_financial_summary(user.id, "month")

        assert summary is not None
        assert summary["total_income"] == Decimal("1000000.00")
        assert summary["total_expenses"] == Decimal("50000.00")
        assert summary["net_balance"] == Decimal("950000.00")
        assert summary["transaction_count"] == 2

        # Test category breakdown
        breakdown = await summary_service.get_category_breakdown(user.id, "month")
        assert "Food & Dining" in breakdown
        assert breakdown["Food & Dining"] == Decimal("50000.00")


@pytest.mark.asyncio
async def test_navigation_state_persistence():
    """Test navigation state persistence in Redis."""
    from unittest.mock import AsyncMock

    from src.bot.services.navigation_service import NavigationService

    mock_redis = AsyncMock()

    # Test navigation state storage
    navigation_service = NavigationService(mock_redis)

    user_id = 123456789

    # Mock Redis get (empty initially)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    # Navigate to a screen
    await navigation_service.navigate_to(user_id, "add_transaction")

    # Verify Redis set was called
    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert "navigation" in call_args[0][0]

    # Test getting navigation state
    state_data = '{"stack": ["main_menu", "add_transaction"], "current": "add_transaction"}'
    mock_redis.get = AsyncMock(return_value=state_data)

    state = await navigation_service.get_navigation_state(user_id)

    assert state is not None
    assert "stack" in state
    assert state["current"] == "add_transaction"

    # Test navigating back
    previous = await navigation_service.navigate_back(user_id)

    assert previous == "main_menu"
    # Verify state was updated
    assert mock_redis.set.call_count >= 2
