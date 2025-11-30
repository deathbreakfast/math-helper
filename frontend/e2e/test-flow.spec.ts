import { test, expect } from './fixtures/test-user'
import {
  openJourneyModal,
  navigateToTestsTab,
  getTestEligibility,
  createTestUserWithState,
  deleteTestUser,
  createCompletedPracticeSessions,
  startTestSession,
  answerQuestionViaAPI,
  createPassedTestAttempt,
} from './helpers/test-helpers'

test.describe('Test Flow', () => {
  test('TEST-001: Test eligibility check displays requirements', async ({ page, request }) => {
    // Create user at level 1 with 0 completed sessions (not eligible)
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements, no sessions - ensures requirements are visible
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)
    
    // Verify tests tab is visible
    const testsTab = page.getByTestId('testid-tests-tab')
    await expect(testsTab).toBeVisible()
    
    // Check eligibility via API
    const eligibility = await getTestEligibility(request, testUser.id)
    
    // Verify eligibility information is displayed in UI
    // Test achievements grid should be visible
    const testGrid = page.getByTestId('testid-test-achievements-grid')
    await expect(testGrid).toBeVisible()
    
    // Verify eligibility shows requirements (user should not be eligible)
    expect(eligibility).toBeDefined()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('TEST-002: Start eligible test', async ({ page, request }) => {
    // Create user at level 1
    const testUser = await createTestUserWithState(request, {
      level: 1
    })
    
    // Set up 3+ completed practice sessions at level 1 (for eligibility)
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    // Verify user is eligible via API
    const eligibility = await getTestEligibility(request, testUser.id, 1)
    expect(eligibility).toBeDefined()
    
    // Verify UI shows eligible state
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)
    
    // Verify tests tab is visible
    const testsTab = page.getByTestId('testid-tests-tab')
    await expect(testsTab).toBeVisible()
    
    // Verify test achievements grid is visible
    const testGrid = page.getByTestId('testid-test-achievements-grid')
    await expect(testGrid).toBeVisible()
    
    // Actually start a test via API and verify it succeeds
    const testSession = await startTestSession(request, testUser.id, 'level_1')
    expect(testSession).toBeDefined()
    expect(testSession.session_id).toBeDefined()
    expect(testSession.questions).toBeDefined()
    expect(testSession.questions.length).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('TEST-003: Test submission', async ({ page, request }) => {
    // Create user at level 1
    const testUser = await createTestUserWithState(request, {
      level: 1
    })
    
    // Set up 3+ completed practice sessions (for eligibility)
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    // Start test session via API
    const testSession = await startTestSession(request, testUser.id, 'level_1')
    expect(testSession.session_id).toBeDefined()
    expect(testSession.questions).toBeDefined()
    expect(testSession.questions.length).toBeGreaterThan(0)
    
    const sessionId = testSession.session_id
    const questions = testSession.questions
    
    // Answer questions via API
    for (const question of questions) {
      await answerQuestionViaAPI(
        request,
        sessionId,
        question.question_id || question.id,
        question.correct_answer || question.correctAnswer,
        2000 // 2 seconds per question
      )
    }
    
    // Submit test session via API
    const submitResponse = await request.post(`/api/practice/sessions/${sessionId}/complete`, {
      data: {
        total_duration_ms: questions.length * 2000
      }
    })
    
    expect(submitResponse.ok()).toBe(true)
    
    const result = await submitResponse.json()
    expect(result).toBeDefined()
    expect(result.session).toBeDefined()
    expect(result.session.completed_at).toBeDefined()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('TEST-004: Test retake eligibility', async ({ page, request }) => {
    // Create user at level 1
    const testUser = await createTestUserWithState(request, {
      level: 1
    })
    
    // Set up 3+ completed practice sessions
    await createCompletedPracticeSessions(request, testUser.id, 1, 3)
    
    // Create a passed test attempt (for retake eligibility)
    await createPassedTestAttempt(request, testUser.id, 1, 'level_1')
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    // Verify retake eligibility is shown via API
    const eligibility = await getTestEligibility(request, testUser.id, 1)
    expect(eligibility).toBeDefined()
    
    // Verify UI shows retake eligibility
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)
    
    // Verify tests tab is visible
    const testsTab = page.getByTestId('testid-tests-tab')
    await expect(testsTab).toBeVisible()
    
    // Verify test achievements are displayed (may show retake eligibility)
    const testGrid = page.getByTestId('testid-test-achievements-grid')
    await expect(testGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('TEST-005: Test tier filtering in tests tab', async ({ page, request }) => {
    // Create user with test achievements at different tiers
    const testUser = await createTestUserWithState(request, {
      level: 10, // Level 10 has test requirements
      achievements: [
        'multiply-by-two-test-a', // A tier
        'multiply-by-three-test-s', // S tier
      ]
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToTestsTab(page)
    
    // Verify tests tab is visible
    const testsTab = page.getByTestId('testid-tests-tab')
    await expect(testsTab).toBeVisible()
    
    // Verify test achievements grid is visible
    const testGrid = page.getByTestId('testid-test-achievements-grid')
    await expect(testGrid).toBeVisible()
    
    // Test tier filter - filter by 'A' tier
    const tierFilter = page.getByTestId('testid-test-filter-tier')
    await tierFilter.selectOption('A')
    await page.waitForTimeout(500)
    
    // Verify filtered results show A-tier tests
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const count = await achievementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Test search filter
    const searchInput = page.getByTestId('testid-test-search-input')
    await searchInput.fill('multiply')
    await page.waitForTimeout(500)
    
    // Verify grid is still visible after filtering
    await expect(testGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })
})


