import type { PracticeQuestion } from '../types'
import { transformBackendQuestionsToPracticeQuestions } from './questionTransformers'

export type FeedbackState = 'correct' | 'incorrect' | null

export type QuestionAnswer = {
  answer: string
  isChecked: boolean
  feedback: FeedbackState
  elapsedMs?: number
}

export type ReconstructedSessionState = {
  problems: PracticeQuestion[]
  questionAnswers: Record<string, QuestionAnswer>
  currentQuestionIndex: number
  questionStartTimes: Record<string, number>
  flaggedQuestions: Record<string, boolean>
}

/**
 * Reconstruct session state from backend API response.
 * Handles both new sessions and incomplete sessions being resumed.
 */
export function reconstructSessionStateFromResponse(
  responseData: any
): ReconstructedSessionState {
  const questions = responseData.questions || []
  const sessionMode = responseData.mode || 'standard'

  // Transform questions to PracticeQuestion[]
  const problems = transformBackendQuestionsToPracticeQuestions(questions, sessionMode)

  // Build questionAnswers from response data (questions with responses)
  const questionAnswers: Record<string, QuestionAnswer> = {}
  let firstUnansweredIndex = -1

  problems.forEach((problem, index) => {
    const questionData = questions.find(
      (q: any) => (q.question_id || q.id) === (problem.question_id || problem.id)
    )

    if (questionData?.response) {
      // Question has been answered
      questionAnswers[problem.id] = {
        answer: questionData.response.submitted_answer || '',
        isChecked: true,
        feedback: questionData.response.is_correct ? 'correct' : 'incorrect',
        elapsedMs: questionData.response.duration_ms,
      }
    } else {
      // Question is unanswered
      if (firstUnansweredIndex === -1) {
        firstUnansweredIndex = index
      }
    }
  })

  // Find latest unanswered question index (or last answered if all are answered)
  const currentQuestionIndex =
    firstUnansweredIndex !== -1 ? firstUnansweredIndex : problems.length > 0 ? problems.length - 1 : 0

  // Initialize empty questionStartTimes and flaggedQuestions
  const questionStartTimes: Record<string, number> = {}
  const flaggedQuestions: Record<string, boolean> = {}

  return {
    problems,
    questionAnswers,
    currentQuestionIndex,
    questionStartTimes,
    flaggedQuestions,
  }
}





