# Data Model: Telegram AI Financial Assistant Bot

**Created**: 2025-01-27  
**Purpose**: Define data entities, relationships, and validation rules

---

## Entity: User

**Purpose**: Represents a Telegram bot user and their preferences

**Attributes**:
- `id` (BigInteger, Primary Key): Telegram user ID (unique identifier)
- `username` (String, Optional): Telegram username
- `first_name` (String): User's first name from Telegram
- `language_code` (String, Default: "id"): Preferred language (Indonesian default)
- `timezone` (String, Default: "Asia/Jakarta"): User's timezone for date/time display
- `default_currency` (String, Default: "IDR"): Default currency for transactions
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `preferences` (JSON, Optional): User preferences (default categories, notification settings)

**Relationships**:
- One-to-Many with Transaction (user has many transactions)
- One-to-One with Session (user has one active session)

**Validation Rules**:
- `id` must be positive integer
- `language_code` must be valid ISO 639-1 code
- `timezone` must be valid IANA timezone
- `default_currency` must be valid ISO 4217 currency code

**Indexes**:
- Primary key on `id`
- Index on `username` for lookups

---

## Entity: Transaction

**Purpose**: Represents a single financial transaction (income or expense)

**Attributes**:
- `id` (Integer, Primary Key): Auto-incrementing transaction ID
- `user_id` (BigInteger, Foreign Key → User.id): Owner of transaction
- `amount` (Numeric(10, 2)): Transaction amount (positive, 2 decimal places)
- `type` (Enum: "income" | "expense"): Transaction type
- `category` (String(100)): Transaction category (user-defined or system default)
- `description` (Text, Optional): User-provided description
- `timestamp` (DateTime): When transaction occurred (user-specified or current time)
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `tags` (JSON, Optional): Additional tags for filtering/searching

**Relationships**:
- Many-to-One with User (many transactions belong to one user)

**Validation Rules**:
- `amount` must be > 0
- `type` must be "income" or "expense"
- `category` must be non-empty string, max 100 characters
- `timestamp` must be valid datetime
- `user_id` must reference existing user

**Indexes**:
- Primary key on `id`
- Composite index on (`user_id`, `timestamp`) for chronological queries
- Composite index on (`user_id`, `type`) for filtering by type
- Index on `category` for category-based queries

**Business Rules**:
- Transactions are immutable once created (audit trail requirement)
- Deletions soft-delete (add `deleted_at` timestamp)
- Amounts stored with 2 decimal precision

---

## Entity: FinancialSummary

**Purpose**: Aggregated financial data for a user over a time period (calculated, not stored)

**Attributes** (Calculated):
- `user_id` (BigInteger): User identifier
- `period` (String): Time period ("today", "week", "month", "custom")
- `start_date` (DateTime): Period start
- `end_date` (DateTime): Period end
- `total_income` (Numeric(10, 2)): Sum of income transactions
- `total_expenses` (Numeric(10, 2)): Sum of expense transactions
- `net_balance` (Numeric(10, 2)): total_income - total_expenses
- `transaction_count` (Integer): Number of transactions in period
- `category_breakdown` (JSON): Expenses grouped by category

**Relationships**:
- Derived from Transaction entities (not a stored entity)

**Calculation Logic**:
```python
def calculate_summary(user_id: int, period: str) -> FinancialSummary:
    start, end = get_period_dates(period)
    transactions = get_transactions(user_id, start, end)
    
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
    net_balance = total_income - total_expenses
    
    category_breakdown = {}
    for t in transactions:
        if t.type == "expense":
            category_breakdown[t.category] = category_breakdown.get(t.category, 0) + t.amount
    
    return FinancialSummary(
        user_id=user_id,
        period=period,
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=net_balance,
        transaction_count=len(transactions),
        category_breakdown=category_breakdown
    )
```

**Caching Strategy**:
- Cache results in Redis for 5 minutes (key: `summary:{user_id}:{period}`)
- Invalidate cache when new transaction added

---

## Entity: Session

**Purpose**: User session state for conversation management

**Attributes**:
- `user_id` (BigInteger, Primary Key): Telegram user ID
- `conversation_state` (String, Optional): Current conversation state (FSM state)
- `navigation_stack` (JSON): Stack of screens for back navigation
- `context_data` (JSON, Optional): Temporary data for current conversation
- `last_activity` (DateTime): Last interaction timestamp
- `created_at` (DateTime): Session creation timestamp

**Relationships**:
- One-to-One with User (user has one active session)

**Validation Rules**:
- `navigation_stack` must be array of strings
- `context_data` must be valid JSON object
- `last_activity` updated on every interaction

**Storage**:
- Stored in Redis (not database) for fast access
- TTL: 1 hour (expires if inactive)
- Key format: `session:{user_id}`

**Navigation Stack Example**:
```json
{
  "navigation_stack": ["main_menu", "add_transaction", "transaction_type"]
}
```

---

## Entity: Category (System Defaults)

**Purpose**: Predefined transaction categories

