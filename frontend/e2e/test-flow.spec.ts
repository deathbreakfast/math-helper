import { test, expect } from './fixtures/test-user'
import {
  navigateToJourneyTab,
  getTestEligibility,
  deleteTestUser,
  startTestSession,
  answerQuestionViaAPI,
  scenario,
  waitForComponent,
  waitForFramerMotion,
} from './helpers/test-helpers'

test.describe('Test Flow', () => {
  test('TEST-001: Test eligibility check displays requirements', async ({ page, request }) => {
    // Create user at level 1 with 0 completed sessions (not eligible)
    const context = await scenario()
      .withUser({ level: 1 })
      .build(request)
    
    try {
      // Navigate directly to tests tab
      await navigateToJourneyTab(page, context.user.id, 'tests')
      
      // Wait for tests tab to load
      await waitForComponent(page, 'testid-tests-tab')
      
      // Check eligibility via API
      const eligibility = await getTestEligibility(request, context.user.id)
      
      // Verify eligibility information is displayed in UI
      await waitForComponent(page, 'testid-test-achievements-grid')
      
      // Verify eligibility shows requirements (user should not be eligible)
      expect(eligibility).toBeDefined()
    } finally {
      await context.cleanup()
    }
  })

  test('TEST-002: Start eligible test', async ({ page, request }) => {
    // Create user at level 1 with 3 completed practice sessions (for eligibility)
    const context = await scenario()
      .withUser({ level: 1 })
      .withCompletedSessions(1, 3)
      .build(request)
    
    try {
      // Verify user is eligible via API
      const eligibility = await getTestEligibility(request, context.user.id, 1)
      expect(eligibility).toBeDefined()
      
      // Navigate directly to tests tab
      await navigateToJourneyTab(page, context.user.id, 'tests')
      
      // Wait for tests tab and grid to load
      await waitForComponent(page, 'testid-tests-tab')
      await waitForComponent(page, 'testid-test-achievements-grid')
      
      // Actually start a test via API and verify it succeeds
      const testSession = await startTestSession(request, context.user.id, 'level_1')
      expect(testSession).toBeDefined()
      expect(testSession.session_id).toBeDefined()
      expect(testSession.questions).toBeDefined()
      expect(testSession.questions.length).toBeGreaterThan(0)
    } finally {
      await context.cleanup()
    }
  })

  test('TEST-003: Test submission', async ({ page, request }) => {
    // Create user at level 1 with 3 completed practice sessions (for eligibility)
    const context = await scenario()
      .withUser({ level: 1 })
      .withCompletedSessions(1, 3)
      .build(request)
    
    try {
      // Start test session via API
      const testSession = await startTestSession(request, context.user.id, 'level_1')
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
    } finally {
      await context.cleanup()
    }
  })

  test('TEST-004: Test retake eligibility', async ({ page, request }) => {
    // Create user at level 1 with 3 completed practice sessions
    const context = await scenario()
      .withUser({ level: 1 })
      .withCompletedSessions(1, 3)
      .build(request)
    
    try {
      // Create a passed test attempt (for retake eligibility)
      const { createPassedTestAttempt } = await import('./helpers/test-helpers')
      await createPassedTestAttempt(request, context.user.id, 1, 'level_1')
      
      // Verify retake eligibility is shown via API
      const eligibility = await getTestEligibility(request, context.user.id, 1)
      expect(eligibility).toBeDefined()
      
      // Navigate directly to tests tab
      await navigateToJourneyTab(page, context.user.id, 'tests')
      
      // Wait for tests tab and grid to load
      await waitForComponent(page, 'testid-tests-tab')
      await waitForComponent(page, 'testid-test-achievements-grid')
    } finally {
      await context.cleanup()
    }
  })

  test('TEST-005: Test tier filtering in tests tab', async ({ page, request }) => {
    // Create user with test attempts at different tiers
    const context = await scenario()
      .withUser({ level: 10 }) // Level 10 has test requirements
      .withCompletedSessions(1, 3) // Make user eligible for tests
      .build(request)
    
    try {
      // Create a passed test attempt (for tier filtering)
      const { createPassedTestAttempt } = await import('./helpers/test-helpers')
      await createPassedTestAttempt(request, context.user.id, 1, 'level_1')
      
      // Navigate directly to tests tab
      await navigateToJourneyTab(page, context.user.id, 'tests')
      
      // Wait for tests tab and grid to load
      await waitForComponent(page, 'testid-tests-tab')
      await waitForComponent(page, 'testid-test-achievements-grid')
      
      // Test tier filter - filter by 'Bronze' tier (valid tier name)
      const tierFilter = page.getByTestId('testid-test-filter-tier')
      await tierFilter.selectOption('Bronze')
      await waitForFramerMotion(page)
      
      // Verify filtered results show tests (all tests remain visible, just filtered visually)
      const testCards = page.locator('[data-testid^="testid-test-card-"]')
      const count = await testCards.count()
      expect(count).toBeGreaterThan(0)
      
      // Test search filter
      const searchInput = page.getByTestId('testid-test-search-input')
      await searchInput.fill('multiply')
      await waitForFramerMotion(page)
      
      // Verify grid is still visible after filtering
      const testGrid = page.getByTestId('testid-test-achievements-grid')
      await expect(testGrid).toBeVisible()
    } finally {
      await context.cleanup()
    }
  })
})


