import { Page, expect } from '@playwright/test'
import type { TestUser, PracticeElements } from '../types/test-types'

/**
 * Get all practice page element references
 */
export function getPracticeElements(page: Page): PracticeElements {
  return {
    answerInput: page.getByTestId('testid-answer-input'),
    checkButton: page.getByTestId('testid-check-answer-button'),
    nextButton: page.getByTestId('testid-next-button'),
    submitButton: page.getByTestId('testid-submit-session-button'),
    questionDisplay: page.getByTestId('testid-question-display'),
    progressBar: page.getByTestId('testid-progress-bar'),
    flagButton: page.getByTestId('testid-flag-button'),
    previousButton: page.getByTestId('testid-previous-button'),
  }
}

/**
 * Navigate to practice page and wait for session to start
 */
export async function navigateToPractice(page: Page, testUser: TestUser): Promise<void> {
  await page.goto(`/practice?user=${encodeURIComponent(testUser.name)}&pin=${testUser.pin}&userId=${testUser.id}`)
  await page.waitForLoadState('networkidle')
  await page.waitForTimeout(2000)
}

/**
 * Answer the current question and wait for feedback
 */
export async function answerQuestion(
  page: Page,
  answer: string = '10',
  options?: {
    waitForLocked?: boolean
    waitForDisabled?: boolean
  }
): Promise<void> {
  const { answerInput, checkButton } = getPracticeElements(page)
  
  await answerInput.fill(answer)
  await checkButton.click()
  
  // Brief wait for React state to update (reduced from 1000ms)
  await page.waitForTimeout(300)
}

/**
 * Move to the next question, handling next button replacement by submit button
 * Returns: { moved: boolean, onLastQuestion: boolean }
 */
export async function moveToNextQuestion(page: Page): Promise<{ moved: boolean; onLastQuestion: boolean }> {
  const { nextButton, answerInput } = getPracticeElements(page)
  
  // Scroll next button into view before checking visibility
  // isVisible() requires element to be in viewport
  try {
    await nextButton.evaluate((el) => el.scrollIntoView({ behavior: 'auto', block: 'center' }))
  await page.waitForTimeout(100) // Small delay after scrolling
  } catch (error) {
    // Continue anyway - might still be able to interact with it
  }
  
  // Check if next button is visible and enabled (same approach as PRAC-006)
  // Don't check count() first - it can return 0 even if button exists but isn't visible yet
  const nextVisible = await nextButton.isVisible({ timeout: 1000 }).catch(() => false)
  const nextDisabled = await nextButton.isDisabled().catch(() => true)
  
  if (!nextVisible || nextDisabled) {
    // Next button not visible or disabled
    // Could mean: 1) on last question, 2) button replaced by submit, 3) timing issue
    // Check if submit button is visible instead (means we're on last question)
    const { submitButton } = getPracticeElements(page)
    const submitVisible = await submitButton.isVisible({ timeout: 2000 }).catch(() => false)
    if (submitVisible) {
      return { moved: false, onLastQuestion: true }
    }
    // Next button not available and submit not visible - assume on last question
    return { moved: false, onLastQuestion: true }
  }
  
  // Check if input is currently disabled (we just answered)
  const inputDisabledBefore = await answerInput.isDisabled().catch(() => false)
  
  // Click next button
  await nextButton.click()
  await page.waitForTimeout(300) // Reduced from 1000ms
  
  // Verify we actually moved to a new question by checking if input is enabled again
  // If we're on the last question, clicking next won't change anything and input stays disabled
  const inputEnabledAfter = await answerInput.isEnabled().catch(() => false)
  
  if (inputDisabledBefore && !inputEnabledAfter) {
    // Input was disabled before clicking next and is still disabled after
    // This means we're on the last question and clicking next didn't move us
    return { moved: false, onLastQuestion: true }
  }
  
  // Successfully moved to next question
  return { moved: true, onLastQuestion: false }
}

/**
 * Check if submit button is visible and enabled (all questions answered)
 */
