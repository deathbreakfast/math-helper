import { useEffect, useMemo, useCallback, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'

import type { PracticeQuestion, User } from '../types'
import { logError } from '../../../utils/logger'
import type { FeedbackState, QuestionAnswer } from '../utils/sessionReconstruction'
import { usePracticeState } from './usePracticeState'
import { startSession, checkAnswer, completeSession, createSessionSummary } from './usePracticeAPI'
import type { PracticeMode } from './usePracticeAPI'
import { initializeSessionState, loadQuestionAnswer } from './usePracticeSessionHelpers'

type UsePracticeSessionArgs = {
  selectedUser: User | null
  practiceMode: PracticeMode
  navigate?: (path: string) => void
}

type UsePracticeSessionResult = {
  problems: PracticeQuestion[]
  currentQuestionIndex: number
  currentQuestion: PracticeQuestion | undefined
  userAnswer: string
  feedback: FeedbackState
  showAnswer: boolean
  flaggedQuestions: Record<string, boolean>
  isPartialProducts: boolean
  isLongDivision: boolean
  progressPercent: number
  cardCounterDisplay: string
  questionAnswers: Record<string, QuestionAnswer>
  sessionMode: string
  sessionError: string | null
  isLoadingProblems: boolean
  handleAnswerChange: (value: string) => void
  handleCheckAnswer: () => void
  handleSetAnswer: (questionId: string, answer: string, isCorrect: boolean) => void
  goToQuestion: (index: number) => void
  handleMove: (direction: 'next' | 'prev') => void
  toggleFlag: () => void
  canSubmit: boolean
  handleSubmit: () => void
}


export const usePracticeSession = ({
  selectedUser,
  practiceMode,
  navigate,
}: UsePracticeSessionArgs): UsePracticeSessionResult => {
  const [searchParams] = useSearchParams()
  const { state, actions } = usePracticeState()
  
  // Extract searchParams values we need to avoid dependency on the object itself
  // Use useMemo to create stable references based on the actual string values
  const conceptIdValue = searchParams.get('conceptId')
  const isConceptValue = searchParams.get('isConcept')
  const resumeOldestValue = searchParams.get('resumeOldest')
  
  // Create a stable searchParams object for startSession
  const stableSearchParams = useMemo(() => {
    const params = new URLSearchParams()
    if (conceptIdValue) params.set('conceptId', conceptIdValue)
    if (isConceptValue === 'true') params.set('isConcept', 'true')
    if (resumeOldestValue === 'true') params.set('resumeOldest', 'true')
    return params
  }, [conceptIdValue, isConceptValue, resumeOldestValue])
  
  const {
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
  } = state

  const {
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
  } = actions

  // Fetch problems from backend API when learner or mode changes
  const fetchProblems = useCallback(async () => {
    if (!selectedUser) {
      resetState()
      return
    }

    setIsLoadingProblems(true)
    setSessionError(null)
    try {
      const result = await startSession({
        selectedUser,
        practiceMode,
        searchParams: stableSearchParams,
      })

      initializeSessionState(result, {
        setProblems,
        setSessionId,
        setSessionMode,
        setCurrentQuestionIndex,
        setQuestionAnswers,
        setQuestionStartTimes,
        setFlaggedQuestions,
        setUserAnswer,
        setFeedback,
        setShowAnswer,
      })
    } catch (error) {
      logError('Error fetching problems:', error)
      // Set error message for display - user can retry
      const errorMessage = error instanceof Error ? error.message : 'Failed to start session'
      setSessionError(errorMessage)
      setProblems([])
    } finally {
      setIsLoadingProblems(false)
    }
  }, [selectedUser, practiceMode, stableSearchParams, resetState])

  useEffect(() => {
    fetchProblems()
  }, [fetchProblems])

  const currentQuestion = problems[currentQuestionIndex]

  // Track start time when question changes
  const currentQuestionId = currentQuestion?.id
  useEffect(() => {
    if (currentQuestionId && !questionStartTimes[currentQuestionId]) {
      setQuestionStartTimes((prev) => ({
        ...prev,
        [currentQuestionId]: Date.now(),
      }))
    }
  }, [currentQuestionId, questionStartTimes])

  // Load saved answer when switching questions
  useEffect(() => {
    loadQuestionAnswer(currentQuestion, questionAnswers, {
      setUserAnswer,
      setFeedback,
      setShowAnswer,
    })
  }, [currentQuestion, questionAnswers])

  const isPartialProducts = currentQuestion?.layout?.type === 'partialProducts'
  const isLongDivision = currentQuestion?.layout?.type === 'longDivision'

  const handleAnswerChange = (value: string) => {
    if (currentQuestion?.id && questionAnswers[currentQuestion.id]?.isChecked) {
      // Don't allow changes if answer is locked
      return
    }
    const sanitized = value.replace(/[^\d-]/g, '')
    setUserAnswer(sanitized)
  }

  const handleCheckAnswer = async () => {
    if (!currentQuestion || !userAnswer.trim() || !sessionId) return
    if (questionAnswers[currentQuestion.id]?.isChecked) return // Already checked

    // Calculate elapsed time
    const startTime = questionStartTimes[currentQuestion.id] || Date.now()
    const elapsedMs = Date.now() - startTime

    try {
      // Check answer with backend
      const data = await checkAnswer({
        sessionId,
        questionId: currentQuestion.question_id || currentQuestion.id,
        submittedAnswer: userAnswer,
        durationMs: elapsedMs,
      })
      
      const feedbackState: FeedbackState = data.is_correct ? 'correct' : 'incorrect'

      // Save the answer
      setQuestionAnswers((prev) => ({
        ...prev,
        [currentQuestion.id]: {
          answer: userAnswer,
          isChecked: true,
          feedback: feedbackState,
          elapsedMs,
        },
      }))

      setFeedback(feedbackState)
      setShowAnswer(true)
    } catch (error) {
      logError('Error checking answer:', error)
      // Show error to user instead of silently falling back
      // This ensures backend correctness is enforced
      const errorMessage = error instanceof Error ? error.message : 'Failed to check answer. Please try again.'
      setSessionError(errorMessage)
    }
  }

  const handleSetAnswer = (questionId: string, answer: string, isCorrect: boolean) => {
    const startTime = questionStartTimes[questionId] || Date.now()
    const elapsedMs = Date.now() - startTime

    setQuestionAnswers((prev) => ({
      ...prev,
      [questionId]: {
        answer,
        isChecked: true,
        feedback: isCorrect ? 'correct' : 'incorrect',
        elapsedMs,
      },
    }))
  }

  const goToQuestion = (index: number) => {
    setCurrentQuestionIndex(index)
    // Answer will be loaded via useEffect
  }

  const handleMove = (direction: 'next' | 'prev') => {
    if (direction === 'next' && currentQuestionIndex < problems.length - 1) {
      goToQuestion(currentQuestionIndex + 1)
    }
    if (direction === 'prev' && currentQuestionIndex > 0) {
      goToQuestion(currentQuestionIndex - 1)
    }
  }

  const toggleFlag = () => {
    if (!currentQuestion) return
    setFlaggedQuestions((prev) => ({
      ...prev,
      [currentQuestion.id]: !prev[currentQuestion.id],
    }))
  }

  const canSubmit = useMemo(() => {
    return (
      problems.length > 0 &&
      problems.every((problem) => {
        const answer = questionAnswers[problem.id]
        return answer?.isChecked
      })
    )
  }, [problems, questionAnswers])

  const handleSubmit = async () => {
    if (!selectedUser || !canSubmit || !sessionId) return

    try {
      // Complete session with backend
      const totalDurationMs = Object.values(questionAnswers).reduce(
        (sum, qa) => sum + (qa.elapsedMs || 0),
        0
      )

      const data = await completeSession({
        sessionId,
        totalDurationMs,
      })

      // Create session summary from backend response
      const sessionSummary = createSessionSummary(data, problems, questionAnswers, selectedUser)

      // Save to localStorage (for summary page display - this is different from session state)
      localStorage.setItem('lastPracticeSession', JSON.stringify(sessionSummary))

      // Navigate to summary page - only pass sessionId, not entire session object
      const sessionIdForNav = sessionSummary.id
      if (navigate) {
        // Use navigate function which should preserve context params
        navigate(`/summary?sessionId=${sessionIdForNav}`)
      } else {
        // Fallback: preserve context params manually
        const contextParams = new URLSearchParams()
        contextParams.set('sessionId', sessionIdForNav)
        window.location.href = `/summary?${contextParams.toString()}`
      }
    } catch (error) {
      logError('Failed to complete session:', error)
      // Show error to user instead of silently falling back
      // This ensures backend correctness is enforced and achievements/XP are properly calculated
      const errorMessage = error instanceof Error ? error.message : 'Failed to complete session. Please try again.'
      setSessionError(errorMessage)
    }
  }

  const progressPercent = problems.length ? ((currentQuestionIndex + 1) / problems.length) * 100 : 0
  const cardCounterDisplay = problems.length ? `${currentQuestionIndex + 1} / ${problems.length}` : '0 / 0'

  return {
    problems: isLoadingProblems ? [] : problems,
    currentQuestionIndex,
    currentQuestion,
    userAnswer,
    feedback,
    showAnswer,
    flaggedQuestions,
    isPartialProducts,
    isLongDivision,
    progressPercent,
    cardCounterDisplay,
    questionAnswers,
    sessionMode,
    sessionError,
    handleAnswerChange,
    handleCheckAnswer,
    handleSetAnswer,
    goToQuestion,
    handleMove,
    toggleFlag,
    canSubmit,
    handleSubmit,
    isLoadingProblems,
  }
}


