# E2E Test Failures - Root Cause Analysis

**Date:** 2025-01-03  
**Total Failures:** 11  
**Total Tests:** 74  
**Pass Rate:** 85.1%

## Executive Summary

This document provides a comprehensive Root Cause Analysis (RCA) for all failing E2E tests. The failures fall into several categories:

1. **Timing/Race Conditions** (6 failures) - Tests failing due to async state updates, animations, or network delays
2. **Data State Issues** (3 failures) - Tests failing due to incorrect data setup or state assumptions
3. **UI Element Visibility** (2 failures) - Tests failing due to elements not being visible when expected

---

## Failure #1: ACH-008 - Achievement Status Display

**Test File:** `achievements.spec.ts:148`  
**Test ID:** `ACH-008: Achievement status display`  
**Error:** `expect(locator('[data-testid="testid-achievement-unlock-icon"]').first()).toBeVisible() failed`

### Root Cause
The test creates a user with achievements (`first-victory`, `addition-basics`) and expects to see unlock icons. However, the unlock icon only appears when `achievement.status !== 'locked'`. The issue is likely:

1. **Achievement Status Not Set Correctly**: The `createTestUserWithState` helper awards achievements via `/api/users/${userId}/test-setup`, but the frontend may not immediately reflect the "unlocked" status
2. **Timing Issue**: The test checks for unlock icons before the achievement data has fully loaded and been processed by the frontend
3. **Achievement Mapping**: The achievement codes used in the test (`first-victory`, `addition-basics`) may not match the actual achievement codes in the system

### Evidence
- Error context shows achievements are displayed but no unlock icons are visible
- The `AchievementCard` component renders unlock icons conditionally: `{isLocked ? <Lock /> : <Unlock />}`
- The test waits for `waitForDataLoad` and `waitForFramerMotion`, but may not wait long enough for achievement status to be determined

### Recommended Fix
1. Verify achievements are actually unlocked after `createTestUserWithState` by checking via API
2. Add explicit wait for achievement status to be determined (check for `unlockedAt` field)
3. Verify achievement codes match the actual system codes
4. Consider checking achievement status via API before UI assertions

---

## Failure #2: DEV-004 - Dev Mode Persists Across Navigation

**Test File:** `dev-mode.spec.ts:144`  
**Test ID:** `DEV-004: Dev mode persists across navigation`  
**Error:** `expect(locator('[data-testid^="testid-student-card-"]').filter({ hasText: 'TestUser_Test_...' }).first()).toBeVisible() failed`

### Root Cause
The test navigates to dashboard with dev mode (`/?env=dev`), opens journey modal, navigates between tabs, and then expects to find the user card. The failure occurs in `openJourneyModal` when trying to find the user card by name.

**Primary Issues:**
1. **User Card Not Rendered**: After navigation, the user card may not be immediately visible in the DOM
2. **Timing Issue**: The `openJourneyModal` helper uses `waitForTimeout(500)` which may be insufficient after tab navigation
3. **Name Matching**: The test user name may not match exactly what's displayed in the card (whitespace, formatting)

### Evidence
- Error shows user card with specific test name not found
- The `openJourneyModal` helper looks for cards by name: `.filter({ hasText: testUser.name })`
- Multiple test users may exist from previous test runs, causing name collisions

### Recommended Fix
1. Use `waitForSelector` with test ID instead of name matching
2. Increase wait times after navigation
3. Ensure test user cleanup happens before test starts
4. Use more specific selectors: `page.getByTestId(\`testid-student-card-${testUser.id}\`)`

---

## Failure #3: SUM-007 - Review Flagged

**Test File:** `summary-page.spec.ts:332`  
**Test ID:** `SUM-007: Review flagged`  
**Error:** Button not found or not visible

### Root Cause
The test flags a question during practice, submits the session, and expects to see a "Review Flagged" button on the summary page. The button may not appear if:

1. **No Flagged Questions**: The flag may not persist through session submission
2. **Conditional Rendering**: The Review Flagged button only appears when there are flagged questions
3. **Timing Issue**: The button may appear after the test checks for it

