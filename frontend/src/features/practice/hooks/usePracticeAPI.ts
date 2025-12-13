import { logError } from '../../../utils/logger'
import type { User, PracticeAttempt } from '../types'
import { reconstructSessionStateFromResponse } from '../utils/sessionReconstruction'
import type { ReconstructedSessionState } from '../utils/sessionReconstruction'

export type PracticeMode = 'standard' | 'multiplication' | 'division'

export type StartSessionParams = {
  selectedUser: User
  practiceMode: PracticeMode
  searchParams: URLSearchParams
}

export type StartSessionResult = {
  sessionId: number
  sessionMode: string
  sessionState: ReconstructedSessionState
}

export type CheckAnswerParams = {
  sessionId: number
  questionId: string | number
  submittedAnswer: string
  durationMs: number
}

export type CheckAnswerResult = {
  is_correct: boolean
}

export type CompleteSessionParams = {
  sessionId: number
  totalDurationMs: number
}

export type CompleteSessionResult = {
  session: {
    id?: number
    completed_at?: string
    total_questions?: number
    correct_count?: number
    accuracy?: number
  }
  level_up?: {
    new_level?: number
  }
  achievements?: Array<{
    id?: string
    code?: string
    title?: string
    description?: string
    icon?: string
    category?: string
    earnedAt?: string
  }>
}

/**
 * Start a new practice session or resume an incomplete one.
 */
export async function startSession(params: StartSessionParams): Promise<StartSessionResult> {
  const { selectedUser, practiceMode, searchParams } = params

  // Check URL parameters for test type
  const testType = searchParams.get('testType')
  const isTestParam = searchParams.get('isTest')
  const isTest = isTestParam === 'true' && testType !== null

  // Determine mode and test type
  const mode = practiceMode === 'multiplication' ? 'multiplication' : practiceMode === 'division' ? 'division' : 'standard'
  const level = selectedUser.level ?? 1

  // Call start endpoint - it handles both new and existing incomplete sessions
  const requestBody: any = {
    user_id: parseInt(selectedUser.id),
    mode,
    is_test: isTest,
    level,
  }

  if (isTest && testType) {
    requestBody.test_type = testType
  }

  const response = await fetch('/api/practice/sessions/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })

  if (!response.ok) {
    // Try to parse error message from response
    let errorMessage = `Failed to start session: ${response.statusText}`
    try {
      const errorData = await response.json()
      if (errorData.error) {
        errorMessage = errorData.error
      }
    } catch {
      // If JSON parsing fails, use the status text
    }
    throw new Error(errorMessage)
  }

  const data = await response.json()

  // Reconstruct session state from response
  const sessionState = reconstructSessionStateFromResponse(data)

  return {
    sessionId: data.session_id,
    sessionMode: data.mode || 'standard',
    sessionState,
  }
}

/**
 * Check an answer with the backend.
 */
export async function checkAnswer(params: CheckAnswerParams): Promise<CheckAnswerResult> {
  const { sessionId, questionId, submittedAnswer, durationMs } = params

  const response = await fetch('/api/practice/questions/check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      question_id: typeof questionId === 'string' ? parseInt(questionId) : questionId,
      submitted_answer: submittedAnswer,
      duration_ms: durationMs,
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to check answer: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * Complete a practice session.
 */
export async function completeSession(params: CompleteSessionParams): Promise<CompleteSessionResult> {
  const { sessionId, totalDurationMs } = params

  const response = await fetch(`/api/practice/sessions/${sessionId}/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      total_duration_ms: totalDurationMs,
    }),
  })

  if (!response.ok) {
    throw new Error(`Failed to complete session: ${response.statusText}`)
  }

  return await response.json()
}

/**
 * Create session summary from backend response and practice data.
 */
export function createSessionSummary(
  data: CompleteSessionResult,
  problems: any[],
  questionAnswers: Record<string, any>,
  selectedUser: User
): {
  id: string
  submittedAt: string
  status: string
  message?: string
  totals: {
    questions: number
    correct: number
    accuracy: number
  }
  user: {
    id: number
    name: string
    avatar?: string
    level?: number
  }
  attempts: PracticeAttempt[]
  achievements?: Array<{
    id?: string
    code?: string
    title?: string
    description?: string
    icon?: string
    category?: string
    earnedAt?: string
  }>
  level_up?: {
    eligible?: boolean
    new_level?: number
    missing_achievements?: string[]
    errors?: string[]
  }
} {
  // Create session summary from backend response
  const attempts: PracticeAttempt[] = problems.map((problem) => {
    const answer = questionAnswers[problem.id]
    const isCorrect = answer?.feedback === 'correct'
    
    return {
      questionId: problem.question_id?.toString() || problem.id,
      prompt: problem.prompt,
      submittedAnswer: answer?.answer || '',
      correctAnswer: problem.correctAnswer,
      isCorrect: isCorrect,
      awardedPoints: isCorrect ? 10 : 0,
      elapsedMs: answer?.elapsedMs,
    }
  })

  return {
    id: data.session?.id?.toString() || `session-${Date.now()}`,
    submittedAt: data.session?.completed_at || new Date().toISOString(),
    status: 'completed',
    message: 'Great job completing the practice session!',
    totals: {
      questions: data.session?.total_questions || attempts.length,
      correct: data.session?.correct_count || attempts.filter((a) => a.isCorrect).length,
      accuracy: data.session?.accuracy || Math.round(
        ((data.session?.correct_count || 0) / (data.session?.total_questions || 1)) * 100
      ),
    },
    user: {
      id: selectedUser.id,
      name: selectedUser.name,
      avatar: selectedUser.avatar,
      level: data.level_up?.new_level || selectedUser.level,
    },
    attempts,
    achievements: data.achievements || [],
    level_up: data.level_up || {},
  }
}




