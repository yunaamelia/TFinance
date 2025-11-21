# Tasks: Telegram AI Financial Assistant Bot

**Input**: Design documents from `/specs/001-telegram-finance-bot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per Constitution §II requirement for TDD approach. All new features MUST follow Red-Green-Refactor cycle.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow plan.md structure: `src/bot/` for bot code

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md in src/bot/ with handlers/, keyboards/, services/, models/, utils/, config/ directories
- [x] T002 Initialize Python 3.11+ project with requirements.txt including python-telegram-bot v20+, SQLAlchemy, Pydantic, python-dotenv, aiohttp, openai, redis, pytest, pytest-asyncio, pytest-mock, pytest-cov
- [x] T003 [P] Configure linting tools (ruff or flake8) and formatting (black) in pyproject.toml
- [x] T004 [P] Setup pytest configuration in pytest.ini with async support and coverage settings
- [x] T005 [P] Create .env.example file with TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, DATABASE_URL, REDIS_URL placeholders
- [x] T006 [P] Create .gitignore file with Python, environment, database, and IDE exclusions
- [x] T007 [P] Create README.md with project description, setup instructions, and usage guide
- [x] T008 Create Dockerfile in docker/ directory for containerization
- [x] T009 Create docker-compose.yml in docker/ directory with bot, postgres, and redis services

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Setup database connection and SQLAlchemy engine configuration in src/bot/config/settings.py
- [x] T011 [P] Initialize Alembic for database migrations in migrations/ directory with env.py
- [x] T012 [P] Create database models base class in src/bot/models/**init**.py with SQLAlchemy declarative base
- [x] T013 [P] Create User model in src/bot/models/user.py with attributes: id, username, first_name, language_code, timezone, default_currency, preferences, created_at, updated_at
- [x] T014 [P] Create Transaction model in src/bot/models/transaction.py with attributes: id, user_id, amount, type, category, description, timestamp, tags, created_at, updated_at, deleted_at
- [x] T015 [P] Create Category model in src/bot/models/category.py with attributes: id, name, type, icon, is_system
- [x] T016 Create database migration for users, transactions, and categories tables in migrations/versions/
- [x] T017 [P] Setup Redis client connection in src/bot/config/settings.py with async support
- [x] T018 [P] Create custom exception classes in src/bot/utils/errors.py: ValidationError, DatabaseError, AIServiceError, NavigationError
- [x] T019 [P] Create logging configuration in src/bot/config/settings.py with structured JSON logging
- [x] T020 [P] Create environment configuration manager in src/bot/config/settings.py using Pydantic Settings
- [x] T021 Create error handler middleware in src/bot/main.py for global error handling with user-friendly messages
- [x] T022 [P] Seed default categories (Income: Salary, Freelance, Investment, Gift, Other; Expense: Food & Dining, Transportation, Shopping, Bills, Entertainment, Health, Education, Other) in scripts/seed_categories.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Record Financial Transaction (Priority: P1) 🎯 MVP

**Goal**: Users can record income and expense transactions through an interactive conversation with the bot, with validation and confirmation.

**Independent Test**: Can be fully tested by initiating a conversation with the bot, selecting "Add Transaction" from the main menu, and successfully recording a transaction with amount, category, and description. The bot should confirm the transaction and display it in the transaction history.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T023 [P] [US1] Unit test for Transaction model validation in tests/unit/test_models/test_transaction.py
- [x] T024 [P] [US1] Unit test for amount validator in tests/unit/test_utils/test_validators.py
- [x] T025 [P] [US1] Unit test for category validator in tests/unit/test_utils/test_validators.py
- [x] T026 [P] [US1] Unit test for TransactionService.create_transaction in tests/unit/test_services/test_transaction_service.py
- [x] T027 [P] [US1] Unit test for TransactionService.get_transactions with pagination in tests/unit/test_services/test_transaction_service.py
- [x] T028 [P] [US1] Integration test for transaction recording flow in tests/integration/test_handlers/test_transaction_flow.py
- [x] T029 [P] [US1] Integration test for database transaction persistence in tests/integration/test_services/test_database_integration.py
- [x] T030 [US1] E2E test for complete transaction recording journey in tests/e2e/test_user_journeys/test_record_transaction.py

### Implementation for User Story 1

- [x] T031 [P] [US1] Create input validation utilities in src/bot/utils/validators.py: validate_amount, validate_category, validate_transaction_type
- [x] T032 [P] [US1] Create message formatting utilities in src/bot/utils/formatters.py: format_transaction, format_transaction_list, format_currency
- [x] T033 [US1] Implement TransactionService in src/bot/services/transaction_service.py with create_transaction, get_transactions, get_transaction_by_id methods
- [x] T034 [P] [US1] Create keyboard builder utilities in src/bot/keyboards/builder.py: build_transaction_type_keyboard, build_category_keyboard
- [x] T035 [P] [US1] Create main menu keyboard in src/bot/keyboards/main_menu.py with Add Transaction, View Summary, Ask JARVIS buttons
- [x] T036 [US1] Implement /start command handler in src/bot/handlers/start.py with welcome message and main menu keyboard
- [x] T037 [US1] Implement transaction recording ConversationHandler in src/bot/handlers/transaction.py with states: TRANSACTION_TYPE, TRANSACTION_AMOUNT, TRANSACTION_CATEGORY, TRANSACTION_DESCRIPTION
- [x] T038 [US1] Implement transaction type selection handler in src/bot/handlers/transaction.py (Income/Expense)
- [x] T039 [US1] Implement transaction amount input handler in src/bot/handlers/transaction.py with validation
- [x] T040 [US1] Implement transaction category input handler in src/bot/handlers/transaction.py with system category suggestions
- [x] T041 [US1] Implement transaction description input handler in src/bot/handlers/transaction.py (optional)
- [x] T042 [US1] Implement transaction confirmation and save logic in src/bot/handlers/transaction.py
- [x] T043 [US1] Add error handling for invalid transaction input in src/bot/handlers/transaction.py
- [x] T044 [US1] Register transaction handlers in src/bot/main.py Application

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can record transactions through the bot.

---

## Phase 4: User Story 2 - AI-Powered Financial Insights (Priority: P2)

**Goal**: Users can interact with an AI assistant (JARVIS persona) that provides financial insights, answers questions about spending patterns, and offers personalized recommendations.

**Independent Test**: Can be fully tested by asking the AI assistant questions about spending patterns, requesting budget recommendations, or asking for financial advice. The bot should provide relevant, contextual responses based on the user's transaction history with JARVIS persona characteristics.

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T045 [P] [US2] Unit test for AIService.generate_response with mocked OpenAI API in tests/unit/test_services/test_ai_service.py
- [x] T046 [P] [US2] Unit test for JARVIS persona system prompt generation in tests/unit/test_services/test_ai_service.py
- [x] T047 [P] [US2] Unit test for conversation context building in tests/unit/test_services/test_ai_service.py
- [x] T048 [P] [US2] Unit test for AIService.analyze_spending_pattern in tests/unit/test_services/test_ai_service.py
- [x] T049 [P] [US2] Integration test for AI API integration with mocked responses in tests/integration/test_services/test_ai_api_integration.py
- [x] T050 [US2] Integration test for AI conversation flow in tests/integration/test_handlers/test_ai_conversation.py
- [x] T051 [US2] E2E test for AI insights user journey in tests/e2e/test_user_journeys/test_ai_insights.py

### Implementation for User Story 2

- [x] T052 [P] [US2] Create JARVIS persona configuration in src/bot/config/persona.py with system prompt template and personality traits
- [x] T053 [US2] Implement AIService abstract base class in src/bot/services/ai_service.py with generate_response and analyze_spending_pattern methods
- [x] T054 [US2] Implement OpenAIService in src/bot/services/ai_service.py extending AIService with OpenAI API integration
- [x] T055 [US2] Implement conversation context builder in src/bot/services/ai_service.py to include user transaction history and financial summary
- [x] T056 [US2] Implement JARVIS system prompt builder in src/bot/services/ai_service.py using persona configuration
- [x] T057 [US2] Implement streaming response support in src/bot/services/ai_service.py for real-time token delivery
- [x] T058 [US2] Implement AI conversation handler in src/bot/handlers/ai_chat.py with ConversationHandler for multi-turn conversations
- [x] T059 [US2] Implement AI message processing in src/bot/handlers/ai_chat.py with context injection and response formatting
- [x] T060 [US2] Add "Ask JARVIS" button to main menu keyboard in src/bot/keyboards/main_menu.py
- [x] T061 [US2] Implement error handling for AI service failures in src/bot/handlers/ai_chat.py with graceful degradation
- [x] T062 [US2] Register AI chat handlers in src/bot/main.py Application

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can record transactions and interact with JARVIS AI assistant.

---

## Phase 5: User Story 3 - View Financial Summary and Reports (Priority: P2)

**Goal**: Users can view their financial summary, transaction history, and categorized reports through interactive menus with dynamic keyboard navigation.

**Independent Test**: Can be fully tested by navigating to "View Summary" from the main menu, selecting different time periods and categories, and viewing transaction lists with proper pagination and navigation controls.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T063 [P] [US3] Unit test for SummaryService.get_financial_summary calculation logic in tests/unit/test_services/test_summary_service.py
- [x] T064 [P] [US3] Unit test for SummaryService.get_category_breakdown in tests/unit/test_services/test_summary_service.py
- [x] T065 [P] [US3] Unit test for financial summary caching in Redis in tests/unit/test_services/test_summary_service.py
- [x] T066 [P] [US3] Unit test for period date calculation (today, week, month) in tests/unit/test_services/test_summary_service.py
- [x] T067 [P] [US3] Integration test for summary database queries in tests/integration/test_services/test_database_integration.py
- [x] T068 [US3] Integration test for summary viewing flow in tests/integration/test_handlers/test_summary_flow.py
- [x] T069 [US3] E2E test for view summary user journey in tests/e2e/test_user_journeys/test_view_summary.py

### Implementation for User Story 3

- [x] T070 [US3] Implement SummaryService in src/bot/services/summary_service.py with get_financial_summary and get_category_breakdown methods
- [x] T071 [US3] Implement financial summary calculation logic in src/bot/services/summary_service.py aggregating transactions by period
- [x] T072 [US3] Implement Redis caching for financial summaries in src/bot/services/summary_service.py with 5-minute TTL
- [x] T073 [US3] Implement period date calculation utilities in src/bot/services/summary_service.py for today, week, month periods
- [x] T074 [P] [US3] Create summary formatting utilities in src/bot/utils/formatters.py: format_summary, format_category_breakdown
- [x] T075 [P] [US3] Create transaction list formatting with pagination in src/bot/utils/formatters.py: format_transaction_list_paginated
- [x] T076 [US3] Implement summary viewing handler in src/bot/handlers/summary.py with time period selection
- [x] T077 [US3] Implement transaction history viewing handler in src/bot/handlers/summary.py with pagination controls
- [x] T078 [US3] Implement transaction filtering by category and date range in src/bot/handlers/summary.py
- [x] T079 [P] [US3] Create summary keyboard builder in src/bot/keyboards/builder.py: build_period_selector_keyboard, build_pagination_keyboard
- [x] T080 [US3] Add "View Summary" button to main menu keyboard in src/bot/keyboards/main_menu.py
- [x] T081 [US3] Register summary handlers in src/bot/main.py Application

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can record transactions, interact with AI, and view financial summaries.

---

## Phase 6: User Story 4 - Interactive Navigation and Help System (Priority: P3)

**Goal**: Users can navigate the bot interface using consistent navigation controls (Home, Back, Help) that are always accessible, providing intuitive wayfinding and assistance.

**Independent Test**: Can be fully tested by navigating through different bot sections, using Home to return to main menu, Back to previous screen, and Help to access guidance. Navigation buttons should be consistently available and contextually appropriate.

### Tests for User Story 4 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T082 [P] [US4] Unit test for NavigationService.navigate_to and navigate_back in tests/unit/test_services/test_navigation_service.py
- [x] T083 [P] [US4] Unit test for NavigationService.build_keyboard with context awareness in tests/unit/test_services/test_navigation_service.py
- [x] T084 [P] [US4] Unit test for navigation stack management in tests/unit/test_services/test_navigation_service.py
- [x] T085 [P] [US4] Integration test for navigation flow in tests/integration/test_handlers/test_navigation.py
- [x] T086 [US4] Integration test for navigation state persistence in Redis in tests/integration/test_services/test_database_integration.py

### Implementation for User Story 4

- [x] T087 [US4] Implement NavigationService in src/bot/services/navigation_service.py with get_navigation_state, navigate_to, navigate_back, build_keyboard methods
- [x] T088 [US4] Implement navigation stack management in src/bot/services/navigation_service.py using Redis for persistence
- [x] T089 [P] [US4] Create navigation keyboard builder in src/bot/keyboards/navigation.py: build_navigation_row with Home, Back (conditional), Help buttons
- [x] T090 [US4] Implement Home button handler in src/bot/handlers/navigation.py to return to main menu from any screen
- [x] T091 [US4] Implement Back button handler in src/bot/handlers/navigation.py to navigate to previous screen in stack
- [x] T092 [US4] Implement Help button handler in src/bot/handlers/navigation.py with contextual help messages
- [x] T093 [US4] Update all keyboard builders to include navigation buttons using NavigationService in src/bot/keyboards/builder.py
- [x] T094 [US4] Integrate navigation state updates in all handlers (start, transaction, summary, ai_chat) when navigating
- [x] T095 [US4] Register navigation handlers in src/bot/main.py Application
- [x] T096 [US4] Update main menu keyboard to show navigation buttons conditionally in src/bot/keyboards/main_menu.py

**Checkpoint**: At this point, all user stories should work independently with full navigation support. Users can navigate seamlessly through all bot features.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T097 [P] Update documentation in README.md with setup, usage, and API documentation
- [x] T098 [P] Code cleanup and refactoring: Review all handlers for complexity < 10, functions < 50 lines
- [x] T099 [P] Performance optimization: Add connection pooling for database, optimize queries with proper indexes
- [x] T100 [P] Add comprehensive unit tests to reach 80% coverage target in tests/unit/
- [x] T101 [P] Add integration tests for edge cases: invalid input, AI service failures, database errors
- [x] T102 Security hardening: Input sanitization, SQL injection prevention, rate limiting implementation
- [x] T103 Implement rate limiting middleware in src/bot/main.py to prevent abuse (30 messages/second per bot)
- [x] T104 Add monitoring and logging for production: structured logs, error tracking, performance metrics
- [x] T105 Run quickstart.md validation: Execute all test scenarios and verify success criteria
- [x] T106 [P] Create deployment scripts and documentation in docs/deployment.md
- [x] T107 Add health check endpoint for monitoring in src/bot/main.py
- [x] T108 [P] Create database backup and recovery procedures in docs/operations.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on TransactionService from US1 for context
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on TransactionService from US1 for data
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Can work independently but enhances all other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before handlers
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, user stories can start in parallel (US1, US2, US3 can work in parallel after US1 TransactionService is complete)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (after US1 TransactionService is done)

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for User Story 1 together:
Task: "Unit test for Transaction model validation in tests/unit/test_models/test_transaction.py"
Task: "Unit test for amount validator in tests/unit/test_utils/test_validators.py"
Task: "Unit test for category validator in tests/unit/test_utils/test_validators.py"
Task: "Unit test for TransactionService.create_transaction in tests/unit/test_services/test_transaction_service.py"

# Launch model and utility creation together:
Task: "Create input validation utilities in src/bot/utils/validators.py"
Task: "Create message formatting utilities in src/bot/utils/formatters.py"
Task: "Create keyboard builder utilities in src/bot/keyboards/builder.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Record Transaction)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md scenarios
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (AI features)
4. Add User Story 3 → Test independently → Deploy/Demo (Summary features)
5. Add User Story 4 → Test independently → Deploy/Demo (Navigation polish)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Transaction recording) - CRITICAL PATH
   - Developer B: User Story 2 (AI integration) - Can start after US1 TransactionService
   - Developer C: User Story 3 (Summary) - Can start after US1 TransactionService
3. After US1 TransactionService complete:
   - All developers can work on their stories in parallel
4. Developer D: User Story 4 (Navigation) - Can enhance all stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Follow Constitution requirements: functions < 50 lines, complexity < 10, 80% coverage
- All handlers must use ConversationHandler pattern for stateful interactions
- All services must follow SOLID principles with abstract interfaces

---

**Total Tasks**: 108 tasks

- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 13 tasks
- Phase 3 (US1 - P1): 22 tasks (8 tests + 14 implementation)
- Phase 4 (US2 - P2): 18 tasks (7 tests + 11 implementation)
- Phase 5 (US3 - P2): 19 tasks (7 tests + 12 implementation)
- Phase 6 (US4 - P3): 15 tasks (5 tests + 10 implementation)
- Phase 7 (Polish): 12 tasks

**MVP Scope**: Phases 1, 2, 3 (User Story 1 only) = 44 tasks
