import { logError } from '../../../utils/logger'
import type { User, PracticeAttempt, PracticeSessionSummary, LevelUpResult } from '../types'
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
  level_up?: LevelUpResult
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

  // Check URL parameters for concept
  const conceptId = searchParams.get('conceptId')
  const isConceptParam = searchParams.get('isConcept')
  const isConcept = isConceptParam === 'true' && conceptId !== null
  const resumeOldestParam = searchParams.get('resumeOldest')
  const resumeOldest = resumeOldestParam === 'true'

  // Determine mode and test type
  const mode = practiceMode === 'multiplication' ? 'multiplication' : practiceMode === 'division' ? 'division' : 'standard'
  
  // For concepts, don't pass level - backend will derive it from concept_id
  // Otherwise use user's level
  let level: number | undefined = selectedUser.level ?? 1
  if (isConcept && conceptId) {
    // For concept practice, don't send level - backend will extract it from concept_id
    // This allows backend to use concept-based question generation
    level = undefined
    console.log(`[Practice] Starting concept practice: conceptId=${conceptId}`)
  }

  // Call start endpoint - it handles both new and existing incomplete sessions
  const requestBody: any = {
    user_id: parseInt(selectedUser.id),
    mode,
  }
  
  // Only include level if not doing concept practice
  if (level !== undefined) {
    requestBody.level = level
  }

  if (isConcept && conceptId) {
    requestBody.concept_id = conceptId
  }

  if (resumeOldest) {
    requestBody.resume_oldest = true
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
): PracticeSessionSummary {
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

  const totalQuestions = data.session?.total_questions ?? attempts.length
  const correct = data.session?.correct_count ?? attempts.filter((a) => a.isCorrect).length
  const accuracy =
    data.session?.accuracy ??
    Math.round((correct / Math.max(1, totalQuestions)) * 100)

  return {
    id: data.session?.id?.toString() || `session-${Date.now()}`,
    submittedAt: data.session?.completed_at || new Date().toISOString(),
    status: 'completed',
    message: 'Great job completing the practice session!',
    totals: {
      questions: totalQuestions,
      correct,
      accuracy,
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





