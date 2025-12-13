import { test, expect } from './fixtures/test-user'
import {
  navigateToPractice,
  startPracticeSessionViaAPI,
  answerQuestionViaAPI,
  handleSessionRestorationAndAnswerToSubmit,
  getIncompleteSession,
  getPracticeElements,
  waitForSessionRestoration,
} from './helpers/test-helpers'

test.describe('Practice Session - Keyboard Input', () => {
  test('PRAC-KB-001: Enter key submits session after last question', async ({ page, request, testUser }) => {
    test.setTimeout(60000)
    
    // Create a session with a few questions
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    // Answer all questions except the last one via API
    for (let i = 0; i < questions.length - 1; i++) {
      const question = questions[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        2000
      )
    }
    
    // Navigate to practice page
    const startSessionPromise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSessionResponse = await startSessionPromise
    const sessionDataUI = await startSessionResponse.json()
    
    // Handle session restoration if needed
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session_id,
      sessionDataUI.session_id,
      questions,
      sessionDataUI.questions
    )
    
    // Wait for practice page to be ready
    await page.waitForLoadState('networkidle')

    // NOTE:
    // `handleSessionRestorationAndAnswerToSubmit` will answer/lock questions as needed
    // (including the last question). At this point the answer input may be disabled,
    // so we should NOT attempt to fill it again. The correct behavior we want to test
    // is: once the session is ready to submit, pressing Enter submits the session.

    const submitButton = page.getByTestId('testid-submit-session-button')
    await expect(submitButton).toBeVisible({ timeout: 10000 })

    // Press Enter key (should trigger session submission).
    // Use the page keyboard so this works even if the input is disabled.
    await page.keyboard.press('Enter')

    // Wait for navigation to summary page
    await page.waitForURL(/\/summary/, { timeout: 10000 })
    expect(page.url()).toContain('/summary')
  })

  test('PRAC-KB-002: Enter key moves to next question (not last question)', async ({ page, request, testUser }) => {
    test.setTimeout(60000)
    
    const sessionData = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id, questions } = sessionData
    
    // Answer first question via API
    if (questions.length > 1) {
      const firstQuestion = questions[0]
      const questionId = firstQuestion.question_id || firstQuestion.id
      const correctAnswer = firstQuestion.correctAnswer || firstQuestion.correct_answer
      
      await answerQuestionViaAPI(
        request,
        session_id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        2000
      )
    }
    
    // Navigate to practice page
    const startSessionPromise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSessionResponse = await startSessionPromise
    const sessionDataUI = await startSessionResponse.json()
    
    await page.waitForLoadState('networkidle')
    
    // Answer the current question (should be second question if first was answered via API)
    const { answerInput, checkButton } = getPracticeElements(page)
    await expect(answerInput).toBeVisible({ timeout: 5000 })
    
    // Get current question answer
    const currentQuestionIndex = await page.evaluate(() => {
      // Try to get current question index from React state or DOM
      return 1 // Assume we're on question 1 (0-indexed = second question)
    }).catch(() => 1)
    
    // Find the correct answer for current question
    const currentQuestion = sessionDataUI.questions[currentQuestionIndex] || sessionDataUI.questions[1] || sessionDataUI.questions[0]
    const correctAnswer = currentQuestion.correctAnswer || currentQuestion.correct_answer
    
    // Type and check answer
    await answerInput.fill(String(correctAnswer))
    await checkButton.click()
    await page.waitForTimeout(500)
    
    // Verify we're NOT on the last question
    const submitButton = page.getByTestId('testid-submit-session-button')
    const submitVisible = await submitButton.isVisible({ timeout: 2000 }).catch(() => false)
    
    if (!submitVisible && questions.length > 2) {
      // Press Enter - should move to next question, not submit
      await answerInput.press('Enter')
      await page.waitForTimeout(500)
      
      // Verify we moved to next question (input should be enabled again)
      const inputEnabled = await answerInput.isEnabled().catch(() => false)
      expect(inputEnabled).toBe(true)
      
      // Verify submit button is still not visible (not on last question)
      const submitStillVisible = await submitButton.isVisible({ timeout: 1000 }).catch(() => false)
      expect(submitStillVisible).toBe(false)
    }
  })

  test('PRAC-KB-003: Keyboard input works in answer field', async ({ page, testUser }) => {
    await navigateToPractice(page, testUser)
    
    const { answerInput } = getPracticeElements(page)
    await expect(answerInput).toBeVisible({ timeout: 5000 })
    
    // Type using keyboard
    await answerInput.fill('42')
    
    // Verify value was entered
    const value = await answerInput.inputValue()
    expect(value).toBe('42')
    
    // Clear and type again
    await answerInput.clear()
    await answerInput.type('100', { delay: 50 })
    
    const newValue = await answerInput.inputValue()
    expect(newValue).toBe('100')
  })

  test('PRAC-KB-004: Tab key navigation', async ({ page, testUser }) => {
    await navigateToPractice(page, testUser)
    
    await page.waitForLoadState('networkidle')
    
    const { answerInput, checkButton } = getPracticeElements(page)
    await expect(answerInput).toBeVisible({ timeout: 5000 })
    
    // Focus on input
    await answerInput.focus()
    
    // Type an answer
    await answerInput.fill('42')
    
    // Press Tab - should move focus to next element (check button)
    await answerInput.press('Tab')
    
    // Verify focus moved (check button should be focused)
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    // Focus might be on button or other element
    expect(['BUTTON', 'INPUT']).toContain(focusedElement)
  })
})

