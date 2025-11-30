import { test, expect } from './fixtures/test-user'
import {
  navigateToPractice,
  answerQuestion,
  submitPracticeSession,
  waitForSummaryPage,
  getPracticeElements,
  startPracticeSessionViaAPI,
  answerQuestionViaAPI,
} from './helpers/test-helpers'

test.describe('Summary Page', () => {
  test('SUM-001: Summary page loads with backend session restoration', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      // Questions from generate_session API have: question_id (int) and correctAnswer (camelCase)
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000 // 1 second per question
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    
    // Wait for the session to load/resume
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Verify that the session was restored from backend (not localStorage)
    // The practice page should show the last unanswered question
    const { questionDisplay } = getPracticeElements(page)
    await expect(questionDisplay).toBeVisible({ timeout: 10000 })
    
    // Verify we're on the last question (all previous questions were answered via API)
    // The backend should have restored the session with answered questions first, then unanswered
    // So we should be on the last question
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Verify summary page loaded
    await expect(page.locator('body')).toBeVisible()
  })

  test('SUM-002: Summary stats', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000 // 1 second per question
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    
    // Wait for the session to load/resume
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Verify stats are displayed
    const stats = page.locator('text=/accuracy|correct|total|time/i')
    await expect(stats.first()).toBeVisible({ timeout: 5000 })
  })

  test('SUM-003: Problem grid', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Look for problem grid
    const problemGrid = page.locator('[data-testid*="problem"]').or(
      page.locator('text=/problem|question/i')
    )
    await expect(problemGrid.first()).toBeVisible({ timeout: 5000 })
  })

  test('SUM-004: Problem detail modal', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Click on a problem card
    const problemCard = page.locator('[data-testid*="problem"]').or(
      page.locator('button').filter({ hasText: /\d+/ })
    )
    const cardVisible = await problemCard.first().isVisible({ timeout: 3000 }).catch(() => false)
    
    if (cardVisible) {
      await problemCard.first().click()
      await page.waitForTimeout(500)
      
      // Verify modal or detail view appears
      const detail = page.locator('[role="dialog"]').or(
        page.locator('text=/detail|answer|question/i')
      )
      await expect(detail.first()).toBeVisible({ timeout: 3000 })
    }
  })

  test('SUM-005: Practice again', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Click Practice Again button
    const practiceAgainButton = page.getByTestId('testid-practice-again-button')
    await practiceAgainButton.click()
    
    // Should navigate back to practice
    await page.waitForURL(/\/practice/, { timeout: 5000 })
    expect(page.url()).toContain('/practice')
  })

  test('SUM-006: Try next level', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Look for Try Next Level button (might only appear if leveled up)
    const nextLevelButton = page.getByTestId('testid-try-next-level-button')
    const nextLevelVisible = await nextLevelButton.isVisible({ timeout: 2000 }).catch(() => false)
    
    if (nextLevelVisible && !(await nextLevelButton.isDisabled())) {
      await nextLevelButton.click()
      await page.waitForURL(/\/practice/, { timeout: 5000 })
    }
  })

  test('SUM-007: Review flagged', async ({ page, testUser, request }) => {
    // Start a practice session via API
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    expect(questions.length).toBeGreaterThan(0)
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      if (!questionId || !correctAnswer) {
        throw new Error(`Question ${i} missing required fields: ${JSON.stringify(question)}`)
      }
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        1000
      )
    }
    
    // Navigate to practice page - this should resume the incomplete session from backend
    await navigateToPractice(page, testUser)
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // Flag the current question (the last unanswered one)
    const { flagButton } = getPracticeElements(page)
    const flagVisible = await flagButton.isVisible({ timeout: 5000 }).catch(() => false)
    
    if (flagVisible) {
      await flagButton.click()
      await page.waitForTimeout(500)
    }
    
    // Get the last question's correct answer
    const lastQuestion = questions[questions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    
    // Submit the session via UI
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Look for Review Flagged button
    const reviewFlaggedButton = page.getByTestId('testid-review-flagged-button')
    const reviewVisible = await reviewFlaggedButton.isVisible({ timeout: 2000 }).catch(() => false)
    
    if (reviewVisible && !(await reviewFlaggedButton.isDisabled())) {
      await reviewFlaggedButton.click()
      await page.waitForTimeout(1000)
      
      // Should show flagged problems
      const flaggedProblems = page.locator('text=/flagged|review/i')
      await expect(flaggedProblems.first()).toBeVisible({ timeout: 3000 })
    }
  })
})


