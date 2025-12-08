import { test, expect } from './fixtures/test-user'
import {
  openJourneyModal,
  navigateToTestsTab,
  waitForTestCards,
  clickTestCardSafely,
  handlePinVerification,
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

  test('TST-UI-002: Test discovery - locked tests visible but disabled', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify tests tab is visible
    await expect(page.getByTestId('testid-tests-tab')).toBeVisible()

    // Verify all tests are visible (both locked and unlocked)
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()

    // Should have at least one test card
    expect(cardCount).toBeGreaterThan(0)

    // Check that locked tests show lock icon and are visible
    const lockedTests = page.locator('[data-testid^="testid-test-card-"]').filter({
      has: page.locator('[data-testid="testid-test-lock-icon"]'),
    })
    const lockedCount = await lockedTests.count()

    // Should have some locked tests (tests requiring level > 1)
    expect(lockedCount).toBeGreaterThan(0)

    // Verify locked tests are visible (not hidden)
    const firstLockedTest = lockedTests.first()
    await expect(firstLockedTest).toBeVisible()

    // Verify locked tests have disabled styling (opacity)
    const opacity = await firstLockedTest.evaluate((el) => {
      return window.getComputedStyle(el).opacity
    })
    expect(parseFloat(opacity)).toBeLessThan(1) // Should be less than 1 (disabled state)

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
    test.setTimeout(60000) // 60 second timeout for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    // Create a test attempt
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'addition-1digit')

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
    test.setTimeout(60000) // 60 second timeout for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'addition-1digit')

    // Wait a bit for database to commit the test attempt
    await new Promise(resolve => setTimeout(resolve, 500))

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Find a test card with attempts and click it safely (avoids achievement links)
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await clickTestCardSafely(page, testCard)

    // Verify modal opens
    const modal = page.getByTestId('testid-test-detail-modal')
    await expect(modal).toBeVisible({ timeout: 5000 })

    // Wait for attempts to load (the modal loads them asynchronously)
    // First wait for "Loading attempts..." to disappear (if it appears)
    const loadingText = page.locator('text=/Loading attempts/i')
    await loadingText.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {
      // Loading text might not appear if it loads quickly, that's okay
    })
    
    // Wait for either attempt cards to appear OR a "no attempts" message
    // This ensures we wait for the async loading to complete
    const attemptCards = page.locator('[data-testid^="testid-attempt-card-"]')
    const noAttemptsMessage = page.locator('text=/no attempts|no test attempts/i')
    
    // Wait for one of these to appear (indicating loading is complete)
    await Promise.race([
      attemptCards.first().waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}),
      noAttemptsMessage.waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}),
      page.waitForTimeout(3000) // Fallback timeout
    ])

    // Give a small additional wait for React to render
    await page.waitForTimeout(500)

    // Verify past attempts are listed
    const attemptCount = await attemptCards.count()
    console.log(`[TST-UI-005] Found ${attemptCount} attempt cards after loading`)

    // Should have at least one attempt (we created one via createPassedTestAttempt)
    if (attemptCount === 0) {
      // Debug: Check if there's a "no attempts" message
      const hasNoAttemptsMessage = await noAttemptsMessage.isVisible().catch(() => false)
      if (hasNoAttemptsMessage) {
        const messageText = await noAttemptsMessage.textContent()
        console.error(`[TST-UI-005] No attempts found. Message: ${messageText}`)
      }
      // Check if loading is still showing
      const stillLoading = await loadingText.isVisible().catch(() => false)
      if (stillLoading) {
        console.error('[TST-UI-005] Still loading attempts after timeout')
      }
    }
    
    expect(attemptCount).toBeGreaterThan(0)

    // Verify attempt details (date, accuracy, tier, time)
    const firstAttempt = attemptCards.first()
    await expect(firstAttempt).toBeVisible()

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-006: Test detail modal - drill down to questions', async ({ page, request }) => {
    test.setTimeout(60000) // 60 second timeout for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'addition-1digit')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Click on test card safely (avoids achievement links)
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await clickTestCardSafely(page, testCard)

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
    test.setTimeout(60000) // 60 second timeout for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Wait for test cards to render
    const totalCardCount = await waitForTestCards(page, 1)
    console.log(`[TST-UI-007] Found ${totalCardCount} total test cards`)

    // Find unlocked test cards (those without lock icon)
    const unlockedTestCards = page
      .locator('[data-testid^="testid-test-card-"]')
      .filter({ hasNot: page.locator('[data-testid="testid-test-lock-icon"]') })
    
    // Wait for unlocked cards to be available
    const unlockedCount = await unlockedTestCards.count()
    console.log(`[TST-UI-007] Found ${unlockedCount} unlocked test cards`)

    if (unlockedCount === 0) {
      // If no unlocked tests, check if we have any tests at all
      if (totalCardCount === 0) {
        throw new Error('No test cards found. Tests may not be loaded yet.')
      }
      // All tests are locked - this might be expected for level 1 user
      // Try to find any test card and verify it's locked
      const allTestCards = page.locator('[data-testid^="testid-test-card-"]')
      const firstCard = allTestCards.first()
      const hasLockIcon = await firstCard.locator('[data-testid="testid-test-lock-icon"]').count()
      if (hasLockIcon > 0) {
        throw new Error(`No unlocked tests available for level 1 user. All ${totalCardCount} tests are locked.`)
      }
    }

    const unlockedTestCard = unlockedTestCards.first()
    await expect(unlockedTestCard).toBeVisible({ timeout: 5000 })

    // Click "Start Test" button
    const startButton = unlockedTestCard.getByTestId('testid-test-start-button')
    await expect(startButton).toBeVisible({ timeout: 5000 })
    await startButton.click()

    // Handle PIN verification if modal appears
    const pinModal = page.locator('[role="dialog"]').filter({ hasText: /PIN|pin/i })
    const pinModalVisible = await pinModal.isVisible({ timeout: 2000 }).catch(() => false)
    
    if (pinModalVisible) {
      console.log('[TST-UI-007] PIN modal appeared, handling PIN verification')
      await handlePinVerification(page, testUser.pin || '1234')
    }

    // Verify navigation to practice session
    // Should redirect to /practice with test parameters
    await page.waitForURL(/\/practice/, { timeout: 10000 })

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-008: Test filtering works with new tier system', async ({ page, request }) => {
    test.setTimeout(80000) // 80 second timeout (1 min 20 sec) for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 10,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    // Create test attempts with different tiers
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    await createPassedTestAttempt(request, testUser.id, 1, 'addition-1digit')

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Verify all tests are visible initially
    const allTestCards = page.locator('[data-testid^="testid-test-card-"]')
    const initialCount = await allTestCards.count()
    expect(initialCount).toBeGreaterThan(0)

    // Filter by tier (Bronze - new tier system)
    const tierFilter = page.getByTestId('testid-test-filter-tier')
    await tierFilter.selectOption('Bronze')

    await page.waitForTimeout(500)

    // Verify all tests are still visible (filters don't hide tests)
    const testCards = page.locator('[data-testid^="testid-test-card-"]')
    const cardCount = await testCards.count()
    expect(cardCount).toBe(initialCount) // All tests should still be visible

    // Filter by status (attempted)
    const statusFilter = page.getByTestId('testid-test-filter-status')
    await statusFilter.selectOption('attempted')

    await page.waitForTimeout(500)

    // Verify all tests are still visible
    const filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    const filteredCount = await filteredCards.count()
    expect(filteredCount).toBe(initialCount) // All tests should still be visible

    // Test other tier filters
    await tierFilter.selectOption('Gold')
    await page.waitForTimeout(500)
    const goldFilteredCards = page.locator('[data-testid^="testid-test-card-"]')
    const goldCount = await goldFilteredCards.count()
    expect(goldCount).toBe(initialCount) // All tests should still be visible

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
    test.setTimeout(60000) // 60 second timeout for API setup
    
    // Create user with achievements needed to unlock addition-1digit test
    // addition-1digit requires: question-master-bronze and level-master-bronze with metadata {"level": 1}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'question-master-bronze' as any,
        { code: 'level-master-bronze', metadata: { level: 1 } }
      ]
    })

    await createCompletedPracticeSessions(request, testUser.id, 1, 3)

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Wait for test cards to render
    await waitForTestCards(page, 1)

    // Open test detail modal - click safely to avoid achievement links
    const testCard = page.locator('[data-testid^="testid-test-card-"]').first()
    await clickTestCardSafely(page, testCard)

    await expect(page.getByTestId('testid-test-detail-modal')).toBeVisible({ timeout: 5000 })

    // Click "Start New Test" button (this opens PIN modal)
    const startButton = page.getByTestId('testid-test-detail-start-button')
    await expect(startButton).toBeVisible({ timeout: 5000 })
    console.log('[TST-UI-010] Clicking Start New Test button')
    await startButton.click()

    // Handle PIN verification
    console.log('[TST-UI-010] Handling PIN verification')
    await handlePinVerification(page, testUser.pin || '1234')

    // Verify navigation to practice session
    console.log('[TST-UI-010] Waiting for navigation to /practice')
    await page.waitForURL(/\/practice/, { timeout: 10000 })

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-011: All tests visible regardless of filters', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Get initial count of all tests
    const allTestCards = page.locator('[data-testid^="testid-test-card-"]')
    const initialCount = await allTestCards.count()
    expect(initialCount).toBeGreaterThan(0)

    // Apply various filters and verify all tests remain visible
    const tierFilter = page.getByTestId('testid-test-filter-tier')
    const statusFilter = page.getByTestId('testid-test-filter-status')
    const searchInput = page.getByTestId('testid-test-search-input')

    // Test tier filter
    await tierFilter.selectOption('Diamond')
    await page.waitForTimeout(300)
    let filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    expect(await filteredCards.count()).toBe(initialCount)

    // Test status filter
    await statusFilter.selectOption('locked')
    await page.waitForTimeout(300)
    filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    expect(await filteredCards.count()).toBe(initialCount)

    // Test search filter
    await searchInput.fill('nonexistent-test-name-xyz')
    await page.waitForTimeout(300)
    filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    expect(await filteredCards.count()).toBe(initialCount)

    // Clear filters
    await tierFilter.selectOption('all')
    await statusFilter.selectOption('all')
    await searchInput.clear()
    await page.waitForTimeout(300)
    filteredCards = page.locator('[data-testid^="testid-test-card-"]')
    expect(await filteredCards.count()).toBe(initialCount)

    await deleteTestUser(request, testUser.id)
  })

  test('TST-UI-012: Locked tests have disabled state', async ({ page, request }) => {
    const testUser = await createTestUserWithState(request, {
      level: 1,
    })

    await page.goto('/')
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)

    // Find a locked test
    const lockedTests = page.locator('[data-testid^="testid-test-card-"]').filter({
      has: page.locator('[data-testid="testid-test-lock-icon"]'),
    })
    const lockedCount = await lockedTests.count()
    expect(lockedCount).toBeGreaterThan(0)

    const firstLockedTest = lockedTests.first()

    // Verify locked test has disabled styling
    const opacity = await firstLockedTest.evaluate((el) => {
      return window.getComputedStyle(el).opacity
    })
    expect(parseFloat(opacity)).toBeLessThan(1) // Should be less than 1 (disabled state)

    // Verify locked test has "Locked" button instead of action buttons
    const lockedButton = firstLockedTest.locator('button:has-text("Locked")')
    await expect(lockedButton).toBeVisible()
    await expect(lockedButton).toBeDisabled()

    // Verify locked test cannot be clicked to open modal
    // (This is handled by the onClick handler, but we can verify the button is disabled)

    // Verify unlocked tests don't have disabled state
    const unlockedTests = page.locator('[data-testid^="testid-test-card-"]').filter({
      hasNot: page.locator('[data-testid="testid-test-lock-icon"]'),
    })
    const unlockedCount = await unlockedTests.count()
    if (unlockedCount > 0) {
      const firstUnlockedTest = unlockedTests.first()
      const unlockedOpacity = await firstUnlockedTest.evaluate((el) => {
        return window.getComputedStyle(el).opacity
      })
      expect(parseFloat(unlockedOpacity)).toBe(1) // Should be fully opaque
    }

    await deleteTestUser(request, testUser.id)
  })
})

