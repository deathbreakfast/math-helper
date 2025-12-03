# Parallel E2E Test Issues

## Summary

When running e2e tests with 4 workers in parallel, some tests fail that pass when run sequentially or one section at a time in the UI.

## Test Results with 4 Workers

- **Total Tests**: 74
- **Passed**: 69
- **Failed**: 5
- **Duration**: ~1.7 minutes

## Failing Tests

The following tests fail when running with 4 workers but pass when run individually:

1. **ACH-008: Achievement status display** (`achievements.spec.ts:148`)
   - Error: `expect(locator).toBeVisible()` failed
   - Locator: `[data-testid="testid-achievement-unlock-icon"]`
   - Issue: Unlock icons not found/visible within timeout
   - Potential cause: Race condition with achievement rendering or animation timing

2. **SUB-004: Incomplete session handling with backend restoration** (`session-submission.spec.ts:69`)
   - Error: `Submit button not ready: visible=false, enabled=false`
   - Issue: Submit button not becoming ready in time
   - Potential cause: Session state not fully restored before test continues

3. **SUM-001: Summary page loads with backend session restoration** (`summary-page.spec.ts:13`)
   - Error: `Submit button not ready: visible=false, enabled=false`
   - Issue: Submit button not ready when trying to submit practice session
   - Potential cause: Backend session restoration timing issues

4. **SUM-002: Summary stats** (`summary-page.spec.ts:71`)
   - Error: `Submit button not ready: visible=false, enabled=false`
   - Issue: Same as SUM-001 - submit button readiness
   - Potential cause: Shared state or timing issues

5. **SUM-007: Review flagged** (`summary-page.spec.ts:332`)
   - Error: `Submit button not ready: visible=false, enabled=false`
   - Issue: Same submit button readiness problem
   - Potential cause: Parallel test execution affecting session state

## Common Patterns

### Submit Button Readiness Issues
4 out of 5 failures involve the submit button not being ready:
- All in `summary-page.spec.ts` and `session-submission.spec.ts`
- All use `submitPracticeSession()` helper
- Error occurs at `helpers/ui/practice-helpers.ts:255`

### Achievement Display Issues
1 failure involves achievement unlock icons not appearing:
- Test waits for unlock icons but they don't appear in time
- May be related to animation timing or data loading race conditions

## Potential Root Causes

1. **Shared Test Data**: Tests may be interfering with each other's data when running in parallel
2. **Timing Issues**: Race conditions with:
   - Backend session restoration
   - UI animations (Framer Motion)
   - Data loading states
   - Submit button state management
3. **Resource Contention**: Multiple tests hitting the same backend endpoints simultaneously
4. **State Isolation**: Test cleanup may not be happening fast enough between parallel runs

## How to Run Tests with 4 Workers

### Option 1: Using npm script
```bash
npm run test:e2e:workers
```

### Option 2: Using command flag
```bash
npm run test:e2e -- --workers=4
```

### Option 3: Direct playwright command
```bash
npx playwright test --workers=4
```

## Next Steps / TODO

- [ ] Investigate submit button readiness timing in `helpers/ui/practice-helpers.ts`
  - Review `isSubmitButtonReady()` function
  - Consider adding longer timeouts or better waiting logic
  - Check if parallel execution affects button state updates

- [ ] Review achievement unlock icon rendering
  - Check animation timing in achievement cards
  - Verify data loading completes before checking for icons
  - Consider adding explicit waits for achievement data

- [ ] Improve test isolation
  - Ensure each test uses unique user IDs
  - Verify cleanup happens properly in parallel scenarios
  - Check for shared state between tests

- [ ] Review backend session restoration
  - Verify session state is fully restored before UI checks
  - Add explicit waits for session restoration completion
  - Check for race conditions in session state management

- [ ] Consider test grouping
  - Group related tests that might interfere with each other
  - Use Playwright's `test.describe.serial()` for tests that must run sequentially
  - Review if any tests should be excluded from parallel execution

- [ ] Add better error context
  - Capture screenshots on failure
  - Log more detailed state information when submit button isn't ready
  - Add debug logging for parallel execution scenarios

## Related Files

- `frontend/e2e/helpers/ui/practice-helpers.ts` - Submit button logic
- `frontend/e2e/achievements.spec.ts` - Achievement display tests
- `frontend/e2e/session-submission.spec.ts` - Session submission tests
- `frontend/e2e/summary-page.spec.ts` - Summary page tests
- `frontend/playwright.config.ts` - Test configuration

