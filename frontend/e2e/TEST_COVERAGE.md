# E2E Test Coverage

This document provides a comprehensive overview of all E2E tests in the Math Helper application.

## Test Organization

Tests are organized into the following spec files:

- `page-load.spec.ts` - Basic page load verification
- `learner-management.spec.ts` - Learner CRUD operations
- `dashboard.spec.ts` - Dashboard UI and navigation
- `practice-flow.spec.ts` - Practice session interactions
- `session-submission.spec.ts` - Session completion and submission
- `leveling.spec.ts` - Level progression functionality
- `achievements.spec.ts` - Achievement earning and display
- `journey-page.spec.ts` - Journey/Progress page features
- `summary-page.spec.ts` - Practice summary page

## Test Coverage Tables

### Table 1: Learner Management Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| LM-001 | Create new learner | Create learner with valid name, avatar, PIN | `testid-student-grid`, modal inputs | `learner-management.spec.ts` |
| LM-002 | Create learner validation | Attempt invalid inputs (short name, wrong PIN) | Modal error messages | `learner-management.spec.ts` |
| LM-003 | Delete learner | Delete a test learner | Delete button/API | `learner-management.spec.ts` |
| LM-004 | Select learner | Click learner card | `testid-student-card-{id}` | `learner-management.spec.ts` |
| LM-005 | Duplicate name prevention | Try creating learner with existing name | Modal | `learner-management.spec.ts` |

### Table 2: Dashboard & Navigation Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| DASH-001 | Dashboard loads | Verify main dashboard elements | `testid-select-learner-header`, `testid-student-grid` | `dashboard.spec.ts` |
| DASH-002 | Learner stats display | Select learner, verify stats cards | Stats cards | `dashboard.spec.ts` |
| DASH-003 | Start Practice button | Click Start Practice with selected learner | `testid-start-practice-button` | `dashboard.spec.ts` |
| DASH-004 | PIN verification | Enter correct/incorrect PIN | PIN input | `dashboard.spec.ts` |

### Table 3: Practice Flow Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| PRAC-001 | Start practice session | Navigate to practice with user | Practice page elements | `practice-flow.spec.ts` |
| PRAC-002 | Answer question | Enter answer and check | `testid-answer-input`, `testid-check-answer-button` | `practice-flow.spec.ts` |
| PRAC-003 | Navigate questions | Use Next/Previous buttons | `testid-next-button`, `testid-previous-button` | `practice-flow.spec.ts` |
| PRAC-004 | Flag question | Flag a question for review | `testid-flag-button` | `practice-flow.spec.ts` |
| PRAC-005 | Progress indicator | Verify progress bar updates | `testid-progress-bar` | `practice-flow.spec.ts` |
| PRAC-006 | Submit session | Complete all questions and submit | `testid-submit-session-button` | `practice-flow.spec.ts` |

### Table 4: Session Submission Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| SUB-001 | Submit practice session | Complete session and verify submission | Summary page | `session-submission.spec.ts` |
| SUB-002 | Session accuracy calculation | Verify correct accuracy shown | Summary stats | `session-submission.spec.ts` |
| SUB-003 | Session time tracking | Verify time is recorded | Summary stats | `session-submission.spec.ts` |
| SUB-004 | Incomplete session handling | Navigate away mid-session | Browser navigation | `session-submission.spec.ts` |

### Table 5: Test Flow Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| TEST-001 | Test eligibility check | Verify test requirements displayed | Journey/Test tabs | `test-flow.spec.ts` |
| TEST-002 | Start eligible test | Begin test when eligible | Test start button | `test-flow.spec.ts` |
| TEST-003 | Test submission | Complete and submit test | Submit button | `test-flow.spec.ts` |
| TEST-004 | Test retake eligibility | Check retake requirements | Test UI | `test-flow.spec.ts` |

### Table 6: Leveling Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| LVL-001 | Level up eligibility | Check if user can level up | Level card/API | `leveling.spec.ts` |
| LVL-002 | Level up achievement requirements | Verify required achievements | Journey page | `leveling.spec.ts` |
| LVL-003 | Level up after requirements met | Complete requirements and level up | Level up button | `leveling.spec.ts` |
| LVL-004 | Level up blocks | Verify level up blocked when requirements not met | Level UI | `leveling.spec.ts` |