export async function isSubmitButtonReady(page: Page): Promise<{ visible: boolean; enabled: boolean }> {
  const { submitButton } = getPracticeElements(page)
  
  // Use shorter timeout (1 second) to avoid long waits
  const visible = await submitButton.isVisible({ timeout: 1000 }).catch(() => false)
  
  // Only check disabled state if button is visible
  // If not visible, don't wait - just return false (prevents 30s timeout)
  if (!visible) {
    return { visible: false, enabled: false }
  }
  
  // Button is visible, now check if it's disabled (with timeout)
  const disabled = await submitButton.isDisabled({ timeout: 1000 }).catch(() => true)
  
  return { visible, enabled: !disabled }
}

/**
 * Complete entire practice session by answering all questions
 * Returns when submit button is ready
 */
export async function completePracticeSession(
  page: Page,
  options?: {
    maxIterations?: number
    answer?: string
  }
): Promise<void> {
  const maxIterations = options?.maxIterations || 50
  const answer = options?.answer || '10'
  const { answerInput } = getPracticeElements(page)
  
  let questionsAnswered = 0
  
  while (questionsAnswered < maxIterations) {
    // Check if input is available and not disabled
    const inputVisible = await answerInput.isVisible({ timeout: 2000 }).catch(() => false)
    const inputDisabled = await answerInput.isDisabled().catch(() => true)
    
    if (!inputVisible || inputDisabled) {
      // No more questions to answer
      break
    }
    
    // Answer the question
    await answerQuestion(page, answer, { waitForLocked: true, waitForDisabled: true })
    
    questionsAnswered++
    
    // Check if submit button is now ready (all questions answered)
    const submitStatus = await isSubmitButtonReady(page)
    
    if (submitStatus.visible && submitStatus.enabled) {
      // All questions answered, submit button is ready
      break
    }
    
    // Move to next question
    const moveResult = await moveToNextQuestion(page)
    
    if (moveResult.onLastQuestion && !moveResult.moved) {
      // We're on the last question, wait briefly for submit button to appear
      await page.waitForTimeout(200) // Reduced from 500ms
      const finalSubmitStatus = await isSubmitButtonReady(page)
      if (finalSubmitStatus.visible && finalSubmitStatus.enabled) {
        break
      }
      // If still no submit button, break to avoid infinite loop
      break
    }
    
    if (!moveResult.moved && !moveResult.onLastQuestion) {
      // Couldn't move and not on last question - something went wrong
      break
    }
    
    // After successfully moving to next question, wait for input to be enabled
    // This ensures the check at the start of the next loop iteration will pass
    if (moveResult.moved) {
      // Wait for input to become enabled (new question loaded)
      let attempts = 0
      const maxAttempts = 30 // 3 seconds with 100ms intervals
      while (attempts < maxAttempts) {
        const enabled = await answerInput.isEnabled().catch(() => false)
        if (enabled) {
          break
        }
        await page.waitForTimeout(50) // Reduced from 100ms
        attempts++
      }
    }
  }
}

/**
 * Submit practice session and wait for summary page
 * Returns API response promise
 */
