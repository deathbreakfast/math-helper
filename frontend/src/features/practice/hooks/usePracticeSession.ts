import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

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

function transformBackendQuestionsToPracticeQuestions(
  backendQuestions: any[],
  sessionMode: string
): PracticeQuestion[] {
  return backendQuestions.map((q) => {
    // Handle layout config - may be JSON string or object
    let layout: PracticeQuestion['layout'] = undefined
    if (q.layout) {
      if (typeof q.layout === 'string') {
        try {
          layout = JSON.parse(q.layout)
        } catch {
          layout = { type: q.layout_type || 'vertical' }
        }
      } else {
        layout = q.layout
      }
    } else if (q.layout_type) {
      layout = { type: q.layout_type }
    }

    return {
      id: q.id || `q-${q.question_id}`,
      prompt: q.prompt || '',
      operation: q.operation || 'addition',
      operand1: q.operand1 || 0,
      operand2: q.operand2 || 0,
      correctAnswer: q.correctAnswer || q.correct_answer || '',
      difficulty: q.difficulty || 'Level 1',
      targetMs: q.targetMs || q.target_ms || 4000,
      hint: q.hint || '',
      layout,
      answerFormat: q.answerFormat || q.answer_format,
      acceptedAnswers: q.acceptedAnswers || q.accepted_answers,
      decimalPlaces: q.decimalPlaces || q.decimal_places,
      mathTypeLabel: q.mathTypeLabel || q.math_type_label,
      question_id: q.question_id || q.id,
    }
  })
}

function reconstructSessionStateFromResponse(
  responseData: any
): {
  problems: PracticeQuestion[]
  questionAnswers: Record<string, QuestionAnswer>
  currentQuestionIndex: number
  questionStartTimes: Record<string, number>
  flaggedQuestions: Record<string, boolean>
} {
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

export const usePracticeSession = ({
  selectedUser,
  practiceMode,
  navigate,
}: UsePracticeSessionArgs): UsePracticeSessionResult => {
  const [searchParams] = useSearchParams()
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
      setSessionError(null)
      return
    }

    const fetchProblems = async () => {
      setIsLoadingProblems(true)
      setSessionError(null)
      try {
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

        // Set session state
        setProblems(sessionState.problems)
        setSessionId(data.session_id)
        setSessionMode(data.mode || 'standard')
        setCurrentQuestionIndex(sessionState.currentQuestionIndex)
        setQuestionAnswers(sessionState.questionAnswers)
        setQuestionStartTimes(sessionState.questionStartTimes)
        setFlaggedQuestions(sessionState.flaggedQuestions)

        // Set current question state
        const currentQuestion = sessionState.problems[sessionState.currentQuestionIndex]
        if (currentQuestion) {
          const answer = sessionState.questionAnswers[currentQuestion.id]
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
        console.error('Error fetching problems:', error)
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
          level: data.level_up?.new_level || selectedUser.level,
        },
        attempts,
        achievements: data.achievements || [],
        level_up: data.level_up || {},
      }

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
        if (searchParams.get('env')) {
          contextParams.set('env', searchParams.get('env')!)
        }
        contextParams.set('sessionId', sessionIdForNav)
        window.location.href = `/summary?${contextParams.toString()}`
      }
    } catch (error) {
      console.error('Failed to complete session:', error)
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
      
      // Navigate to summary page - only pass sessionId, not entire session object
      const sessionId = sessionSummary.id
      if (navigate) {
        // Use navigate function which should preserve context params
        navigate(`/summary?sessionId=${sessionId}`)
      } else {
        // Fallback: preserve context params manually
        const contextParams = new URLSearchParams()
        if (searchParams.get('env')) {
          contextParams.set('env', searchParams.get('env')!)
        }
        contextParams.set('sessionId', sessionId)
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


