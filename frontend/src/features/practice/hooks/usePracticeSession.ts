import { useEffect, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'

import type { PracticeQuestion, User } from '../types'
import { logError } from '../../../utils/logger'
import type { FeedbackState, QuestionAnswer } from '../utils/sessionReconstruction'
import { usePracticeState } from './usePracticeState'
import { startSession, checkAnswer, completeSession, createSessionSummary } from './usePracticeAPI'
import type { PracticeMode } from './usePracticeAPI'

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
  useEffect(() => {
    if (!selectedUser) {
      resetState()
      return
    }

    const fetchProblems = async () => {
      setIsLoadingProblems(true)
      setSessionError(null)
      try {
        const result = await startSession({
          selectedUser,
          practiceMode,
          searchParams,
        })

        // Set session state
        setProblems(result.sessionState.problems)
        setSessionId(result.sessionId)
        setSessionMode(result.sessionMode)
        setCurrentQuestionIndex(result.sessionState.currentQuestionIndex)
        setQuestionAnswers(result.sessionState.questionAnswers)
        setQuestionStartTimes(result.sessionState.questionStartTimes)
        setFlaggedQuestions(result.sessionState.flaggedQuestions)

        // Set current question state
        const currentQuestion = result.sessionState.problems[result.sessionState.currentQuestionIndex]
        if (currentQuestion) {
          const answer = result.sessionState.questionAnswers[currentQuestion.id]
          if (answer) {
            setUserAnswer(answer.answer)
            setFeedback(answer.feedback)
            setShowAnswer(answer.isChecked)
          } else {
            setUserAnswer('')
            setFeedback(null)
            setShowAnswer(false)
          }
        } else {
          setUserAnswer('')
          setFeedback(null)
          setShowAnswer(false)
        }
      } catch (error) {
        logError('Error fetching problems:', error)
        // Set error message for display
        const errorMessage = error instanceof Error ? error.message : 'Failed to start session'
        setSessionError(errorMessage)
        // Fallback to empty problems
        setProblems([])
      } finally {
        setIsLoadingProblems(false)
      }
    }

    fetchProblems()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedUser, practiceMode])

  const currentQuestion = problems[currentQuestionIndex]

  // Track start time when question changes
  useEffect(() => {
    if (currentQuestion?.id && !questionStartTimes[currentQuestion.id]) {
      setQuestionStartTimes((prev) => ({
        ...prev,
        [currentQuestion.id]: Date.now(),
      }))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentQuestion?.id])

  // Load saved answer when switching questions
  useEffect(() => {
    if (currentQuestion?.id) {
      const saved = questionAnswers[currentQuestion.id]
      if (saved) {
        setUserAnswer(saved.answer)
        setFeedback(saved.feedback)
        setShowAnswer(saved.isChecked)
      } else {
        setUserAnswer('')
        setFeedback(null)
        setShowAnswer(false)
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentQuestion?.id, questionAnswers])

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
        durationMs,
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
      // Fallback to client-side check
      const numericAnswer = Number(userAnswer)
      const correct = numericAnswer === Number(currentQuestion.correctAnswer)
      const feedbackState: FeedbackState = correct ? 'correct' : 'incorrect'
      
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
      // Fallback to client-side submission
      const attempts = problems.map((problem) => {
        const answer = questionAnswers[problem.id]
        const isCorrect = answer?.feedback === 'correct'
        
        return {
          questionId: problem.id,
          prompt: problem.prompt,
          submittedAnswer: answer?.answer || '',
          correctAnswer: problem.correctAnswer,
          isCorrect: isCorrect,
          awardedPoints: isCorrect ? 10 : 0,
          elapsedMs: answer?.elapsedMs,
        }
      })

      const correctCount = attempts.filter((a) => a.isCorrect).length
      const accuracy = Math.round((correctCount / attempts.length) * 100)

      const sessionSummary = {
        id: `session-${Date.now()}`,
        submittedAt: new Date().toISOString(),
        status: 'completed',
        message: 'Great job completing the practice session!',
        totals: {
          questions: attempts.length,
          correct: correctCount,
          accuracy,
        },
        user: {
          id: selectedUser.id,
          name: selectedUser.name,
          avatar: selectedUser.avatar,
          level: selectedUser.level,
        },
        attempts,
      }

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