### Table 7: Achievement Tests

| Test ID | Test Name | Description | Achievement Categories | File |
|---------|-----------|-------------|------------------------|------|
| ACH-001 | Milestone achievements | Earn milestone achievements | Milestone | `achievements.spec.ts` |
| ACH-002 | Accuracy achievements | Earn accuracy-based achievements | Accuracy | `achievements.spec.ts` |
| ACH-003 | Speed achievements | Earn speed-based achievements | Speed | `achievements.spec.ts` |
| ACH-004 | Consistency achievements | Earn consistency achievements | Consistency | `achievements.spec.ts` |
| ACH-006 | Level mastery achievements | Earn level-specific achievements | Level Mastery | `achievements.spec.ts` |
| ACH-007 | Progression achievements | Earn progression achievements | Progression | `achievements.spec.ts` |
| ACH-008 | Achievement display | Verify achievements shown on dashboard | Achievement cards | `achievements.spec.ts` |
| ACH-009 | Achievement progress | Check progress toward locked achievements | Journey page | `achievements.spec.ts` |

### Table 8: Journey/Progress Page Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| JRN-001 | Journey page loads | Open journey modal | Journey modal | `journey-page.spec.ts` |
| JRN-002 | Overview tab | View overview tab | Overview tab | `journey-page.spec.ts` |
| JRN-003 | Achievements tab | View achievements tab | Achievements tab | `journey-page.spec.ts` |
| JRN-005 | Level progression | View level requirements | Level progression UI | `journey-page.spec.ts` |
| JRN-006 | Filter achievements | Filter by category/tier | Filter controls | `journey-page.spec.ts` |

### Table 9: Summary Page Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| SUM-001 | Summary page loads | After session submission | Summary page | `summary-page.spec.ts` |
| SUM-002 | Summary stats | Verify accuracy, time, questions | Summary stats cards | `summary-page.spec.ts` |
| SUM-003 | Problem grid | View answered problems | Problem grid | `summary-page.spec.ts` |
| SUM-004 | Problem detail modal | Click problem to see details | Problem cards | `summary-page.spec.ts` |
| SUM-005 | Practice again | Click Practice Again button | `testid-practice-again-button` | `summary-page.spec.ts` |
| SUM-006 | Try next level | Click Try Next Level (if leveled up) | `testid-try-next-level-button` | `summary-page.spec.ts` |
| SUM-007 | Review flagged | Click Review Flagged | `testid-review-flagged-button` | `summary-page.spec.ts` |

### Table 10: Page Load Tests

| Test ID | Test Name | Description | Test IDs Used | File |
|---------|-----------|-------------|---------------|------|
| PAGE-001 | Main dashboard page loads | Verify dashboard loads | `testid-select-learner-header` | `page-load.spec.ts` |
| PAGE-002 | Practice page loads | Verify practice page loads | Body element | `page-load.spec.ts` |
| PAGE-003 | Summary page loads | Verify summary page loads | Body element | `page-load.spec.ts` |
| PAGE-004 | Test IDs present | Verify test IDs on interactive elements | Various test IDs | `page-load.spec.ts` |

## Test Statistics

- **Total Test Files**: 10
- **Total Test Cases**: 50+
- **Test Categories**: 10
- **Test Helpers**: 1 (`helpers/test-helpers.ts`)
- **Test Fixtures**: 1 (`fixtures/test-user.ts`)

## Test Isolation & Concurrency

All tests use unique test users to ensure:
- **No conflicts** between parallel test runs
- **Test isolation** - each test is independent
- **Automatic cleanup** - test users are deleted after each test
- **Unique naming** - Format: `TestUser_{testName}_{timestamp}_{random}`

## Running Specific Tests

### Run a single test file:
```bash
npx playwright test e2e/learner-management.spec.ts
```

### Run a specific test:
```bash
npx playwright test --grep "LM-001"
```