### Evidence
- Test flags a question via UI, then submits
- The flag state may not be properly saved to the backend
- The summary page may not receive flagged question data

### Recommended Fix
1. Verify flagging persists via API before submitting
2. Check if flagged questions are included in session completion payload
3. Add explicit wait for Review Flagged button with longer timeout
4. Verify flagged questions are returned in summary page data

---

## Failure #4: LVL-003 - Level Up After Requirements Met

**Test File:** `leveling.spec.ts:68`  
**Test ID:** `LVL-003: Level up after requirements met`  
**Error:** `expect(received).toBe(expected) // Expected: 2, Received: 1`

### Root Cause
The test creates a user at level 1 with achievement `addition-1digit-bronze` (required for level 2), attempts to level up via API, and expects the level to be 2. However, the level remains at 1.

**Primary Issues:**
1. **Wrong Achievement Code**: The achievement code `addition-1digit-bronze` may not be the correct requirement for level 2
2. **Level Up Logic**: The level up API may have additional requirements not met
3. **Achievement Not Awarded**: The achievement may not have been properly awarded via test setup

### Evidence
- Test awards `addition-1digit-bronze` and expects level up to work
- Level up API call succeeds (200 OK) but level doesn't change
- Need to verify actual level 2 requirements

### Recommended Fix
1. Verify the correct achievement code for level 2 requirements
2. Check level up API response for error messages
3. Verify achievement was actually awarded before level up attempt
4. Check if there are multiple requirements for level 2 (not just one achievement)

---

## Failures #5-10: Submit Button Not Ready (Multiple Tests)

**Test Files:**
- `session-submission.spec.ts:17` (SUB-001)
- `session-submission.spec.ts:36` (SUB-002)
- `session-submission.spec.ts:53` (SUB-003)
- `practice-flow.spec.ts:170` (PRAC-006)
- Additional tests using `completePracticeSession`

**Error:** `Submit button not ready: visible=false, enabled=false`

### Root Cause
Multiple tests fail because the submit button is not visible or enabled after completing all questions. The `canSubmit` logic in `usePracticeSession` requires:

```typescript
canSubmit = problems.length > 0 && 
  problems.every((problem) => {
    const answer = questionAnswers[problem.id]
    return answer?.isChecked
  })
```

**Primary Issues:**
1. **Answer State Not Updated**: After answering questions, the `questionAnswers` state may not be updated with `isChecked: true`
2. **Timing Issue**: The submit button appears conditionally based on `canSubmit`, which is a `useMemo` that may not update immediately
3. **Question Navigation**: The test may not be properly navigating through all questions, leaving some unanswered
4. **State Synchronization**: React state updates are async, and the test may check before state has updated

### Evidence
- `completePracticeSession` helper answers all questions and checks for submit button
- The `isSubmitButtonReady` function uses short timeouts (1 second) which may be too short
- The submit button only appears when `canSubmit` is true, which depends on all questions being checked

### Recommended Fix
1. **Increase Wait Times**: Add longer waits after answering each question for state to update
2. **Verify Answer State**: After answering, verify `questionAnswers[problem.id].isChecked === true` before moving to next question
3. **Wait for State Update**: After completing all questions, wait for `canSubmit` to become true (check via React DevTools or add test ID to submit button wrapper)
4. **Fix `completePracticeSession`**: Ensure it properly waits for state updates between questions
5. **Add Retry Logic**: Retry checking submit button with exponential backoff

### Code Changes Needed
```typescript
// In completePracticeSession helper
// After answering each question, wait for state to update
await page.waitForFunction(() => {
  // Check if current question's answer is checked
  // This requires exposing state or checking UI indicators
}, { timeout: 5000 })

// After all questions answered, wait for canSubmit
await page.waitForFunction(() => {
  const submitButton = document.querySelector('[data-testid="testid-submit-session-button"]')
  return submitButton && !submitButton.disabled
}, { timeout: 10000 })
```

