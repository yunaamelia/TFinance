# Quickstart Guide: Telegram AI Financial Assistant Bot

**Created**: 2025-01-27  
**Purpose**: Test scenarios and validation steps for feature implementation

---

## Prerequisites

1. Telegram account
2. Bot token from @BotFather
3. OpenAI API key (or Anthropic API key)
4. Python 3.11+ installed
5. PostgreSQL database (or SQLite for development)

---

## Setup Instructions

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd financialassist

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token"
export OPENAI_API_KEY="your_openai_key"
export DATABASE_URL="postgresql://user:pass@localhost/financialassist"
export REDIS_URL="redis://localhost:6379"
```

### 2. Database Setup

```bash
# Run migrations
alembic upgrade head

# Seed default categories
python scripts/seed_categories.py
```

### 3. Start Bot

```bash
# Development mode
python -m src.bot.main

# Production mode (with Docker)
docker-compose up
```

---

## Test Scenarios

### Scenario 1: First-Time User Onboarding

**Objective**: Verify new user registration and welcome flow

**Steps**:
1. Open Telegram and search for bot username
2. Click "Start" or send `/start` command
3. Verify welcome message appears
4. Verify main menu keyboard displays with options:
   - 💰 Add Transaction
   - 📊 View Summary
   - 🤖 Ask JARVIS
   - Navigation buttons (Home, Help)

**Expected Results**:
- Welcome message: "Good [time], [name]. I'm JARVIS, your financial assistant..."
- Main menu keyboard visible and functional
- User record created in database
- Session initialized in Redis

**Validation**:
```python
# Check database
user = db.query(User).filter(User.id == telegram_user_id).first()
assert user is not None
assert user.first_name == "UserFirstName"

# Check Redis session
session = redis.get(f"session:{telegram_user_id}")
assert session is not None
```

---

### Scenario 2: Record Income Transaction

**Objective**: Verify transaction recording flow (P1 - Core functionality)

**Steps**:
1. From main menu, select "💰 Add Transaction"
2. Select "Income" from transaction type keyboard
3. Enter amount: "5000000"
4. Enter category: "Salary" (or select from keyboard)
5. Enter description: "Monthly salary"
6. Confirm transaction

**Expected Results**:
- Transaction type selection keyboard appears
- Amount validation accepts positive numbers
- Category selection works (system categories or custom)
- Confirmation message: "Transaction recorded, Sir. Your balance is now..."
- Transaction saved to database
- Navigation returns to main menu

**Validation**:
```python
# Check transaction in database
transaction = db.query(Transaction).filter(
    Transaction.user_id == telegram_user_id,
    Transaction.amount == 5000000.00,
    Transaction.type == "income"
).first()
assert transaction is not None
assert transaction.category == "Salary"
assert transaction.description == "Monthly salary"
```

---

### Scenario 3: Record Expense Transaction

**Objective**: Verify expense recording with validation

**Steps**:
1. From main menu, select "💰 Add Transaction"
2. Select "Expense" from transaction type keyboard
3. Enter amount: "50000"
4. Enter category: "Food & Dining"
5. Enter description: "Lunch"
6. Confirm transaction

**Expected Results**:
- Expense transaction recorded successfully
- Financial summary updated
- Confirmation message shows updated balance

**Edge Cases to Test**:
- Invalid amount (negative, zero, non-numeric): Error message displayed
- Empty category: Validation error
- Amount with > 2 decimal places: Rounded or rejected

---

### Scenario 4: View Financial Summary

**Objective**: Verify financial summary display (P2)

**Steps**:
1. From main menu, select "📊 View Summary"
2. Select time period: "This Month"
3. View summary details

**Expected Results**:
- Summary displays:
  - Total Income: [amount]
  - Total Expenses: [amount]
  - Net Balance: [amount]
  - Transaction Count: [number]
- Time period selector works (Today, This Week, This Month)
- Navigation buttons functional (Back, Home, Help)

**Validation**:
```python
summary = summary_service.get_financial_summary(
    user_id=telegram_user_id,
    period="month"
)
assert summary.total_income > 0
assert summary.total_expenses > 0
assert summary.net_balance == summary.total_income - summary.total_expenses
```

---

### Scenario 5: View Transaction History

**Objective**: Verify transaction list with pagination

**Steps**:
1. From summary screen, select "View Transactions"
2. Scroll through transaction list
3. Use pagination controls (if > 20 transactions)

**Expected Results**:
- Transactions displayed in reverse chronological order
- Each transaction shows: amount, type, category, description, date
- Pagination works (Next/Previous buttons if applicable)
- Navigation maintained

**Edge Cases**:
- No transactions: "You haven't recorded any transactions yet" message
- Many transactions: Pagination controls appear

---

### Scenario 6: AI Conversation - Spending Analysis

**Objective**: Verify AI assistant with JARVIS persona (P2)

**Steps**:
1. From main menu, select "🤖 Ask JARVIS"
2. Send message: "What did I spend most on this month?"
3. Wait for AI response

**Expected Results**:
- JARVIS responds with JARVIS persona:
  - Professional, formal tone
  - Addresses user as "Sir" or "Madam"
  - Provides data-driven insights
  - References actual transaction data
- Response includes:
  - Top spending categories
  - Amounts and percentages
  - Brief analysis
- Response time < 3 seconds
- Navigation buttons remain accessible

**Validation**:
```python
# Check AI response quality
response = await ai_service.generate_response(
    user_message="What did I spend most on this month?",
    user_context={...}
)
assert "Sir" in response or "Madam" in response  # JARVIS persona
assert "spent" in response.lower() or "expense" in response.lower()
assert len(response) < 500  # Concise response
```

---

### Scenario 7: AI Conversation - Financial Advice

**Objective**: Verify AI provides personalized recommendations

**Steps**:
1. Select "🤖 Ask JARVIS"
2. Send message: "How can I save more money?"
3. Review AI recommendations

**Expected Results**:
- JARVIS analyzes spending patterns
- Provides specific, actionable recommendations
- References user's actual financial data
- Professional, helpful tone

**Example Response**:
"Based on your spending patterns, Sir, I've noticed you spend 40% of your income on Food & Dining. I recommend:
1. Setting a monthly dining budget of [amount]
2. Tracking daily expenses more closely
3. Consider meal planning to reduce restaurant visits

Your current savings rate is [X]%. With these adjustments, you could increase it to [Y]%."

---

### Scenario 8: Navigation Flow

**Objective**: Verify navigation buttons work correctly (P3)

**Steps**:
1. Navigate: Main Menu → Add Transaction → Transaction Type
2. Click "Back" button
3. Click "Home" button
4. Click "Help" button

**Expected Results**:
- Back button returns to previous screen
- Home button returns to main menu from any screen
- Help button shows contextual help
- Navigation stack maintained correctly

**Validation**:
```python
# Check navigation state
state = navigation_service.get_navigation_state(user_id)
assert state.current() == "main_menu"  # After Home click
assert len(state.stack) == 1  # Only main menu in stack
```

---

### Scenario 9: Error Handling

**Objective**: Verify graceful error handling

**Test Cases**:

**Invalid Amount**:
1. Try to enter negative amount: "-1000"
2. Expected: Error message "Amount must be positive"

**Invalid Category**:
1. Try to use income category for expense
2. Expected: Error message "Category 'Salary' is for income, not expense"

**AI Service Failure**:
1. Disconnect from internet
2. Ask JARVIS a question
3. Expected: "I'm experiencing technical difficulties. Please try again in a moment."

**Database Error**:
1. Stop database
2. Try to record transaction
3. Expected: User-friendly error message, error logged

---

### Scenario 10: Performance Validation

**Objective**: Verify performance requirements (Constitution §IV)

**Test Cases**:

**Response Time**:
```python
import time

