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

