import { useState, useCallback } from 'react'
import type { PracticeQuestion } from '../types'
import type { FeedbackState, QuestionAnswer } from '../utils/sessionReconstruction'

export type PracticeState = {
  problems: PracticeQuestion[]
  currentQuestionIndex: number
  userAnswer: string
  feedback: FeedbackState
  showAnswer: boolean
  flaggedQuestions: Record<string, boolean>
  questionAnswers: Record<string, QuestionAnswer>
  questionStartTimes: Record<string, number>
  sessionId: number | null
  sessionMode: string
  sessionError: string | null
  isLoadingProblems: boolean
}

export type PracticeStateActions = {
  setProblems: (problems: PracticeQuestion[]) => void
  setCurrentQuestionIndex: (index: number) => void
  setUserAnswer: (answer: string) => void
  setFeedback: (feedback: FeedbackState) => void
  setShowAnswer: (show: boolean) => void
  setFlaggedQuestions: (flagged: Record<string, boolean> | ((prev: Record<string, boolean>) => Record<string, boolean>)) => void
  setQuestionAnswers: (answers: Record<string, QuestionAnswer> | ((prev: Record<string, QuestionAnswer>) => Record<string, QuestionAnswer>)) => void
  setQuestionStartTimes: (times: Record<string, number> | ((prev: Record<string, number>) => Record<string, number>)) => void
  setSessionId: (id: number | null) => void
  setSessionMode: (mode: string) => void
  setSessionError: (error: string | null) => void
  setIsLoadingProblems: (loading: boolean) => void
  resetState: () => void
}

/**
 * Hook for managing practice session state.
 * Returns state values and setter functions.
 */
export function usePracticeState(): {
  state: PracticeState
  actions: PracticeStateActions
} {
  const [problems, setProblems] = useState<PracticeQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [feedback, setFeedback] = useState<FeedbackState>(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [flaggedQuestions, setFlaggedQuestions] = useState<Record<string, boolean>>({})
  const [questionAnswers, setQuestionAnswers] = useState<Record<string, QuestionAnswer>>({})
  const [questionStartTimes, setQuestionStartTimes] = useState<Record<string, number>>({})
  const [isLoadingProblems, setIsLoadingProblems] = useState(false)
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [sessionMode, setSessionMode] = useState<string>('standard')
  const [sessionError, setSessionError] = useState<string | null>(null)

  const resetState = useCallback(() => {
    setProblems([])
    setCurrentQuestionIndex(0)
    setUserAnswer('')
    setFeedback(null)
    setShowAnswer(false)
    setQuestionAnswers({})
    setQuestionStartTimes({})
    setSessionId(null)
    setSessionError(null)
  }, [])

  return {
    state: {
      problems,
      currentQuestionIndex,
      userAnswer,
      feedback,
      showAnswer,
      flaggedQuestions,
      questionAnswers,
      questionStartTimes,
      sessionId,
      sessionMode,
      sessionError,
      isLoadingProblems,
    },
    actions: {
      setProblems,
      setCurrentQuestionIndex,
      setUserAnswer,
      setFeedback,
      setShowAnswer,
      setFlaggedQuestions,
      setQuestionAnswers,
      setQuestionStartTimes,
      setSessionId,
      setSessionMode,
      setSessionError,
      setIsLoadingProblems,
      resetState,
    },
  }
}

