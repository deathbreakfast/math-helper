# Testing Framework Guide

This guide provides an overview of the testing framework abstractions available for writing E2E tests in the Math Helper application.

## Overview

The testing framework provides reusable helpers for common test patterns, making tests more maintainable, reliable, and easier to write. The framework includes:

- **Core Testing Framework**: Scenario setup, component waiting, cleanup
- **Router Navigation Helpers**: URL-based navigation for tests
- **Loading & Animation Utilities**: Handling loading states and animations
- **Test Scenarios Builder**: Fluent API for test data preparation

## Core Testing Framework

### Scenario Setup and Cleanup

#### `setupTestScenario(request, scenario)`

Creates a test scenario with user, achievements, sessions, etc.

```typescript
import { setupTestScenario } from './helpers/test-helpers'

const context = await setupTestScenario(request, {
  user: { level: 2 },
  achievements: ['addition-basics', 'first-victory'],
  sessions: [{ level: 1, count: 5 }]
})

// Use context.user, context.scenario, etc.
// Cleanup: await context.cleanup()
```

#### `runTestWithScenario(page, request, scenario, testFn)`

Runs a test with automatic setup and cleanup.

```typescript
import { runTestWithScenario } from './helpers/test-helpers'

await runTestWithScenario(
  page,
  request,
  { user: { level: 1 }, achievements: ['first-victory'] },
  async (context) => {
    // Test logic here
    // context.user is available
    // Cleanup happens automatically
  }
)
```

### Component Waiting

#### `waitForComponent(page, testId, options?)`

Waits for a component to be visible/ready with smart waiting logic.

```typescript
import { waitForComponent } from './helpers/test-helpers'

// Wait for component with default options
await waitForComponent(page, 'testid-achievements-grid')

// Wait with custom options
await waitForComponent(page, 'testid-level-card', {
  timeout: 15000,
  state: 'visible',
  waitForAnimation: true
})
```

#### `waitForComponents(page, testIds, options?)`

Waits for multiple components to be ready.

```typescript
import { waitForComponents } from './helpers/test-helpers'

await waitForComponents(page, [
  'testid-achievements-grid',
  'testid-achievement-card-first-victory'
])
```

## Router Navigation Helpers

### URL-Based Navigation

Use URL navigation when the navigation mechanism (button click, etc.) is already tested in a dedicated test. This allows tests to focus on the destination state/feature rather than repeating the same navigation steps.

**Important**: 
- Always test the navigation mechanism (clicks, buttons, PIN entry, etc.) in at least one dedicated test
- Once that navigation path is verified, other tests can use URL navigation to efficiently reach the feature being tested
- Example: If you have a test that verifies clicking "Start Practice" + entering PIN works, other tests can use `navigateToPractice()` to skip repeating those steps

#### `navigateToJourneyTab(page, userId, tab, filters?)`

Navigate to a specific journey tab with optional filters.

```typescript
import { navigateToJourneyTab } from './helpers/test-helpers'

// Navigate to achievements tab
await navigateToJourneyTab(page, testUser.id, 'achievements')

// Navigate with filter
await navigateToJourneyTab(page, testUser.id, 'achievements', {
  category: 'milestone',
  filter: 'first-victory'
})

// Available tabs: 'overview' | 'achievements' | 'levels' | 'tests'
```

#### `navigateToDashboard(page, selectedUserId?)`

Navigate to dashboard with optional user selection.

```typescript
import { navigateToDashboard } from './helpers/test-helpers'

// Navigate to dashboard
await navigateToDashboard(page)

// Navigate with user selected
await navigateToDashboard(page, testUser.id)
```

#### `navigateToRoute(page, route, params?)`

Navigate to any route via URL.

```typescript
import { navigateToRoute } from './helpers/test-helpers'

// Navigate to practice
await navigateToRoute(page, '/practice', { userId: '123' })

// Navigate to summary
await navigateToRoute(page, '/summary', { sessionId: '456' })
```

## Loading & Animation Utilities

### Animation Handling

#### `waitForFramerMotion(page, selector?, duration?)`

Waits for framer-motion animations to complete.

```typescript
import { waitForFramerMotion } from './helpers/test-helpers'

// Wait for default animation duration (800ms)
await waitForFramerMotion(page)

// Wait for specific element's animation
await waitForFramerMotion(page, '[data-testid="testid-card"]', 1000)
```

### Data Loading

#### `waitForDataLoad(page, testId, timeout?)`

Waits for data to load by checking for loading spinners and content appearance.

```typescript
import { waitForDataLoad } from './helpers/test-helpers'

await waitForDataLoad(page, 'testid-achievements-grid', 15000)
```

#### `waitForNetworkIdle(page, timeout?)`

Waits for network activity to complete.

