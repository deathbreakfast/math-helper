/**
 * Helper functions for usePracticeSession hook.
 * Extracted to separate concerns and improve testability.
 */

import type { FeedbackState, QuestionAnswer } from '../utils/sessionReconstruction'
import type { PracticeQuestion } from '../types'
import type { StartSessionResult } from './usePracticeAPI'

/**
 * Synchronize current question state from session state.
 */
export function syncCurrentQuestionState(
  result: StartSessionResult,
  setters: {
    setUserAnswer: (answer: string) => void
    setFeedback: (feedback: FeedbackState) => void
    setShowAnswer: (show: boolean) => void
  }
): void {
  const currentQuestion = result.sessionState.problems[result.sessionState.currentQuestionIndex]
  if (currentQuestion) {
    const answer = result.sessionState.questionAnswers[currentQuestion.id]
    if (answer) {
      setters.setUserAnswer(answer.answer)
      setters.setFeedback(answer.feedback)
      setters.setShowAnswer(answer.isChecked)
    } else {
      setters.setUserAnswer('')
      setters.setFeedback(null)
      setters.setShowAnswer(false)
    }
  } else {
    setters.setUserAnswer('')
    setters.setFeedback(null)
    setters.setShowAnswer(false)
  }
}

/**
 * Initialize session state from API result.
 */
export function initializeSessionState(
  result: StartSessionResult,
  setters: {
    setProblems: (problems: PracticeQuestion[]) => void
    setSessionId: (id: number) => void
    setSessionMode: (mode: string) => void
    setCurrentQuestionIndex: (index: number) => void
    setQuestionAnswers: (answers: Record<string, QuestionAnswer>) => void
    setQuestionStartTimes: (times: Record<string, number>) => void
    setFlaggedQuestions: (flagged: Record<string, boolean>) => void
    setUserAnswer: (answer: string) => void
    setFeedback: (feedback: FeedbackState) => void
    setShowAnswer: (show: boolean) => void
  }
): void {
  // Set session state
  setters.setProblems(result.sessionState.problems)
  setters.setSessionId(result.sessionId)
  setters.setSessionMode(result.sessionMode)
  setters.setCurrentQuestionIndex(result.sessionState.currentQuestionIndex)
  setters.setQuestionAnswers(result.sessionState.questionAnswers)
  setters.setQuestionStartTimes(result.sessionState.questionStartTimes)
  setters.setFlaggedQuestions(result.sessionState.flaggedQuestions)

  // Sync current question state
  syncCurrentQuestionState(result, {
    setUserAnswer: setters.setUserAnswer,
    setFeedback: setters.setFeedback,
    setShowAnswer: setters.setShowAnswer,
  })
}

/**
 * Load saved answer when switching to a question.
 */
export function loadQuestionAnswer(
  currentQuestion: PracticeQuestion | undefined,
  questionAnswers: Record<string, QuestionAnswer>,
  setters: {
    setUserAnswer: (answer: string) => void
    setFeedback: (feedback: FeedbackState) => void
    setShowAnswer: (show: boolean) => void
  }
): void {
  if (currentQuestion?.id) {
    const saved = questionAnswers[currentQuestion.id]
    if (saved) {
      setters.setUserAnswer(saved.answer)
      setters.setFeedback(saved.feedback)
      setters.setShowAnswer(saved.isChecked)
    } else {
      setters.setUserAnswer('')
      setters.setFeedback(null)
      setters.setShowAnswer(false)
    }
  }
}