### Run tests in UI mode:
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser):
```bash
npx playwright test --headed
```

## Test Helpers

The test suite includes helper functions in `e2e/helpers/test-helpers.ts`:

- `generateTestUserName(testName)` - Generate unique test user names
- `createTestUser(request, options)` - Create a test user via API
- `deleteTestUser(request, userId)` - Delete a test user via API
- `getUser(request, userId)` - Get user details via API
- `listUsers(request)` - List all users via API
- `waitForVisible(element, timeout)` - Wait for element visibility
- `waitForAPIResponse(page, urlPattern, timeout)` - Wait for API response

## Test Fixtures

The test suite includes Playwright fixtures in `e2e/fixtures/test-user.ts`:

- `testUser` - Auto-creates and cleans up a unique test user for each test
- `authenticatedPage` - Page with test user context already set up

Usage:
```typescript
test('my test', async ({ testUser, page }) => {
  // testUser is automatically created and will be cleaned up
  console.log(testUser.name) // e.g., "TestUser_MyTest_1701234567_a3f2"
})
```

## Test Data IDs Reference

All interactive UI elements have `data-testid` attributes for reliable test targeting:

### Practice Components
- `testid-answer-input` - Answer input field
- `testid-check-answer-button` - Check Answer button
- `testid-question-display` - Question display area
- `testid-next-button` - Next question button
- `testid-previous-button` - Previous question button
- `testid-flag-button` - Flag for Review button
- `testid-submit-session-button` - Submit Session button
- `testid-progress-bar` - Progress indicator

### Dashboard Components
- `testid-student-grid` - Student grid container
- `testid-student-card-{id}` - Individual student cards
- `testid-select-learner-header` - Select Learner header
- `testid-start-practice-button` - Start Practice button

### Summary Components
- `testid-back-to-dashboard-button` - Back to Dashboard button
- `testid-practice-again-button` - Practice Again button
- `testid-try-next-level-button` - Try Next Level button
- `testid-review-flagged-button` - Review Flagged button

## Testing Framework

The E2E tests use a comprehensive testing framework with abstractions for common patterns. See [FRAMEWORK_GUIDE.md](./FRAMEWORK_GUIDE.md) for detailed documentation.

### Key Framework Features

- **Router Navigation**: URL-based navigation helpers for direct route access
- **Component Waiting**: Smart component waiting with animation handling
- **Scenario Builder**: Fluent API for test data preparation
- **Loading Utilities**: Utilities for handling loading states and animations

### Framework Usage Examples

#### Router-Based Navigation

```typescript
import { navigateToJourneyTab } from './helpers/test-helpers'

// Navigate directly to journey tab (no modal clicks needed)
await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'milestone' })
```

#### Scenario Builder

```typescript
import { scenario } from './helpers/test-helpers'

const context = await scenario()
  .withUser({ level: 2 })
  .withAchievements(['addition-basics', 'first-victory'])
  .withCompletedSessions(1, 5)
  .build(request)

try {
  // Test logic
} finally {
  await context.cleanup()
}
```

#### Component Waiting

```typescript
import { waitForComponent, waitForFramerMotion } from './helpers/test-helpers'

// Wait for component with animation handling
await waitForComponent(page, 'testid-achievements-grid')

// Wait for animations to complete
await waitForFramerMotion(page)
```

## Notes for Engineers

1. **Test Isolation**: Each test must use unique test users - never hardcode user IDs
2. **Cleanup**: Always clean up test data in teardown hooks (handled automatically by fixtures)
3. **API First**: Use API calls for setup/teardown, UI for verification
4. **Wait Strategies**: Use framework helpers (`waitForComponent`, `waitForFramerMotion`) instead of fixed timeouts
5. **Test IDs**: Always use `data-testid` attributes for element selection
6. **Parallel Safety**: Tests should be able to run in parallel without conflicts
7. **Error Handling**: Tests should handle API errors gracefully and provide clear failure messages
8. **Router Navigation**: Use URL-based navigation when testing destination features (see FRAMEWORK_GUIDE.md)
9. **Scenario Builder**: Use the scenario builder for complex test data setup

