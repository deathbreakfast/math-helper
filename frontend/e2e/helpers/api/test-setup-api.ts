import { APIRequestContext } from '@playwright/test'
import { getUser } from './user-api'

/**
 * Set user level directly via test setup endpoint (DEV ONLY)
 * Bypasses achievement requirements for test setup purposes
 */
export async function setUserLevelDirectly(
  request: APIRequestContext,
  userId: number,
  level: number
): Promise<void> {
  const response = await request.post(`/api/users/${userId}/test-setup`, {
    data: {
      level: level
    }
  })
  
  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to set user level: ${JSON.stringify(error)}`)
  }
}

/**
 * Award achievements directly via test setup endpoint (DEV ONLY)
 * Bypasses requirement checks for test setup purposes
 * 
 * Supports both string array and object array formats:
 * - String format: ["first-steps", "first-victory"]
 * - Object format: [{"code": "accuracy-ace-gold", "metadata": {"test_type": "addition-1digit"}}]
 */
export async function awardAchievements(
  request: APIRequestContext,
  userId: number,
  achievements: string[] | Array<{ code: string; metadata?: Record<string, any> }>
): Promise<void> {
  const response = await request.post(`/api/users/${userId}/test-setup`, {
    data: {
      achievements: achievements
    }
  })
  
  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to award achievements: ${JSON.stringify(error)}`)
  }
}

/**
 * Set up user with level and achievements in one call (DEV ONLY)
 * 
 * Achievements can be:
 * - String array: ["first-steps", "first-victory"]
 * - Object array: [{"code": "accuracy-ace-gold", "metadata": {"test_type": "addition-1digit"}}]
 */