export async function submitPracticeSession(page: Page): Promise<any> {
  // First, ensure submit button is ready (visible and enabled)
  // Use short timeout to fail fast if not ready
  const submitStatus = await isSubmitButtonReady(page)
  if (!submitStatus.visible || !submitStatus.enabled) {
    throw new Error(`Submit button not ready: visible=${submitStatus.visible}, enabled=${submitStatus.enabled}`)
  }
  
  const { submitButton } = getPracticeElements(page)
  
  // Set up response listener BEFORE clicking to catch the response
  // The endpoint is /api/practice/sessions/{sessionId}/complete
  const responsePromise = page.waitForResponse(
    (response) => {
      const url = response.url()
      const method = response.request().method()
      const status = response.status()
      // Match either the complete endpoint or the submissions endpoint
      // Be lenient with URL matching to catch variations
      const matchesSessions = url.includes('/api/practice/sessions')
      const matchesComplete = matchesSessions && (url.includes('/complete') || url.match(/\/sessions\/\d+\//))
      const matchesSubmissions = url.includes('/api/practice/submissions')
      // Accept POST requests with 2xx status codes
      return (matchesComplete || matchesSubmissions) && method === 'POST' && status >= 200 && status < 300
    },
    { timeout: 10000 } // 10 second timeout - should be enough for API response
  ).catch(() => {
    // If response wait fails, return null (navigation is the key indicator)
    return null
  })
  
  // Submit the session (button is confirmed ready, so use short timeout)
  await submitButton.click({ timeout: 2000 })
  
  // Wait for navigation to summary page - this is the primary indicator of success
  // If navigation succeeds, the submission worked regardless of response wait
  await page.waitForURL(/\/summary/, { timeout: 10000 })
  
  // Try to get the response, but don't block - navigation already succeeded
  // Use Promise.race to avoid waiting too long if response is slow
  return await Promise.race([
    responsePromise,
    new Promise((resolve) => setTimeout(() => resolve(null), 1000)) // Max 1s wait after navigation
  ])
}

/**
 * Get current progress percentage from progress bar
 * Returns: number (0-100)
 */
export async function getProgressPercent(page: Page): Promise<number> {
  const { progressBar } = getPracticeElements(page)
  
  const style = await progressBar.getAttribute('style')
  if (!style) return 0
  
  const match = style.match(/width:\s*(\d+(?:\.\d+)?)%/)
  return match ? parseFloat(match[1]) : 0
}

/**
 * Get current question text from question display
 * Returns: string (normalized question text)
 */
export async function getQuestionText(page: Page): Promise<string | null> {
  const { questionDisplay } = getPracticeElements(page)
  
  const questionText = await questionDisplay.textContent({ timeout: 5000 }).catch(() => null)
  
  if (!questionText || questionText.trim() === '') {
    // Try to get text from innerHTML/evaluate
    const text = await questionDisplay.evaluate((el) => {
      if (el instanceof HTMLElement) {
        return el.innerText || el.textContent || ''
      }
      return el.textContent || ''
    }).catch(() => null)
    return text
  }
  
  return questionText
}

/**
 * Wait for session to be restored from backend
 * Verifies that the session was restored (not a new session) by checking:
 * 1. Question display is visible
 * 2. If expectedQuestionIndex is provided, verifies we're on that question
 * 3. If expectedTotalQuestions is provided, verifies progress matches
 * Returns: { restored: boolean, currentQuestionIndex: number, totalQuestions: number }
 */
export async function waitForSessionRestoration(
  page: Page,
  options?: {
    expectedQuestionIndex?: number
    expectedTotalQuestions?: number
    timeout?: number
  }
): Promise<{ restored: boolean; currentQuestionIndex: number; totalQuestions: number }> {
  const timeout = options?.timeout || 10000
  
  // Wait for question display to be visible
  const { questionDisplay } = getPracticeElements(page)
  await questionDisplay.waitFor({ state: 'visible', timeout })
  
  // Wait a bit for React to update the card counter display
  await page.waitForTimeout(500)
  
  // Get the card counter display text (format: "1 / 10" or similar)
  // It's in a <p> tag with text-3xl font-bold in the PracticeHeader
  const cardCounterLocator = page.locator('text=/\\d+\\s*\\/\\s*\\d+/').first()
  await cardCounterLocator.waitFor({ state: 'visible', timeout: 5000 })
  
  const cardCounterText = await cardCounterLocator.textContent({ timeout: 5000 })
  
  // Parse progress (format: "1 / 10" or similar)
  let currentQuestionIndex = 0
  let totalQuestions = 0
  
  if (cardCounterText) {
    const match = cardCounterText.match(/(\d+)\s*\/\s*(\d+)/)
    if (match) {
      currentQuestionIndex = parseInt(match[1], 10) - 1 // Convert to 0-based index
      totalQuestions = parseInt(match[2], 10)
    }
  }
  
  // Verify we're on the expected question if provided
  if (options?.expectedQuestionIndex !== undefined) {
    if (currentQuestionIndex !== options.expectedQuestionIndex) {
      throw new Error(
        `Session restoration failed: Expected question index ${options.expectedQuestionIndex} (question ${options.expectedQuestionIndex + 1}), but got ${currentQuestionIndex} (question ${currentQuestionIndex + 1}) (display: ${cardCounterText}). This suggests a new session was created instead of restoring the incomplete session.`
      )
    }
  }
  
  // Verify total questions match if provided
  if (options?.expectedTotalQuestions !== undefined) {
    if (totalQuestions !== options.expectedTotalQuestions) {
      throw new Error(
        `Session restoration failed: Expected ${options.expectedTotalQuestions} total questions, but got ${totalQuestions} (display: ${cardCounterText})`
      )
    }
  }
  
  return {
    restored: true,
    currentQuestionIndex,
    totalQuestions,
  }
}

/**
 * Handle session restoration and answer questions to reach submit button
 * This function handles the case where session restoration fails and a new session is created.
 * It will answer all remaining questions to get to the submit button.
 * 
 * Returns: { wasRestored: boolean, answeredQuestions: number }
 */
export async function handleSessionRestorationAndAnswerToSubmit(
  page: Page,
  originalSessionId: number,
  actualSessionId: number,
  originalQuestions: any[],
  responseQuestions: any[]
): Promise<{ wasRestored: boolean; answeredQuestions: number }> {
  const wasRestored = actualSessionId === originalSessionId
  
  // Wait for session to load
  const restorationInfo = await waitForSessionRestoration(page, {
    expectedTotalQuestions: responseQuestions.length,
    timeout: 15000,
  })
  
  const { questionDisplay } = getPracticeElements(page)
  await questionDisplay.waitFor({ state: 'visible', timeout: 10000 })
  
  const isOnLastQuestion = restorationInfo.currentQuestionIndex === restorationInfo.totalQuestions - 1
  
  if (!wasRestored || !isOnLastQuestion) {
    // Session wasn't restored - we're on a new session (likely question 1)
    // We need to answer all questions to get to the submit button
    console.warn(
      `Session restoration failed. Expected session ${originalSessionId}, got ${actualSessionId}. ` +
      `Current question: ${restorationInfo.currentQuestionIndex + 1}/${restorationInfo.totalQuestions}. ` +
      `Answering all questions to reach submit button.`
    )
    
    let answeredCount = 0
    
    // Answer all remaining questions to get to the submit button
    for (let i = restorationInfo.currentQuestionIndex; i < restorationInfo.totalQuestions; i++) {
      // Get the current question's correct answer from the API response
      const currentQuestion = responseQuestions[i]
      const correctAnswer = currentQuestion?.correctAnswer || currentQuestion?.correct_answer || '10'
      
      await answerQuestion(page, String(correctAnswer))
      answeredCount++
      
      // Move to next question if not on last question
      if (i < restorationInfo.totalQuestions - 1) {
        const { nextButton } = getPracticeElements(page)
        await nextButton.click()
        await page.waitForTimeout(300)
      }
    }
    
    return { wasRestored: false, answeredQuestions: answeredCount }
  } else {
    // Session was restored - we're on the last question
    // Get the last question's correct answer from original questions
    const lastQuestion = originalQuestions[originalQuestions.length - 1]
    const lastCorrectAnswer = lastQuestion.correctAnswer || lastQuestion.correct_answer
    
    // Answer the last question via UI
    await answerQuestion(page, String(lastCorrectAnswer))
    await page.waitForTimeout(500)
    
    return { wasRestored: true, answeredQuestions: 1 }
  }
}

/**
 * Wait for navigation to summary page
 */
export async function waitForSummaryPage(page: Page): Promise<void> {
  await page.waitForURL(/\/summary/, { timeout: 10000 })
  expect(page.url()).toContain('/summary')
}