**Attributes**:
- `id` (Integer, Primary Key): Category ID
- `name` (String(100), Unique): Category name
- `type` (Enum: "income" | "expense"): Applicable transaction type
- `icon` (String, Optional): Emoji icon for display
- `is_system` (Boolean): True for system categories, false for user-defined

**Default Categories**:

**Income**:
- Salary 💰
- Freelance 💼
- Investment 📈
- Gift 🎁
- Other ➕

**Expense**:
- Food & Dining 🍔
- Transportation 🚗
- Shopping 🛒
- Bills 💳
- Entertainment 🎬
- Health 🏥
- Education 📚
- Other ➖

**Relationships**:
- Referenced by Transaction.category (string match, not foreign key)

---

## Data Validation Rules

### Transaction Amount Validation
```python
def validate_amount(amount: str) -> Decimal:
    """Validate and parse transaction amount."""
    try:
        value = Decimal(amount)
        if value <= 0:
            raise ValidationError("Amount must be positive")
        if value.as_tuple().exponent < -2:
            raise ValidationError("Amount cannot have more than 2 decimal places")
        return value
    except (ValueError, InvalidOperation):
        raise ValidationError("Invalid amount format")
```

### Category Validation
```python
def validate_category(category: str, transaction_type: str) -> str:
    """Validate category exists and matches transaction type."""
    category = category.strip()
    if len(category) == 0 or len(category) > 100:
        raise ValidationError("Category must be 1-100 characters")
    
    # Check if system category exists and matches type
    system_category = get_system_category(category)
    if system_category and system_category.type != transaction_type:
        raise ValidationError(f"Category '{category}' is for {system_category.type}, not {transaction_type}")
    
    return category
```

### Timestamp Validation
```python
def validate_timestamp(timestamp_str: str, user_timezone: str) -> datetime:
    """Validate and parse timestamp with timezone."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        # Convert to user's timezone
        tz = pytz.timezone(user_timezone)
        return dt.astimezone(tz)
    except (ValueError, pytz.UnknownTimeZoneError):
        raise ValidationError("Invalid timestamp format")
```

---

## Database Schema

### Migration Strategy
- Use Alembic for database migrations
- Version control all schema changes
- Support rollback for production deployments

### Initial Schema
```sql
-- Users table
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    language_code VARCHAR(10) DEFAULT 'id',
    timezone VARCHAR(50) DEFAULT 'Asia/Jakarta',
    default_currency VARCHAR(3) DEFAULT 'IDR',
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    category VARCHAR(100) NOT NULL,
    description TEXT,
    timestamp TIMESTAMP NOT NULL,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_transactions_user_timestamp ON transactions(user_id, timestamp DESC);
CREATE INDEX idx_transactions_user_type ON transactions(user_id, type);
CREATE INDEX idx_transactions_category ON transactions(category);

-- Categories table (system defaults)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
    icon VARCHAR(10),
    is_system BOOLEAN DEFAULT TRUE
);
```

---

## Data Access Patterns

### Transaction Queries

**Get user transactions (paginated)**:
```python
def get_user_transactions(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
    filters: dict = None
) -> List[Transaction]:
    """Get paginated transactions with optional filters."""
    query = session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.deleted_at.is_(None)
    )
    
    if filters:
        if filters.get("type"):
            query = query.filter(Transaction.type == filters["type"])
        if filters.get("category"):
            query = query.filter(Transaction.category == filters["category"])
        if filters.get("start_date"):
            query = query.filter(Transaction.timestamp >= filters["start_date"])
        if filters.get("end_date"):
            query = query.filter(Transaction.timestamp <= filters["end_date"])
    
    return query.order_by(Transaction.timestamp.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
```

**Get financial summary**:
```python
def get_financial_summary(user_id: int, period: str) -> FinancialSummary:
    """Calculate financial summary for period."""
    start_date, end_date = get_period_dates(period)
    
    transactions = session.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.timestamp.between(start_date, end_date),
        Transaction.deleted_at.is_(None)
    ).all()
    
    return calculate_summary(transactions, period)
```

---

## Data Integrity Constraints

1. **Referential Integrity**: 
   - Transaction.user_id must reference existing User.id
   - Cascade delete: Deleting user deletes all transactions

2. **Check Constraints**:
   - Transaction.amount > 0
   - Transaction.type IN ('income', 'expense')
   - Category.type IN ('income', 'expense')

3. **Unique Constraints**:
   - User.id (primary key)
   - Category.name (unique)

4. **Soft Deletes**:
   - Transactions use `deleted_at` timestamp instead of hard delete
   - Queries filter out soft-deleted records

---

## Performance Considerations

1. **Indexing Strategy**:
   - Composite indexes on (user_id, timestamp) for chronological queries
   - Index on category for category-based filtering
   - Index on type for income/expense filtering

2. **Query Optimization**:
   - Use pagination for transaction lists
   - Cache financial summaries (5-minute TTL)
   - Use database aggregations for summary calculations

3. **Data Retention**:
   - Keep transaction history for 3+ months (per SC-008)
   - Archive old transactions (> 1 year) to separate table
   - Regular cleanup of expired sessions

---

**Status**: ✅ Complete - All entities defined with relationships, validation rules, and access patterns.