---

## Failure #11: SUB-004 - Session Restoration Question Text Mismatch

**Test File:** `session-submission.spec.ts:69`  
**Test ID:** `SUB-004: Incomplete session handling with backend restoration`  
**Error:** `expect(normalizedRestored).toContain(normalizedExpected.split(' ')[0])` failed

### Root Cause
The test starts a session via API, answers the first question via API, then navigates to practice page expecting to see the second question. However, the question text doesn't match.

**Primary Issues:**
1. **Question Ordering**: The backend may return questions in a different order than expected
2. **Question Text Formatting**: The question text may be formatted differently when displayed in UI vs API response
3. **Session Restoration Logic**: The session restoration may not preserve question order correctly

### Evidence
- Test expects second question but gets different question text
- Error shows: `Expected substring: "9"`, `Received string: "1+8"`
- The question text comparison is too strict (only checks first number)

### Recommended Fix
1. **Verify Question Order**: Check backend API to confirm question ordering after partial completion
2. **Relax Assertion**: Instead of checking exact question text, verify that:
   - A question is displayed (not the first one that was answered)
   - The question is from the same session
   - The session was restored from backend (not localStorage)
3. **Better Verification**: Check session ID or question IDs instead of text content
4. **Wait for Restoration**: Add explicit wait for session restoration to complete before checking question

---

## Common Patterns Across Failures

### 1. Timing and Async State Issues
- **Pattern**: Tests fail because they check for UI state before React has updated
- **Solution**: Add explicit waits for state updates, use `waitForFunction` instead of fixed timeouts

### 2. Test Data Setup Issues
- **Pattern**: Tests assume data is in a certain state but it's not
- **Solution**: Verify test data setup via API before UI assertions

### 3. Element Visibility Issues
- **Pattern**: Elements exist in DOM but aren't visible when test checks
- **Solution**: Use `waitForSelector` with visibility checks, scroll elements into view

### 4. State Synchronization
- **Pattern**: React state updates are async, tests check too early
- **Solution**: Wait for state indicators (disabled states, text changes) before assertions

---

## Recommended Action Items

### High Priority
1. **Fix Submit Button Issues** (Affects 6+ tests)
   - Update `completePracticeSession` to properly wait for state updates
   - Add retry logic for submit button checks
   - Verify answer state after each question

2. **Fix Achievement Status** (ACH-008)
   - Verify achievement codes match system
   - Add API verification before UI checks
   - Wait for achievement status to be determined

3. **Fix User Card Lookup** (DEV-004)
   - Use test ID instead of name matching
   - Add proper waits after navigation
   - Ensure test user cleanup

### Medium Priority
4. **Fix Level Up Test** (LVL-003)
   - Verify correct achievement codes for level requirements
   - Check level up API response for errors
   - Verify all requirements are met

5. **Fix Session Restoration** (SUB-004)
   - Relax question text assertions
   - Verify session ID instead of text
   - Add proper waits for restoration

6. **Fix Review Flagged** (SUM-007)
   - Verify flagging persists via API
   - Check conditional rendering logic
   - Add explicit waits

### Low Priority
7. **Improve Test Helpers**
   - Add better error messages
   - Add retry logic for flaky operations
   - Improve logging for debugging

8. **Test Stability**
   - Review all fixed timeouts, replace with state-based waits
   - Add test isolation improvements
   - Consider test retry strategy for flaky tests

---

## Testing Recommendations

1. **Run Tests Individually**: Run each failing test in isolation to verify fixes
2. **Add Debug Logging**: Add console.log statements to track test execution
3. **Use Playwright UI Mode**: Run tests in UI mode to see what's happening
4. **Screenshot on Failure**: Add screenshot capture on test failures
5. **API Verification**: Verify backend state via API before UI assertions

---

## Notes

- All tests use `--workers=1` to ensure isolation
- Backend server must be running on port 5004
- Frontend dev server runs on port 5003
- Test users are auto-created and cleaned up
- Some tests may be flaky due to timing issues