start = time.time()
# Trigger bot action (button click, message send)
response = await bot.handle_update(update)
duration = time.time() - start

assert duration < 2.0  # FR-016 requirement
```

**Database Query Performance**:
```python
import time

start = time.time()
transactions = transaction_service.get_transactions(user_id)
duration = time.time() - start

assert duration < 0.1  # Constitution §IV requirement
```

**AI Response Time**:
```python
start = time.time()
response = await ai_service.generate_response(...)
duration = time.time() - start

assert duration < 3.0  # With streaming, first token < 1s
```

---

## Success Criteria Validation

### SC-001: Transaction Recording Time
- **Target**: < 2 minutes from opening bot
- **Test**: Time complete transaction flow
- **Expected**: Average time < 90 seconds

### SC-002: AI Response Relevance
- **Target**: 90% relevant responses
- **Test**: Ask 10 different financial questions
- **Expected**: 9+ responses are relevant and helpful

### SC-003: Navigation Efficiency
- **Target**: ≤ 3 clicks to any feature
- **Test**: Navigate to each feature from main menu
- **Expected**: All features accessible in ≤ 3 clicks

### SC-004: Data Accuracy
- **Target**: 99% accuracy
- **Test**: Record 100 transactions, verify all saved correctly
- **Expected**: 99+ transactions accurate

### SC-005: First-Attempt Success
- **Target**: 85% first-attempt success
- **Test**: 20 new users record first transaction
- **Expected**: 17+ succeed without help

### SC-006: Response Time
- **Target**: < 2 seconds
- **Test**: Measure response time for all interactions
- **Expected**: 95th percentile < 2 seconds

### SC-007: Navigation Accessibility
- **Target**: 100% of screens
- **Test**: Check all screens for navigation buttons
- **Expected**: All screens have Home/Help, Back when applicable

### SC-008: Transaction History
- **Target**: 3+ months of data
- **Test**: Create transactions spanning 4 months, query all
- **Expected**: All transactions retrievable

---

## Manual Testing Checklist

- [ ] Bot starts and responds to /start
- [ ] Main menu displays correctly
- [ ] Add Transaction flow works (income)
- [ ] Add Transaction flow works (expense)
- [ ] Invalid input validation works
- [ ] View Summary displays correct data
- [ ] Transaction history pagination works
- [ ] AI conversation with JARVIS persona
- [ ] Navigation buttons (Home, Back, Help) work
- [ ] Error messages are user-friendly
- [ ] Performance meets requirements (< 2s response)
- [ ] Database persistence works
- [ ] Session management works (Redis)
- [ ] Multiple users can use bot simultaneously

---

## Automated Test Commands

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run E2E tests
pytest tests/e2e/

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/unit/test_transaction_service.py::test_create_transaction
```

---

## Troubleshooting

### Bot Not Responding
- Check bot token is correct
- Verify bot is running (check logs)
- Check Telegram API connectivity

### Database Errors
- Verify database is running
- Check connection string
- Run migrations: `alembic upgrade head`

### AI Not Responding
- Check API key is valid
- Verify internet connectivity
- Check API rate limits
- Review error logs

### Performance Issues
- Check Redis is running (for caching)
- Verify database indexes exist
- Monitor response times in logs
- Check for N+1 query problems

---

**Status**: ✅ Complete - All test scenarios defined with validation steps and success criteria.

