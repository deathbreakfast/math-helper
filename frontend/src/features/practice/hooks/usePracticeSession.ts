import { useEffect, useMemo, useState } from 'react'

import type { PracticeQuestion, User, PracticeAttempt } from '../types'

export type PracticeMode = 'standard' | 'multiplication' | 'division'

type FeedbackState = 'correct' | 'incorrect' | null

type QuestionAnswer = {
  answer: string
  isChecked: boolean
  feedback: FeedbackState
  elapsedMs?: number
}

type UsePracticeSessionArgs = {
  selectedUser: User | null
  practiceMode: PracticeMode
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
}: UsePracticeSessionArgs): UsePracticeSessionResult => {
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

  // Fetch problems from backend API when learner or mode changes
  useEffect(() => {
    if (!selectedUser) {
      setProblems([])
      setCurrentQuestionIndex(0)
      setUserAnswer('')
      setFeedback(null)
      setShowAnswer(false)
      setQuestionAnswers({})
      setQuestionStartTimes({})
      setSessionId(null)
      return
    }

    const fetchProblems = async () => {
      setIsLoadingProblems(true)
      try {
        // Determine mode and test type
        const mode = practiceMode === 'multiplication' ? 'multiplication' : practiceMode === 'division' ? 'division' : 'standard'
        const isTest = false // For now, always practice mode
        const level = selectedUser.level ?? 1

        const response = await fetch('/api/practice/sessions/start', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: parseInt(selectedUser.id),
            mode,
            is_test: isTest,
            level,
          }),
        })

        if (!response.ok) {
          throw new Error(`Failed to start session: ${response.statusText}`)
        }

        const data = await response.json()
        setProblems(data.questions || [])
        setSessionId(data.session_id)
        setCurrentQuestionIndex(0)
        setUserAnswer('')
        setFeedback(null)
        setShowAnswer(false)
        setQuestionAnswers({})
        setQuestionStartTimes({})
      } catch (error) {
        console.error('Error fetching problems:', error)
        // Fallback to empty problems
        setProblems([])
      } finally {
        setIsLoadingProblems(false)
      }
    }

    fetchProblems()
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
  }, [currentQuestion?.id, questionStartTimes])

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
      const response = await fetch('/api/practice/questions/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          question_id: parseInt(currentQuestion.question_id || currentQuestion.id),
          submitted_answer: userAnswer,
          duration_ms: elapsedMs,
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to check answer: ${response.statusText}`)
      }

      const data = await response.json()
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
      console.error('Error checking answer:', error)
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
      const response = await fetch(`/api/practice/sessions/${sessionId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          total_duration_ms: Object.values(questionAnswers).reduce(
            (sum, qa) => sum + (qa.elapsedMs || 0),
            0
          ),
        }),
      })

      if (!response.ok) {
        throw new Error(`Failed to complete session: ${response.statusText}`)
      }

      const data = await response.json()

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

      const sessionSummary = {
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
          level: selectedUser.level,
        },
        attempts,
        achievements: data.achievements || [],
        level_up: data.level_up || {},
      }

      // Save to localStorage
      localStorage.setItem('lastPracticeSession', JSON.stringify(sessionSummary))

      // Navigate to summary page
      const sessionParam = encodeURIComponent(JSON.stringify(sessionSummary))
      window.location.href = `/summary?session=${sessionParam}`
    } catch (error) {
      console.error('Error submitting session:', error)
      // Fallback to client-side submission
      const attempts: PracticeAttempt[] = problems.map((problem) => {
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
      const sessionParam = encodeURIComponent(JSON.stringify(sessionSummary))
      window.location.href = `/summary?session=${sessionParam}`
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


