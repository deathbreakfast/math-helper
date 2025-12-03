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
  console.log('[answerQuestion] Starting to answer question with answer:', answer)
  const { answerInput, checkButton } = getPracticeElements(page)
  
  console.log('[answerQuestion] Filling answer input')
  await answerInput.fill(answer)
  
  console.log('[answerQuestion] Clicking check button')
  await checkButton.click()
  
  console.log('[answerQuestion] Waiting for React state to update')
  // Brief wait for React state to update (reduced from 1000ms)
  await page.waitForTimeout(300)
  console.log('[answerQuestion] Finished waiting, function complete')
}

/**
 * Move to the next question, handling next button replacement by submit button
 * Returns: { moved: boolean, onLastQuestion: boolean }
 */
export async function moveToNextQuestion(page: Page): Promise<{ moved: boolean; onLastQuestion: boolean }> {
  console.log('[moveToNextQuestion] Starting')
  const { nextButton, answerInput } = getPracticeElements(page)
  
  // Scroll next button into view before checking visibility
  // isVisible() requires element to be in viewport
  console.log('[moveToNextQuestion] Scrolling next button into view')
  try {
    await nextButton.evaluate((el) => el.scrollIntoView({ behavior: 'auto', block: 'center' }))
  await page.waitForTimeout(100) // Small delay after scrolling
  console.log('[moveToNextQuestion] Finished scrolling')
  } catch (error) {
    console.log('[moveToNextQuestion] Scroll failed:', error)
    // Continue anyway - might still be able to interact with it
  }
  
  // Check if next button is visible and enabled (same approach as PRAC-006)
  // Don't check count() first - it can return 0 even if button exists but isn't visible yet
  const nextVisible = await nextButton.isVisible({ timeout: 1000 }).catch(() => false)
  const nextDisabled = await nextButton.isDisabled().catch(() => true)
  console.log('[moveToNextQuestion] Next button visible:', nextVisible, 'disabled:', nextDisabled)
  
  if (!nextVisible || nextDisabled) {
    console.log('[moveToNextQuestion] Next button not available')
    // Next button not visible or disabled
    // Could mean: 1) on last question, 2) button replaced by submit, 3) timing issue
    // Check if submit button is visible instead (means we're on last question)
    const { submitButton } = getPracticeElements(page)
    const submitVisible = await submitButton.isVisible({ timeout: 2000 }).catch(() => false)
    if (submitVisible) {
      console.log('[moveToNextQuestion] Submit button visible instead - on last question')
      return { moved: false, onLastQuestion: true }
    }
    // Next button not available and submit not visible - assume on last question
    console.log('[moveToNextQuestion] Next button not available and submit not visible - assuming last question')
    return { moved: false, onLastQuestion: true }
  }
  
  // Check if input is currently disabled (we just answered)
  const inputDisabledBefore = await answerInput.isDisabled().catch(() => false)
  console.log('[moveToNextQuestion] Input disabled before click:', inputDisabledBefore)
  
  // Click next button
  console.log('[moveToNextQuestion] Clicking next button')
  await nextButton.click()
  await page.waitForTimeout(300) // Reduced from 1000ms
  
  // Verify we actually moved to a new question by checking if input is enabled again
  // If we're on the last question, clicking next won't change anything and input stays disabled
  const inputEnabledAfter = await answerInput.isEnabled().catch(() => false)
  console.log('[moveToNextQuestion] Input enabled after click:', inputEnabledAfter)
  
  if (inputDisabledBefore && !inputEnabledAfter) {
    console.log('[moveToNextQuestion] Input still disabled - on last question')
    // Input was disabled before clicking next and is still disabled after
    // This means we're on the last question and clicking next didn't move us
    return { moved: false, onLastQuestion: true }
  }
  
  console.log('[moveToNextQuestion] Successfully moved to next question')
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
  console.log('[completePracticeSession] Starting')
  const maxIterations = options?.maxIterations || 50
  const answer = options?.answer || '10'
  const { answerInput } = getPracticeElements(page)
  
  let questionsAnswered = 0
  
  while (questionsAnswered < maxIterations) {
    console.log(`[completePracticeSession] Loop iteration ${questionsAnswered + 1}/${maxIterations}`)
    
    // Check if input is available and not disabled
    console.log('[completePracticeSession] Checking if input is available')
    const inputVisible = await answerInput.isVisible({ timeout: 2000 }).catch(() => false)
    const inputDisabled = await answerInput.isDisabled().catch(() => true)
    console.log('[completePracticeSession] Input visible:', inputVisible, 'disabled:', inputDisabled)
    
    if (!inputVisible || inputDisabled) {
      console.log('[completePracticeSession] Input not available - breaking')
      // No more questions to answer
      break
    }
    
    // Answer the question
    console.log(`[completePracticeSession] Answering question ${questionsAnswered + 1}`)
    await answerQuestion(page, answer, { waitForLocked: true, waitForDisabled: true })
    console.log(`[completePracticeSession] Finished answering question ${questionsAnswered + 1}`)
    
    questionsAnswered++
    console.log(`[completePracticeSession] Questions answered so far: ${questionsAnswered}`)
    
    // Check if submit button is now ready (all questions answered)
    console.log('[completePracticeSession] Checking submit button status')
    const submitStatus = await isSubmitButtonReady(page)
    console.log('[completePracticeSession] Submit button visible:', submitStatus.visible, 'enabled:', submitStatus.enabled)
    
    if (submitStatus.visible && submitStatus.enabled) {
      console.log('[completePracticeSession] All questions answered, submit button ready - breaking')
      // All questions answered, submit button is ready
      break
    }
    
    // Move to next question
    console.log('[completePracticeSession] Moving to next question')
    const moveResult = await moveToNextQuestion(page)
    console.log('[completePracticeSession] Move result:', moveResult)
    
    if (moveResult.onLastQuestion && !moveResult.moved) {
      console.log('[completePracticeSession] On last question, waiting for submit button')
      // We're on the last question, wait briefly for submit button to appear
      await page.waitForTimeout(200) // Reduced from 500ms
      const finalSubmitStatus = await isSubmitButtonReady(page)
      if (finalSubmitStatus.visible && finalSubmitStatus.enabled) {
        console.log('[completePracticeSession] Submit button appeared - breaking')
        break
      }
      console.log('[completePracticeSession] Submit button did not appear - breaking')
      // If still no submit button, break to avoid infinite loop
      break
    }
    
    if (!moveResult.moved && !moveResult.onLastQuestion) {
      console.log('[completePracticeSession] Could not move and not on last question - breaking')
      // Couldn't move and not on last question - something went wrong
      break
    }
    
    // After successfully moving to next question, wait for input to be enabled
    // This ensures the check at the start of the next loop iteration will pass
    if (moveResult.moved) {
      console.log('[completePracticeSession] Waiting for input to become enabled')
      // Wait for input to become enabled (new question loaded)
      let attempts = 0
      const maxAttempts = 30 // 3 seconds with 100ms intervals
      while (attempts < maxAttempts) {
        const enabled = await answerInput.isEnabled().catch(() => false)
        if (enabled) {
          console.log('[completePracticeSession] Input is now enabled')
          break
        }
        await page.waitForTimeout(50) // Reduced from 100ms
        attempts++
      }
      if (attempts >= maxAttempts) {
        console.log('[completePracticeSession] Input did not become enabled after waiting')
      }
    }
  }
  
  console.log('[completePracticeSession] Finished, total questions answered:', questionsAnswered)
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
 * Wait for navigation to summary page
 */
export async function waitForSummaryPage(page: Page): Promise<void> {
  await page.waitForURL(/\/summary/, { timeout: 10000 })
  expect(page.url()).toContain('/summary')
}

