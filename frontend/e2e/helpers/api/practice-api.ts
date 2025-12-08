import { APIRequestContext } from '@playwright/test'

/**
 * Start a practice session via API
 * Returns session data with session_id and questions
 */
export async function startPracticeSessionViaAPI(
  request: APIRequestContext,
  userId: number,
  options?: {
    mode?: string
    level?: number
  }
): Promise<{ session_id: number; questions: any[] }> {
  const response = await request.post('/api/practice/sessions/start', {
    data: {
      user_id: userId,
      mode: options?.mode || 'standard',
      level: options?.level,
    },
  })

  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to start session: ${JSON.stringify(error)}`)
  }

  return await response.json()
}

/**
 * Answer a question via API
 * Returns response with is_correct and correct_answer
 */
export async function answerQuestionViaAPI(
  request: APIRequestContext,
  sessionId: number,
  questionId: number,
  submittedAnswer: string,
  durationMs?: number
): Promise<{ is_correct: boolean; correct_answer: string }> {
  const response = await request.post('/api/practice/questions/check', {
    data: {
      session_id: sessionId,
      question_id: questionId,
      submitted_answer: submittedAnswer,
      duration_ms: durationMs,
    },
  })

  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to check answer: ${JSON.stringify(error)}`)
  }

  return await response.json()
}

/**
 * Complete a practice session via API
 * This completes the session, awards achievements, and checks leveling
 */
export async function completeSessionViaAPI(
  request: APIRequestContext,
  sessionId: number,
  totalDurationMs?: number
): Promise<any> {
  const response = await request.post(`/api/practice/sessions/${sessionId}/complete`, {
    data: {
      total_duration_ms: totalDurationMs,
    },
  })

  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to complete session: ${JSON.stringify(error)}`)
  }

  return await response.json()
}

/**
 * Get incomplete session for a user
 * Returns session data if found, null otherwise
 */
export async function getIncompleteSession(
  request: APIRequestContext,
  userId: number,
  mode?: string
): Promise<{ session: any; response_count: number; questions: any[] } | null> {
  const params: any = { user_id: userId }
  if (mode) {
    params.mode = mode
  }

  const response = await request.get('/api/practice/sessions/incomplete', {
    params,
  })

  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to get incomplete session: ${JSON.stringify(error)}`)
  }

  const data = await response.json()
  return data.session ? data : null
}

/**
 * Analyze question distribution across multiple questions
 * Returns level counts and percentages
 */
export async function analyzeQuestionDistribution(questions: any[]): Promise<{
  levelCounts: Record<number, number>
  levelPercentages: Record<number, number>
  totalQuestions: number
}> {
  const levelCounts: Record<number, number> = {}
  const totalQuestions = questions.length

  for (const q of questions) {
    const level = q.level || q.required_level || q.requiredLevel || 1
    levelCounts[level] = (levelCounts[level] || 0) + 1
  }

  const levelPercentages: Record<number, number> = {}
  for (const level in levelCounts) {
    levelPercentages[parseInt(level)] = (levelCounts[parseInt(level)] / totalQuestions) * 100
  }

  return { levelCounts, levelPercentages, totalQuestions }
}

/**
 * Create missed questions by answering them incorrectly
 */
export async function createMissedQuestions(
  request: APIRequestContext,
  sessionId: number,
  questionIds: number[]
): Promise<void> {
  // Answer questions incorrectly
  for (const qId of questionIds) {
    await answerQuestionViaAPI(request, sessionId, qId, '999', 5000)
  }
}

/**
 * Create slow responses by answering correctly but slowly
 * Note: This requires getting the correct answer first, which may need
 * to be passed in or fetched from the session
 */
export async function createSlowResponses(
  request: APIRequestContext,
  sessionId: number,
  questionIds: number[],
  durationMs: number,
  correctAnswers?: Map<number, string>
): Promise<void> {
  // Answer questions correctly but slowly
  for (const qId of questionIds) {
    // If correct answers provided, use them; otherwise use placeholder
    // In practice, you'd fetch from session or pass correct answers
    const answer = correctAnswers?.get(qId) || '1'
    await answerQuestionViaAPI(request, sessionId, qId, answer, durationMs)
  }
}
