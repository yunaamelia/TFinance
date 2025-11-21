"""Custom exception classes for FinancialAssist bot."""


class FinancialAssistError(Exception):
    """Base exception for all FinancialAssist errors."""

    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class ValidationError(FinancialAssistError):
    """Raised when input validation fails."""

    pass


class DatabaseError(FinancialAssistError):
    """Raised when database operation fails."""

    def __init__(self, message: str, operation: str = None, field: str = None):
        self.operation = operation
        super().__init__(message, field)


class AIServiceError(FinancialAssistError):
    """Raised when AI service operation fails."""

    def __init__(self, message: str, status_code: int = None, field: str = None):
        self.status_code = status_code
        super().__init__(message, field)


class NavigationError(FinancialAssistError):
    """Raised when navigation operation fails."""

    pass