```typescript
import { waitForNetworkIdle } from './helpers/test-helpers'

// Wait for all API calls to finish
await waitForNetworkIdle(page)
```

#### `waitForFullLoad(page, contentTestId, timeout?)`

Combines waiting for loading spinners, network idle, and content.

```typescript
import { waitForFullLoad } from './helpers/test-helpers'

await waitForFullLoad(page, 'testid-achievements-grid')
```

## Test Scenarios Builder

### Fluent API for Data Preparation

The scenario builder provides a fluent API for creating test scenarios.

#### Basic Usage

```typescript
import { scenario } from './helpers/test-helpers'

const context = await scenario()
  .withUser({ level: 2, name: 'Test User' })
  .withLevel(3)
  .withAchievements(['addition-basics', 'first-victory'])
  .withCompletedSessions(1, 5)
  .build(request)

// Use context.user, context.cleanup(), etc.
```

#### Scenario Builder Methods

- `.withUser(userConfig)` - Set user configuration
- `.withLevel(level)` - Set user level
- `.withAchievements(achievements)` - Add achievements
- `.withCompletedSessions(level, count)` - Add completed practice sessions
- `.build(request)` - Create the scenario
- `.reset()` - Reset the builder

#### Example: Complex Scenario

```typescript
const context = await scenario()
  .withUser({ level: 5, name: 'Advanced User' })
  .withAchievements([
    'addition-basics',
    'subtraction-basics',
    'multiplication-basics',
    'first-victory',
    'century-club'
  ])
  .withCompletedSessions(1, 10)
  .withCompletedSessions(2, 5)
  .withCompletedSessions(3, 3)
  .build(request)

try {
  // Test logic
  await navigateToJourneyTab(page, context.user.id, 'achievements')
  // ... assertions
} finally {
  await context.cleanup()
}
```

## Migration Guide

### Before (Old Pattern)

```typescript
// Old: Manual navigation and waits
await page.goto('/')
await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
await openJourneyModal(page, testUser)
await navigateToAchievementsTab(page)
await page.waitForTimeout(800) // Animation wait
```

### After (New Pattern)

```typescript
// New: Router-based navigation with smart waits
await navigateToJourneyTab(page, testUser.id, 'achievements')
await waitForComponent(page, 'testid-achievements-grid')
```

### Migration Checklist

1. Replace `page.goto('/')` + modal navigation with `navigateToJourneyTab()` (but keep one test that verifies the click navigation works)
2. Replace `page.waitForTimeout()` with `waitForFramerMotion()` or `waitForComponent()`
3. Replace manual test user creation with `scenario()` builder
4. Use `waitForDataLoad()` for components that load data
5. Use try/finally blocks with `context.cleanup()` for cleanup

### Navigation Testing Strategy

**Test navigation mechanisms in dedicated tests:**
- Test clicking the journey modal button → opens modal
- Test PIN entry → starts practice session  
- Test tab clicks → switches tabs correctly

**Use URL navigation in feature tests:**
- Once PIN entry is tested, use `navigateToPractice()` in practice feature tests
- Once journey modal opening is tested, use `navigateToJourneyTab()` in achievement/level tests
- This avoids repeating the same setup steps across multiple tests

**Example:**
```typescript
// In dashboard.spec.ts - Test the navigation mechanism
test('PIN entry starts practice session', async ({ page, testUser }) => {
  await navigateToDashboard(page, testUser.id)
  await clickStartPractice(page)
  await enterPin(page, testUser.pin)
  // Verify practice session started...
})

// In practice-flow.spec.ts - Use URL navigation since PIN entry is already tested
test('Practice session displays questions', async ({ page, testUser }) => {
  await navigateToPractice(page, { userId: testUser.id.toString() })
  // Focus on testing practice features, not navigation...
})
```

## Best Practices

1. **Test Navigation Once, Use URL Navigation Elsewhere**: 
   - Always test navigation mechanisms (clicks, buttons, PIN entry, etc.) in dedicated tests
   - Once a navigation path is verified, use URL navigation in other tests to focus on the destination feature
   - Example: Test PIN entry to start practice in one test; use `navigateToPractice()` in other tests that focus on practice features

2. **Always Wait for Components**: Use `waitForComponent()` instead of fixed timeouts for better reliability.

3. **Handle Animations**: Use `waitForFramerMotion()` after actions that trigger animations.

4. **Use Scenario Builder**: Use the scenario builder for complex test data setup.

5. **Always Cleanup**: Use try/finally blocks to ensure cleanup happens even if tests fail.

6. **Avoid Fixed Timeouts**: Use smart waiting functions instead of `page.waitForTimeout()`.

## Examples

See migrated test files for complete examples:
- `achievements.spec.ts` - Router navigation, component waiting
- `leveling.spec.ts` - Router navigation, data loading

