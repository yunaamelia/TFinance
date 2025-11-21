<!--
Sync Impact Report:
Version: 1.0.0 (initial creation)
Ratified: 2025-01-27
Last Amended: 2025-01-27

Changes:
- Initial constitution creation with four core principle areas
- Added comprehensive code quality standards (SOLID, complexity metrics)
- Added testing methodology framework (testing pyramid, TDD, coverage)
- Added UX consistency guidelines (WCAG 2.2 Level AA, design tokens)
- Added performance benchmarks (Core Web Vitals, API response times)
- Added governance framework and decision-making processes
- Added implementation guidelines with examples

Templates requiring updates:
- ✅ plan-template.md: Constitution Check section references updated
- ✅ spec-template.md: No changes needed (already aligned)
- ✅ tasks-template.md: No changes needed (already aligned)
- ⚠️ checklist-template.md: Pending review for constitution alignment

Follow-up TODOs:
- Review checklist-template.md for constitution compliance checks
-->

# FinancialAssist Constitution

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27

## Executive Summary

This constitution establishes the foundational principles and standards that govern all technical decisions in the FinancialAssist project. It defines measurable criteria for code quality, testing rigor, user experience consistency, and performance optimization. These principles serve as the primary reference for architectural decisions, code reviews, and trade-off resolution throughout the project lifecycle.

The constitution is organized into four core principle areas, each with specific measurable standards, enforcement mechanisms, and governance processes. All team members and contributors MUST adhere to these principles, with exceptions requiring documented justification and approval.

---

## Table of Contents