export async function setupTestUserState(
  request: APIRequestContext,
  userId: number,
  options: {
    level?: number
    achievements?: string[] | Array<{ code: string; metadata?: Record<string, any> }>
  }
): Promise<void> {
  const debug = process.env.E2E_DEBUG_API === '1'
  if (debug) {
    // eslint-disable-next-line no-console
    console.log('[e2e api] POST /api/users/:id/test-setup payload:', { userId, ...options })
  }

  const response = await request.post(`/api/users/${userId}/test-setup`, {
    data: {
      level: options.level,
      achievements: options.achievements || []
    }
  })
  
  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to setup test user state: ${JSON.stringify(error)}`)
  }

  if (debug) {
    // eslint-disable-next-line no-console
    console.log('[e2e api] POST /api/users/:id/test-setup status:', response.status(), response.statusText())
    try {
      const contentType = response.headers()['content-type'] || ''
      if (contentType.includes('application/json')) {
        const body = await response.json()
        // eslint-disable-next-line no-console
        console.log('[e2e api] POST /api/users/:id/test-setup response json:', body)
      } else {
        const text = await response.text()
        // eslint-disable-next-line no-console
        console.log('[e2e api] POST /api/users/:id/test-setup response text (truncated):', text.substring(0, 300))
      }
    } catch (e) {
      // eslint-disable-next-line no-console
      console.log('[e2e api] POST /api/users/:id/test-setup response read failed:', e)
    }
  }
}

/**
 * Create a test user and set up their state (level, achievements) in one call
 * Returns the created user with the requested state
 * 
 * Achievements can be:
 * - String array: ["first-steps", "first-victory"]
 * - Object array: [{"code": "accuracy-ace-gold", "metadata": {"test_type": "addition-1digit"}}]
 */
export async function createTestUserWithState(
  request: APIRequestContext,
  options: {
    name?: string
    avatar?: string
    pin?: string
    level?: number
    achievements?: string[] | Array<{ code: string; metadata?: Record<string, any> }>
  }
): Promise<import('../types/test-types').TestUser> {
  const { createTestUser } = await import('./user-api')
  
  // Create user first
  const user = await createTestUser(request, {
    name: options.name,
    avatar: options.avatar,
    pin: options.pin
  })
  
  // Set up state if provided
  if (options.level !== undefined || options.achievements) {
    await setupTestUserState(request, user.id, {
      level: options.level,
      achievements: options.achievements
    })
    
    // Refresh user to get updated level
    const updatedUser = await getUser(request, user.id)
    return updatedUser || user
  }
  
  return user
}

/**
 * Set up user with all required achievements for a target level
 * Useful for testing level up UI when requirements are met
 */
export async function setupUserForLevelUp(
  request: APIRequestContext,
  userId: number,
  targetLevel: number
): Promise<void> {
  // Get level requirements from config (may need API endpoint for this)
  // For now, manually specify known requirements
  // This is a placeholder - actual implementation depends on how we access level requirements
  
  // For now, use direct achievement codes based on known requirements
  const levelRequirements: Record<number, string[]> = {
    2: ['addition-basics'],
    3: ['level-2-mastery'],
    4: ['subtraction-basics'],
    5: ['perfect-sessions-2', 'basic-math-test', 'level-5-mastery'],
    // Add more as needed for testing
  }
  
  const achievements = levelRequirements[targetLevel] || []
  if (achievements.length > 0) {
    await awardAchievements(request, userId, achievements)
  }
  
  // Set user to targetLevel - 1 so they're ready to level up
  await setUserLevelDirectly(request, userId, targetLevel - 1)
}

/**
 * Get level up eligibility via API
 */
export async function getLevelUpEligibility(request: APIRequestContext, userId: number): Promise<any> {
  const response = await request.get(`/api/users/${userId}/level-up/eligibility`)
  if (!response.ok()) {
    throw new Error(`Failed to get level up eligibility: ${response.status()}`)
  }
  return await response.json()
}

/**
 * Get test eligibility via API
 */
export async function getTestEligibility(request: APIRequestContext, userId: number, level?: number): Promise<any> {
  const url = level 
    ? `/api/practice/test-eligibility?user_id=${userId}&level=${level}`
    : `/api/practice/test-eligibility?user_id=${userId}`
  const response = await request.get(url)
  if (!response.ok()) {
    throw new Error(`Failed to get test eligibility: ${response.status()}`)
  }
  return await response.json()
}

/**
 * Start test session via API
 */
export async function startTestSession(
  request: APIRequestContext,
  userId: number,
  testType: string,
  level?: number
): Promise<any> {
  // Backend only records a TestAttempt on completion if session.level is set.
  // If caller didn't provide it, fall back to the user's current level.
  let effectiveLevel = level
  if (effectiveLevel === undefined) {
    const user = await getUser(request, userId)
    effectiveLevel = user?.level
  }

  const response = await request.post('/api/practice/sessions/start', {
    data: {
      user_id: userId,
      is_test: true,
      test_type: testType,
      mode: 'standard',
      level: effectiveLevel,
    }
  })
  if (!response.ok()) {
    throw new Error(`Failed to start test: ${response.status()}`)
  }
  return await response.json()
}

/**
 * Create completed practice sessions for test eligibility
 * Creates count number of completed practice sessions at the specified level
 * Includes error handling, retries, and logging to prevent request context disposal issues
 */
export async function createCompletedPracticeSessions(
  request: APIRequestContext,
  userId: number,
  level: number,
  count: number
): Promise<void> {
  const { startPracticeSessionViaAPI, answerQuestionViaAPI } = await import('./practice-api')
  
  for (let i = 0; i < count; i++) {
    try {
      // Start a practice session
      const sessionData = await startPracticeSessionViaAPI(request, userId, {
        level: level,
        mode: 'standard'
      })
      
      const sessionId = sessionData.session_id
      const questions = sessionData.questions || []
      
      // Answer all questions correctly to complete the session
      for (let qIdx = 0; qIdx < questions.length; qIdx++) {
        const question = questions[qIdx]
        try {
          await answerQuestionViaAPI(
            request,
            sessionId,
            question.question_id || question.id,
            question.correct_answer || question.correctAnswer,
            1000 // 1 second per question
          )
        } catch (error) {
          console.error(`[createCompletedPracticeSessions] Error answering question ${qIdx + 1}/${questions.length} in session ${i + 1}:`, error)
          throw error
        }
      }
      
      // Complete the session with retry logic
      let completeResponse
      let retries = 3
      let lastError: Error | null = null
      
      while (retries > 0) {
        try {
          completeResponse = await request.post(`/api/practice/sessions/${sessionId}/complete`, {
            data: {
              total_duration_ms: questions.length * 1000
            },
            timeout: 30000 // 30 second timeout per request
          })
          
          if (completeResponse.ok()) {
            break
          } else {
            const errorText = await completeResponse.text().catch(() => 'Unknown error')
            throw new Error(`Failed to complete practice session: ${completeResponse.status()} - ${errorText}`)
          }
        } catch (error: any) {
          lastError = error
          retries--
          if (retries > 0) {
            const waitTime = 1000 * (4 - retries) // Exponential backoff: 1s, 2s, 3s
            console.warn(`[createCompletedPracticeSessions] Session ${i + 1} completion failed, retrying in ${waitTime}ms (${retries} retries left):`, error.message)
            await new Promise(resolve => setTimeout(resolve, waitTime))
          }
        }
      }
      
      if (!completeResponse || !completeResponse.ok()) {
        throw lastError || new Error(`Failed to complete practice session ${i + 1} after retries`)
      }
      
      // Small delay between sessions to avoid overwhelming the API
      if (i < count - 1) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    } catch (error: any) {
      const errorMessage = error?.message || String(error)
      console.error(`[createCompletedPracticeSessions] Failed to create session ${i + 1}/${count}:`, errorMessage)
      
      // Check if it's a request context disposal error
      if (errorMessage.includes('Request context disposed') || errorMessage.includes('disposed')) {
        throw new Error(`Request context was disposed while creating session ${i + 1}/${count}. This may indicate a timeout issue. Original error: ${errorMessage}`)
      }
      
      throw error
    }
  }
}

/**
 * Create a passed test attempt for retake eligibility
 * Creates a completed test session with passing score (≥80%)
 * Includes error handling and logging to prevent request context disposal issues
 */
export async function createPassedTestAttempt(
  request: APIRequestContext,
  userId: number,
  level: number,
  testType: string
): Promise<void> {
  const { answerQuestionViaAPI } = await import('./practice-api')
  
  try {
    // Start test session
    // IMPORTANT: backend only records a TestAttempt on completion if session.level is set.
    // Pass level explicitly so the attempt shows up in /api/tests/* endpoints used by the UI.
    const sessionData = await request.post('/api/practice/sessions/start', {
      data: {
        user_id: userId,
        is_test: true,
        test_type: testType,
        mode: 'standard',
        level,
      },
      timeout: 30000,
    })
    if (!sessionData.ok()) {
      const errorText = await sessionData.text().catch(() => 'Unknown error')
      throw new Error(`Failed to start test: ${sessionData.status()} - ${errorText}`)
    }
    const sessionJson = await sessionData.json()
    const sessionId = sessionJson.session_id
    const questions = sessionJson.questions || []
    
    // Answer questions to achieve passing score (≥80%)
    // Calculate how many need to be correct: Math.ceil(questions.length * 0.8)
    const passingCount = Math.ceil(questions.length * 0.8)
    
    for (let i = 0; i < questions.length; i++) {
      const question = questions[i]
      const isCorrect = i < passingCount // First passingCount questions are correct
      
      try {
        if (isCorrect) {
          // Answer correctly
          await answerQuestionViaAPI(
            request,
            sessionId,
            question.question_id || question.id,
            question.correct_answer || question.correctAnswer,
            2000 // 2 seconds per question
          )
        } else {
          // Answer incorrectly (use wrong answer)
          await answerQuestionViaAPI(
            request,
            sessionId,
            question.question_id || question.id,
            '999', // Wrong answer
            2000
          )
        }
      } catch (error) {
        console.error(`[createPassedTestAttempt] Error answering question ${i + 1}/${questions.length}:`, error)
        throw error
      }
    }
    
    // Complete the test session with retry logic
    let completeResponse
    let retries = 3
    let lastError: Error | null = null
    
    while (retries > 0) {
      try {
        completeResponse = await request.post(`/api/practice/sessions/${sessionId}/complete`, {
          data: {
            total_duration_ms: questions.length * 2000
          },
          timeout: 30000 // 30 second timeout per request
        })
        
        if (completeResponse.ok()) {
          break
        } else {
          const errorText = await completeResponse.text().catch(() => 'Unknown error')
          throw new Error(`Failed to complete test session: ${completeResponse.status()} - ${errorText}`)
        }
      } catch (error: any) {
        lastError = error
        retries--
        if (retries > 0) {
          const waitTime = 1000 * (4 - retries) // Exponential backoff: 1s, 2s, 3s
          console.warn(`[createPassedTestAttempt] Test session completion failed, retrying in ${waitTime}ms (${retries} retries left):`, error.message)
          await new Promise(resolve => setTimeout(resolve, waitTime))
        }
      }
    }
    
    if (!completeResponse || !completeResponse.ok()) {
      throw lastError || new Error(`Failed to complete test session after retries`)
    }
  } catch (error: any) {
    const errorMessage = error?.message || String(error)
    console.error(`[createPassedTestAttempt] Failed to create test attempt:`, errorMessage)
    
    // Check if it's a request context disposal error
    if (errorMessage.includes('Request context disposed') || errorMessage.includes('disposed')) {
      throw new Error(`Request context was disposed while creating test attempt. This may indicate a timeout issue. Original error: ${errorMessage}`)
    }
    
    throw error
  }
}

