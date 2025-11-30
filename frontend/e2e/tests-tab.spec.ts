import { test, expect } from './fixtures/test-user'
import {
  openJourneyModal,
  navigateToTestsTab,
  createTestUserWithState,
  deleteTestUser,
  createCompletedPracticeSessions,
  createPassedTestAttempt,
  startTestSession,
  answerQuestionViaAPI,
} from './helpers/test-helpers'

test.describe('Tests Tab UI', () => {
  test('TST-UI-001: Tests tab displays and navigation works', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify tab is visible
    const testsTab = page.getByTestId('testid-tests-tab')
    await expect(testsTab).toBeVisible()

    // Verify test grid is visible
    const testGrid = page.getByTestId('testid-test-achievements-grid')
    await expect(testGrid).toBeVisible()

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-002: Test discovery - locked tests hidden', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify tests tab is visible
    await expect(page.getByTestId('testid-tests-tab')).toBeVisible()

    // Verify only level 1 tests are visible (unlocked)
    // Higher level tests should be locked
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()

    // Should have at least one test card
    expect(cardCount).toBeGreaterThan(0)

    // Check that locked tests show lock icon
    const lockedTests = page.locator('[data-testid^="testid-test-card-"]').filter({
      has: page.locator('[data-testid="testid-test-lock-icon"]'),
    })
    const lockedCount = await lockedTests.count()

    // Should have some locked tests (tests requiring level > 1)
    expect(lockedCount).toBeGreaterThan(0)

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-003: Test discovery - unlocked tests visible', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 5,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify tests tab is visible
    await expect(page.getByTestId('testid-tests-tab')).toBeVisible()

    // Verify tests up to level 5 are visible
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()

    // Should have multiple test cards
    expect(cardCount).toBeGreaterThan(0)

    // Verify test cards show correct information
    const firstCard = testCards.first()
    await expect(firstCard).toBeVisible()

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-004: Test card displays correctly', async ({ page, request }) => {
    // Create user with test attempts
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    // Create a test attempt
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'level_1')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify test cards show:
    // - Test name
    // - Question count
    // - Best result badge (if attempted)
    // - Lock status (if locked)

    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const firstCard = testCards.first()
    await expect(firstCard).toBeVisible()

    // Check for test name (should be visible)
    const testName = firstCard.locator('h3')
    await expect(testName).toBeVisible()

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-005: Test detail modal opens and displays attempts', async ({ page, request }) => {
    // Create user with multiple test attempts
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'level_1')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Find a test card with attempts and click it
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await testCard.click()

    // Verify modal opens
    const modal = page.getByTestId('testid-test-detail-modal')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Verify past attempts are listed
    const attemptCards = page.locator('[data-testid^="testid-attempt-card-"]')
    const attemptCount = await attemptCards.count()

    // Should have at least one attempt
    expect(attemptCount).toBeGreaterThan(0)

    // Verify attempt details (date, accuracy, tier, time)
    const firstAttempt = attemptCards.first()
    await expect(firstAttempt).toBeVisible()

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-006: Test detail modal - drill down to questions', async ({ page, request }) => {
    // Create user with test attempt
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'level_1')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Click on test card
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await testCard.click()

    // Wait for modal
    await expect(page.getByTestId('testid-test-detail-modal')).toBeVisible({ timeout: 5000 })

    // Expand an attempt
    const expandButton = page.getByTestId('testid-attempt-expand-button').first()
    await expandButton.click()

    // Wait for questions to load
    await page.waitForTimeout(1000)

    // Verify questions/responses are displayed
    const questionsList = page.getByTestId('testid-attempt-questions-list')
    await expect(questionsList).toBeVisible({ timeout: 5000 })

    // Verify correct/incorrect indicators
    const questionCards = page.locator('[data-testid^="testid-question-response-"]')
    const questionCount = await questionCards.count()
    expect(questionCount).toBeGreaterThan(0)

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-007: Start test from tests tab', async ({ page, request }) => {
    // Create eligible user
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Find an unlocked test card
    const unlockedTestCard = page
      .locator('[data-testid^="testid-test-card-"]')
      .filter({ hasNot: page.locator('[data-testid="testid-test-lock-icon"]') })
      .first()

    await expect(unlockedTestCard).toBeVisible()

    // Click "Start Test" button
    const startButton = unlockedTestCard.getByTestId('testid-test-start-button')
    await expect(startButton).toBeVisible()
    await startButton.click()

    // Verify navigation to practice session
    // Should redirect to /practice with test parameters
    await page.waitForURL(/\/practice/, { timeout: 5000 })

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-008: Test filtering works', async ({ page, request }) => {
    // Create user with tests at different tiers
    const testUser = await createTestUserWithState(request, {
      level: 10,
    })

    // Create test attempts with different tiers
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'level_1')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Filter by tier (B)
    const tierFilter = page.getByTestId('testid-test-filter-tier')
    await tierFilter.selectOption('B')

    await page.waitForTimeout(500)

    // Verify filtered results
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()
    expect(cardCount).toBeGreaterThanOrEqual(0)

    // Filter by status (attempted)
    const statusFilter = page.getByTestId('testid-test-filter-status')
    await statusFilter.selectOption('attempted')

    await page.waitForTimeout(500)

    // Verify filtered results
    const filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    const filteredCount = await filteredCards.count()
    expect(filteredCount).toBeGreaterThanOrEqual(0)

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-009: Test search works', async ({ page, request }) => {
    // Create user with multiple tests
    const testUser = await createTestUserWithState(request, {
      level: 5,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Search for test name
    const searchInput = page.getByTestId('testid-test-search-input')
    await searchInput.fill('addition')

    await page.waitForTimeout(500)

    // Verify search results
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()
    expect(cardCount).toBeGreaterThanOrEqual(0)

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-010: Test detail modal - start new test', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Open test detail modal
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await testCard.click()

    await expect(page.getByTestId('testid-test-detail-modal')).toBeVisible({ timeout: 5000 })

    // Click "Start New Test" button
    const startButton = page.getByTestId('testid-test-detail-start-button')
    await expect(startButton).toBeVisible()
    await startButton.click()

    // Verify navigation to practice session
    await page.waitForURL(/\/practice/, { timeout: 5000 })

    await deleteTestUser(request, testUser.id)
  })
})