1. [Core Principles](#core-principles)
   - [I. Code Quality Standards](#i-code-quality-standards)
   - [II. Testing Methodology](#ii-testing-methodology)
   - [III. User Experience Consistency](#iii-user-experience-consistency)
   - [IV. Performance Optimization](#iv-performance-optimization)
2. [Measurable Standards](#measurable-standards)
3. [Governance Framework](#governance-framework)
4. [Implementation Guidelines](#implementation-guidelines)
5. [Quick Reference Checklist](#quick-reference-checklist)
6. [Appendix: Research Sources](#appendix-research-sources)

---

## Core Principles

### I. Code Quality Standards

**Philosophy**: Code is read far more often than it is written. We prioritize maintainability, clarity, and adherence to established design principles over cleverness or premature optimization.

**Non-Negotiable Rules**:

- **SOLID Principles MUST be applied**: All code MUST demonstrate adherence to Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles
- **Cyclomatic Complexity**: Functions MUST NOT exceed complexity of 10. Functions with complexity > 7 require justification in code comments
- **Function Length**: Functions MUST NOT exceed 50 lines. Functions > 30 lines require review justification
- **Code Coverage**: Minimum 80% line coverage for all production code. Critical paths (authentication, payment processing, data validation) require 95% coverage
- **DRY Principle**: Code duplication MUST be eliminated. Shared logic MUST be extracted to reusable functions, utilities, or services
- **Naming Conventions**: All identifiers MUST be self-documenting. Abbreviations prohibited unless industry-standard (e.g., API, HTTP, JSON)
- **Documentation**: Public APIs, complex algorithms, and business logic MUST include inline documentation explaining intent, not implementation

**Rationale**: High-quality code reduces technical debt, accelerates feature development, and minimizes bug introduction. SOLID principles ensure code remains extensible and testable as requirements evolve.

**Priority Hierarchy**: When principles conflict, maintainability (SOLID) > performance > brevity. Performance optimizations that violate SOLID principles require explicit approval and documentation.

---

### II. Testing Methodology

**Philosophy**: Tests are specifications that document behavior and prevent regressions. We follow the Testing Pyramid: many fast unit tests, fewer integration tests, minimal end-to-end tests.

**Non-Negotiable Rules**:

- **Test-Driven Development (TDD)**: All new features MUST follow Red-Green-Refactor cycle. Tests written → Tests fail → Implementation → Tests pass → Refactor
- **Testing Pyramid Ratios**:
  - Unit tests: 70% of test suite (fast, isolated, mock dependencies)
  - Integration tests: 25% of test suite (test component interactions, real dependencies)
  - End-to-end tests: 5% of test suite (critical user journeys only)
- **Test Coverage Thresholds**:
  - Overall: 80% line coverage minimum
  - Critical paths: 95% line coverage (authentication, payments, data validation)
  - New code: 100% coverage required before merge
- **Test Independence**: Tests MUST be independent, isolated, and repeatable. No shared state between tests
- **Test Naming**: Tests MUST follow pattern: `test_[method]_[scenario]_[expectedResult]` (e.g., `test_calculateInterest_rateValid_returnsCorrectAmount`)
- **Integration Test Requirements**: Integration tests REQUIRED for:
  - New API endpoints or contract changes
  - Database schema migrations
  - External service integrations
  - Cross-service communication
- **E2E Test Requirements**: E2E tests REQUIRED for:
  - Critical user journeys (authentication, core financial operations)
  - Payment processing flows
  - Data export/import functionality

**Rationale**: TDD ensures requirements are understood before implementation. The testing pyramid optimizes for fast feedback while maintaining confidence in system behavior. High coverage prevents regressions and documents expected behavior.

**Priority Hierarchy**: Test coverage > test speed > test count. When trade-offs are necessary, prioritize coverage of critical paths over comprehensive edge case coverage.

---

### III. User Experience Consistency

**Philosophy**: Every user interaction must be accessible, predictable, and consistent. We design for the widest possible audience, ensuring financial tools are usable by all.

**Non-Negotiable Rules**:

- **WCAG 2.2 Level AA Compliance**: All user interfaces MUST meet WCAG 2.2 Level AA success criteria. Level AAA compliance encouraged where feasible
- **Accessibility Requirements**:
  - Color contrast: Minimum 4.5:1 for normal text, 3:1 for large text (18pt+ or 14pt+ bold)
  - Keyboard navigation: All interactive elements MUST be keyboard accessible
  - Screen reader support: All content MUST have semantic HTML and ARIA labels where needed
  - Focus indicators: Visible focus indicators required for all interactive elements
- **Design Tokens**: All visual properties (colors, spacing, typography, shadows) MUST use centralized design tokens. No hardcoded values in components
- **Responsive Breakpoints**: Standard breakpoints MUST be used:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px
- **Interaction Patterns**: Consistent interaction patterns MUST be used across similar features:
  - Form validation: Inline errors with clear messaging
  - Loading states: Skeleton screens or progress indicators
  - Error handling: User-friendly error messages with recovery actions
  - Success feedback: Clear confirmation of completed actions
- **Internationalization**: All user-facing text MUST be externalized to translation files. No hardcoded strings in UI components

**Rationale**: Accessibility ensures legal compliance and expands user base. Design tokens and consistent patterns reduce cognitive load and accelerate development. Responsive design ensures usability across devices.

**Priority Hierarchy**: Accessibility (WCAG) > consistency > visual polish. Accessibility violations are blockers and cannot be deferred.

---

### IV. Performance Optimization

**Philosophy**: Performance is a feature, not an afterthought. We optimize for real-world user experience, measuring and improving Core Web Vitals and API responsiveness.

**Non-Negotiable Rules**:

- **Core Web Vitals Targets** (web applications):
  - Largest Contentful Paint (LCP): < 2.5 seconds
  - First Input Delay (FID): < 100 milliseconds
  - Cumulative Layout Shift (CLS): < 0.1
  - First Contentful Paint (FCP): < 1.8 seconds
  - Time to Interactive (TTI): < 3.5 seconds
- **API Response Times**:
  - P50 (median): < 200ms
  - P95: < 500ms
  - P99: < 1000ms
  - Critical endpoints (authentication, payments): P95 < 300ms
- **Database Query Performance**:
  - All queries MUST complete in < 100ms under normal load
  - Queries > 50ms require index review
  - N+1 query problems MUST be eliminated
- **Resource Optimization**:
  - JavaScript bundles: Initial load < 200KB gzipped
  - CSS: Critical CSS inlined, non-critical deferred
  - Images: WebP format with fallbacks, lazy loading for below-fold content
  - Fonts: Font-display: swap, subset fonts when possible
- **Caching Strategy**:
  - Static assets: Long-term caching with versioned filenames
  - API responses: Appropriate cache headers based on data volatility
  - Database queries: Query result caching for expensive operations
- **Performance Budget**: Performance budgets MUST be defined per feature and tracked in CI/CD. Budget violations block merges

**Rationale**: Performance directly impacts user satisfaction, conversion rates, and SEO rankings. Core Web Vitals are Google ranking factors. Fast APIs improve user experience and reduce infrastructure costs.

**Priority Hierarchy**: User-perceived performance (LCP, FID) > API response times > bundle size. When optimizing, prioritize metrics that users directly experience.

---

## Measurable Standards

### Code Quality Metrics

| Metric                | Threshold                     | Measurement Method                  | Enforcement |
| --------------------- | ----------------------------- | ----------------------------------- | ----------- |
| Cyclomatic Complexity | ≤ 10 per function             | Static analysis (SonarQube, ESLint) | CI/CD gate  |
| Function Length       | ≤ 50 lines                    | Static analysis                     | Code review |
| Code Coverage         | ≥ 80% overall, ≥ 95% critical | Coverage tools (Jest, pytest, etc.) | CI/CD gate  |
| Code Duplication      | 0% (DRY violations)           | Static analysis                     | Code review |
| Linting Errors        | 0 errors, < 10 warnings       | ESLint, Pylint, etc.                | CI/CD gate  |

### Testing Metrics

| Metric                 | Threshold                                   | Measurement Method  | Enforcement |
| ---------------------- | ------------------------------------------- | ------------------- | ----------- |
| Unit Test Ratio        | 70% of test suite                           | Test categorization | Code review |
| Integration Test Ratio | 25% of test suite                           | Test categorization | Code review |
| E2E Test Ratio         | 5% of test suite                            | Test categorization | Code review |
| Test Coverage          | ≥ 80% overall, ≥ 95% critical               | Coverage tools      | CI/CD gate  |
| Test Execution Time    | Unit: < 5s, Integration: < 30s, E2E: < 2min | CI/CD timing        | Monitoring  |

### UX Metrics

| Metric                 | Threshold                             | Measurement Method                        | Enforcement       |
| ---------------------- | ------------------------------------- | ----------------------------------------- | ----------------- |
| WCAG Compliance        | Level AA                              | Automated (axe-core, Lighthouse) + Manual | CI/CD + QA review |
| Color Contrast         | ≥ 4.5:1 (normal), ≥ 3:1 (large)       | Automated (axe-core)                      | CI/CD gate        |
| Keyboard Navigation    | 100% coverage                         | Manual testing checklist                  | QA review         |
| Responsive Breakpoints | 3 breakpoints (mobile/tablet/desktop) | Visual regression testing                 | QA review         |
| Design Token Usage     | 100% (no hardcoded values)            | Static analysis                           | Code review       |

### Performance Metrics

| Metric      | Threshold                             | Measurement Method         | Enforcement        |
| ----------- | ------------------------------------- | -------------------------- | ------------------ |
| LCP         | < 2.5s                                | Real User Monitoring (RUM) | CI/CD + Monitoring |
| FID         | < 100ms                               | RUM                        | CI/CD + Monitoring |
| CLS         | < 0.1                                 | RUM                        | CI/CD + Monitoring |
| API P95     | < 500ms (general), < 300ms (critical) | APM tools                  | Monitoring alerts  |
| Bundle Size | < 200KB gzipped (initial)             | Build analysis             | CI/CD gate         |

---

## Governance Framework

### Decision-Making Process

When faced with technical choices, engineers MUST:

1. **Reference Constitution First**: Check if constitution provides clear guidance
2. **Evaluate Trade-offs**: Document how each option aligns with principles
3. **Seek Approval for Exceptions**: If no option fully satisfies principles, document exception request
4. **Document Decision**: Record decision rationale in ADR (Architecture Decision Record) or PR description

### Trade-off Resolution

When principles conflict, use this priority order:

1. **Security & Accessibility** (highest priority - non-negotiable)
2. **Code Quality & Maintainability** (SOLID, testability)
3. **User Experience** (performance, accessibility, consistency)
4. **Performance** (speed, efficiency)
5. **Developer Experience** (tooling, convenience)

**Example**: If performance optimization requires violating SOLID principles, the optimization MUST be:

- Documented with justification
- Isolated in a performance-critical module
- Reviewed by senior engineer
- Include performance benchmarks proving necessity

### Exception Handling

Principles may be temporarily violated ONLY when:

1. **Technical Constraint**: Platform limitation or dependency issue prevents compliance
2. **Business Criticality**: Time-sensitive business requirement with documented timeline for remediation
3. **Experimental Feature**: Proof-of-concept with explicit sunset date

**Exception Process**:

1. Document exception in PR description or ADR
2. Include:
   - Which principle(s) are violated
   - Why violation is necessary
   - Remediation plan with timeline
   - Approval from tech lead or architect
3. Create follow-up ticket for remediation
4. Exception expires after 90 days unless re-approved

### Review Checkpoints

Constitution compliance MUST be validated at:

- **Code Review**: All PRs reviewed against relevant principles
- **Architecture Review**: Major architectural decisions require principle alignment review
- **Sprint Planning**: New features evaluated for constitution compliance
- **Release Planning**: Performance and UX metrics validated before release
- **Quarterly Audit**: Comprehensive review of all principles and metrics

### Amendment Process

Constitution amendments require:

1. **Proposal**: Document proposed change with rationale
2. **Review**: Team discussion and feedback period (minimum 3 days)
3. **Approval**: Majority vote from technical team
4. **Version Update**: Increment version per semantic versioning:
   - **MAJOR**: Backward-incompatible changes, principle removals
   - **MINOR**: New principles, expanded guidance
   - **PATCH**: Clarifications, typo fixes, non-semantic refinements
5. **Communication**: Announce changes to all team members
6. **Template Sync**: Update dependent templates and documentation

---

## Implementation Guidelines

### Code Quality Examples

**✅ GOOD**: SOLID-compliant service with single responsibility

```typescript
// Single Responsibility: Handles only interest calculation
class InterestCalculator {
  calculate(principal: number, rate: number, time: number): number {
    return principal * rate * time;
  }
}

// Dependency Inversion: Depends on abstraction, not concrete implementation
class LoanService {
  constructor(private calculator: InterestCalculator) {}

  processLoan(loan: Loan): LoanResult {
    const interest = this.calculator.calculate(
      loan.principal,
      loan.rate,
      loan.duration
    );
    return { ...loan, interest };
  }
}
```

**❌ BAD**: Violates Single Responsibility and has high complexity

```typescript
// BAD: Handles calculation, validation, persistence, and notification
class LoanManager {
  processLoan(data: any): void {
    // 200+ lines mixing calculation, validation, DB access, email sending
    if (this.validate(data)) {
      const result = this.calculate(data);
      this.saveToDB(result);
      this.sendEmail(result);
      this.logActivity(result);
      // ... more responsibilities
    }
  }
}
```

### Testing Examples

**✅ GOOD**: TDD approach with clear test structure

```typescript
// 1. Write test first (RED)
describe("InterestCalculator", () => {
  it("test_calculate_rateValid_returnsCorrectAmount", () => {
    const calculator = new InterestCalculator();
    const result = calculator.calculate(1000, 0.05, 2);
    expect(result).toBe(100);
  });
});

// 2. Implement to pass (GREEN)
class InterestCalculator {
  calculate(principal: number, rate: number, time: number): number {
    return principal * rate * time;
  }
}

// 3. Refactor if needed
```

**❌ BAD**: Test written after implementation, unclear naming

```typescript
// BAD: Test written after code, vague name, tests implementation details
describe("test1", () => {
  it("works", () => {
    const calc = new InterestCalculator();
    expect(calc.calculate(1000, 0.05, 2)).toBe(100);
    // Also tests internal state, making test brittle
    expect(calc.internalState).toBe("calculated");
  });
});
```

### UX Examples

**✅ GOOD**: Accessible form with proper labels and error handling

```html
<!-- GOOD: Semantic HTML, ARIA labels, keyboard accessible -->
<fieldset>
  <legend>Loan Application</legend>
  <label for="principal">Principal Amount</label>
  <input
    type="number"
    id="principal"
    name="principal"
    aria-describedby="principal-error principal-help"
    aria-invalid="false"
    required
  />
  <span id="principal-help" class="help-text">
    Enter the loan amount in dollars
  </span>
  <span id="principal-error" class="error-text" role="alert" aria-live="polite">
    <!-- Error message appears here -->
  </span>
</fieldset>
```

**❌ BAD**: Inaccessible form with poor UX

```html
<!-- BAD: No labels, no error handling, poor contrast -->
<div>
  <input type="text" placeholder="Amount" style="color: #ccc;" />
  <button onclick="submit()">Submit</button>
  <!-- No error messages, no keyboard navigation support -->
</div>
```

### Performance Examples

**✅ GOOD**: Optimized image loading with lazy loading

```html
<!-- GOOD: WebP format, lazy loading, proper sizing -->
<picture>
  <source srcset="hero.webp" type="image/webp" />
  <img
    src="hero.jpg"
    alt="Financial dashboard"
    loading="lazy"
    width="1200"
    height="600"
    fetchpriority="high"
  />
</picture>
```

**❌ BAD**: Unoptimized images blocking render

```html
<!-- BAD: Large image, no format optimization, blocks rendering -->
<img src="huge-uncompressed-image.png" alt="dashboard" />
```

### Enforcement Mechanisms

1. **Automated Linting**: ESLint, Pylint, or equivalent configured with strict rules
2. **Pre-commit Hooks**: Run linters and formatters before commits
3. **CI/CD Gates**:
   - Coverage thresholds enforced
   - Performance budgets validated
   - Accessibility scans (axe-core) run
   - Bundle size checks
4. **Code Review Checklists**: PR templates include constitution compliance checks
5. **Performance Monitoring**: APM tools alert on threshold violations
6. **Regular Audits**: Quarterly reviews of metrics and compliance

### Documentation Requirements

All architectural decisions MUST be documented in ADRs (Architecture Decision Records) including:

- **Context**: What decision is being made and why
- **Options Considered**: Alternative approaches evaluated
- **Decision**: Chosen approach with rationale
- **Consequences**: Impact on principles, trade-offs made
- **Compliance**: How decision aligns with constitution

---

## Quick Reference Checklist

### Before Writing Code

- [ ] Understand requirements and user stories
- [ ] Write tests first (TDD)
- [ ] Check for existing patterns/components to reuse
- [ ] Verify design tokens available for UI work

### During Development

- [ ] Keep functions < 50 lines, complexity < 10
- [ ] Follow SOLID principles
- [ ] Use design tokens (no hardcoded values)
- [ ] Ensure keyboard accessibility
- [ ] Maintain test coverage > 80%

### Before Code Review

- [ ] All tests passing
- [ ] Coverage thresholds met
- [ ] Linting errors resolved
- [ ] Performance budget not exceeded
- [ ] Accessibility scan passed
- [ ] Documentation updated

### Before Merge

- [ ] Code review approved
- [ ] CI/CD gates passed
- [ ] Performance metrics validated
- [ ] UX review completed (if UI changes)
- [ ] Exception documented (if any)

### Before Release

- [ ] Core Web Vitals within targets
- [ ] API response times validated
- [ ] WCAG Level AA compliance verified
- [ ] Critical path test coverage ≥ 95%
- [ ] Performance monitoring configured

---

## Appendix: Research Sources

### Code Quality

- **SOLID Principles**: Refactoring.Guru (https://refactoring.guru)
- **Clean Architecture**: Robert C. Martin's "Clean Architecture"
- **Code Metrics**: SonarQube Quality Gates, ESLint complexity rules

### Testing

- **Testing Pyramid**: Martin Fowler's "The Practical Test Pyramid"
- **TDD Methodology**: Kent Beck's "Test-Driven Development: By Example"
- **JUnit 5**: Official documentation and best practices

### User Experience

- **WCAG 2.2**: W3C Web Content Accessibility Guidelines (https://www.w3.org/WAI/WCAG22/quickref/)
- **Design Systems**: Material Design, Ant Design principles
- **Responsive Design**: MDN Web Docs responsive design guide

### Performance

- **Core Web Vitals**: Google Web Vitals documentation (https://web.dev/vitals/)
- **Web Performance**: web.dev Learn Performance guide
- **API Performance**: Industry standards for REST API response times

### Additional Reading

- **12-Factor App Methodology**: For cloud-native application principles
- **OWASP Top 10**: Security best practices
- **Semantic Versioning**: https://semver.org/

---

**Constitution Supersedes**: This document supersedes all other coding standards, style guides, and technical decision frameworks. When conflicts arise, this constitution takes precedence.

**Living Document**: This constitution evolves with the project. All amendments must follow the governance process outlined above.

**Questions or Clarifications**: Contact the technical lead or architecture team for constitution interpretation or exception requests.
