# Service Interface Contracts

**Created**: 2025-01-27  
**Purpose**: Define internal service interfaces (not REST APIs - this is a Telegram bot)

---

## TransactionService Interface

**Purpose**: Handle transaction CRUD operations

### Methods

#### `create_transaction(user_id: int, transaction_data: dict) -> Transaction`

**Description**: Create a new transaction for a user

**Parameters**:

- `user_id` (int): Telegram user ID
- `transaction_data` (dict): Transaction data
  - `amount` (Decimal): Transaction amount (required, > 0)
  - `type` (str): "income" or "expense" (required)
  - `category` (str): Category name (required, 1-100 chars)
  - `description` (str, optional): Transaction description
  - `timestamp` (datetime, optional): Transaction timestamp (defaults to now)

**Returns**: `Transaction` object

**Raises**:

- `ValidationError`: If input validation fails
- `DatabaseError`: If database operation fails

**Example**:

```python
transaction = await transaction_service.create_transaction(
    user_id=123456789,
    transaction_data={
        "amount": Decimal("50000.00"),
        "type": "expense",
        "category": "Food & Dining",
        "description": "Lunch at restaurant",
        "timestamp": datetime.now()
    }
)
```

#### `get_transactions(user_id: int, filters: dict = None, page: int = 1, per_page: int = 20) -> List[Transaction]`

**Description**: Get paginated list of user transactions

**Parameters**:

- `user_id` (int): Telegram user ID
- `filters` (dict, optional): Filter criteria
  - `type` (str, optional): "income" or "expense"
  - `category` (str, optional): Category name
  - `start_date` (datetime, optional): Start date
  - `end_date` (datetime, optional): End date
- `page` (int): Page number (default: 1)
- `per_page` (int): Items per page (default: 20)

**Returns**: List of `Transaction` objects

**Raises**:

- `DatabaseError`: If database operation fails

#### `get_transaction_by_id(user_id: int, transaction_id: int) -> Transaction | None`

**Description**: Get a specific transaction by ID

**Parameters**:

- `user_id` (int): Telegram user ID
- `transaction_id` (int): Transaction ID

**Returns**: `Transaction` object or `None` if not found

**Raises**:

- `DatabaseError`: If database operation fails

---

## AIService Interface

**Purpose**: Handle AI-powered responses with JARVIS persona

### Methods

#### `generate_response(user_message: str, user_context: dict, stream: bool = False) -> AsyncIterator[str] | str`

**Description**: Generate AI response with JARVIS persona

**Parameters**:

- `user_message` (str): User's message/query
- `user_context` (dict): User context data
  - `user_id` (int): User ID
  - `recent_transactions` (List[Transaction]): Recent transactions
  - `financial_summary` (FinancialSummary, optional): Current financial summary
  - `conversation_history` (List[dict], optional): Previous messages
- `stream` (bool): Whether to stream response (default: False)

**Returns**:

- If `stream=True`: `AsyncIterator[str]` (token stream)
- If `stream=False`: `str` (complete response)

**Raises**:

- `AIServiceError`: If AI API call fails
- `TimeoutError`: If response takes > 3 seconds

**Example**:

```python
response = await ai_service.generate_response(
    user_message="What did I spend most on this month?",
    user_context={
        "user_id": 123456789,
        "recent_transactions": [...],
        "financial_summary": summary
    },
    stream=False
)
```

#### `analyze_spending_pattern(user_id: int, period: str) -> dict`

**Description**: Analyze user's spending patterns

**Parameters**:

- `user_id` (int): User ID
- `period` (str): Time period ("today", "week", "month")

**Returns**: Analysis dictionary

- `top_categories` (List[dict]): Top spending categories
- `trends` (dict): Spending trends
- `recommendations` (List[str]): Personalized recommendations

**Raises**:

- `AIServiceError`: If analysis fails

---

## SummaryService Interface

**Purpose**: Calculate and cache financial summaries

### Methods

#### `get_financial_summary(user_id: int, period: str) -> FinancialSummary`

**Description**: Get financial summary for a time period

**Parameters**:

- `user_id` (int): User ID
- `period` (str): Time period ("today", "week", "month", "custom")

**Returns**: `FinancialSummary` object

**Performance**:

- Cached in Redis for 5 minutes
- Database query < 100ms

**Raises**:

- `DatabaseError`: If database operation fails

**Example**:

```python
summary = await summary_service.get_financial_summary(
    user_id=123456789,
    period="month"
)
# Returns: FinancialSummary(
#     total_income=5000000.00,
#     total_expenses=3500000.00,
#     net_balance=1500000.00,
#     transaction_count=45
# )
```

#### `get_category_breakdown(user_id: int, period: str) -> dict`

**Description**: Get expenses grouped by category

**Parameters**:

- `user_id` (int): User ID
- `period` (str): Time period

**Returns**: Dictionary mapping category names to amounts

```python
{
    "Food & Dining": 1500000.00,
    "Transportation": 500000.00,
    "Shopping": 1000000.00
}
```

---

## NavigationService Interface

**Purpose**: Manage navigation state and keyboard building

### Methods

#### `get_navigation_state(user_id: int) -> NavigationState`

**Description**: Get user's current navigation state

**Parameters**:

- `user_id` (int): User ID

**Returns**: `NavigationState` object

#### `navigate_to(user_id: int, screen: str) -> None`

**Description**: Navigate to a new screen

**Parameters**:

- `user_id` (int): User ID
- `screen` (str): Screen identifier (e.g., "add_transaction", "view_summary")

**Side Effects**: Updates navigation stack in Redis

#### `navigate_back(user_id: int) -> str`

**Description**: Navigate back to previous screen

**Parameters**:

- `user_id` (int): User ID

**Returns**: Previous screen identifier

**Raises**:

- `NavigationError`: If already at main menu

#### `build_keyboard(user_id: int, screen: str) -> InlineKeyboardMarkup`

**Description**: Build inline keyboard for a screen

**Parameters**:

- `user_id` (int): User ID
- `screen` (str): Screen identifier

**Returns**: `InlineKeyboardMarkup` object with contextually appropriate buttons

**Example**:

```python
keyboard = await navigation_service.build_keyboard(
    user_id=123456789,
    screen="add_transaction"
)
# Returns keyboard with: [Income, Expense], [Back, Home, Help]
```

---

## Error Types

### ValidationError

**Raised by**: TransactionService, Input validators
**Attributes**:

- `message` (str): Error message
- `field` (str, optional): Field that failed validation

### DatabaseError

**Raised by**: All services with database operations
**Attributes**:

- `message` (str): Error message
- `operation` (str): Database operation that failed

### AIServiceError

**Raised by**: AIService
**Attributes**:

- `message` (str): Error message
- `status_code` (int, optional): HTTP status code from AI API

### NavigationError

**Raised by**: NavigationService
**Attributes**:

- `message` (str): Error message

---

## Service Dependencies

```
TransactionService
  └── Database (SQLAlchemy)
  └── Redis (caching)

AIService
  └── OpenAI API / Anthropic API
  └── TransactionService (for context)
  └── SummaryService (for context)

SummaryService
  └── Database (SQLAlchemy)
  └── Redis (caching)
  └── TransactionService (for data)

NavigationService
  └── Redis (session state)
```

---

**Status**: ✅ Complete - All service interfaces defined with method signatures, parameters, and error handling.
