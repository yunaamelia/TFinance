"""Unit tests for custom exception classes."""

from src.bot.utils.errors import (
    AIServiceError,
    DatabaseError,
    FinancialAssistError,
    NavigationError,
    ValidationError,
)


class TestFinancialAssistError:
    """Test base exception class."""

    def test_init_with_message(self):
        """Test exception initialization with message only."""
        error = FinancialAssistError("Test error")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.field is None

    def test_init_with_field(self):
        """Test exception initialization with message and field."""
        error = FinancialAssistError("Test error", field="amount")

        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.field == "amount"


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error(self):
        """Test ValidationError initialization."""
        error = ValidationError("Invalid input", field="amount")

        assert isinstance(error, FinancialAssistError)
        assert error.message == "Invalid input"
        assert error.field == "amount"


class TestDatabaseError:
    """Test DatabaseError exception."""

    def test_database_error(self):
        """Test DatabaseError initialization."""
        error = DatabaseError("Connection failed", operation="query", field="database")

        assert isinstance(error, FinancialAssistError)
        assert error.message == "Connection failed"
        assert error.operation == "query"
        assert error.field == "database"

    def test_database_error_no_operation(self):
        """Test DatabaseError without operation."""
        error = DatabaseError("Connection failed")

        assert error.message == "Connection failed"
        assert error.operation is None


class TestAIServiceError:
    """Test AIServiceError exception."""

    def test_ai_service_error(self):
        """Test AIServiceError initialization."""
        error = AIServiceError("API unavailable", status_code=503, field="ai_service")

        assert isinstance(error, FinancialAssistError)
        assert error.message == "API unavailable"
        assert error.status_code == 503
        assert error.field == "ai_service"

    def test_ai_service_error_no_status(self):
        """Test AIServiceError without status code."""
        error = AIServiceError("API unavailable")

        assert error.message == "API unavailable"
        assert error.status_code is None


class TestNavigationError:
    """Test NavigationError exception."""

    def test_navigation_error(self):
        """Test NavigationError initialization."""
        error = NavigationError("No back history", field="navigation")

        assert isinstance(error, FinancialAssistError)
        assert error.message == "No back history"
        assert error.field == "navigation"
