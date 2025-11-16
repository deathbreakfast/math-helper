import { useEffect, useMemo, useState } from 'react'

import {
  generateDivisionShowcase,
  generateMultiplicationShowcase,
  generateProblems,
} from '../utils/generateProblems'
import type { PracticeMode, PracticeQuestion, User } from '../types'

type FeedbackState = 'correct' | 'incorrect' | null

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
  handleAnswerChange: (value: string) => void
  handleCheckAnswer: () => void
  goToQuestion: (index: number) => void
  handleMove: (direction: 'next' | 'prev') => void
  toggleFlag: () => void
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

  // Regenerate problems when the learner or mode changes
  useEffect(() => {
    if (practiceMode === 'multiplication') {
      setProblems(generateMultiplicationShowcase())
      setCurrentQuestionIndex(0)
      setUserAnswer('')
      setFeedback(null)
      setShowAnswer(false)
      return
    }

    if (practiceMode === 'division') {
      setProblems(generateDivisionShowcase())
      setCurrentQuestionIndex(0)
      setUserAnswer('')
      setFeedback(null)
      setShowAnswer(false)
      return
    }

    if (!selectedUser) {
      setProblems([])
      setCurrentQuestionIndex(0)
      setUserAnswer('')
      setFeedback(null)
      setShowAnswer(false)
      return
    }

    setProblems(generateProblems(selectedUser.level ?? 1))
    setCurrentQuestionIndex(0)
    setUserAnswer('')
    setFeedback(null)
    setShowAnswer(false)
  }, [selectedUser, practiceMode])

  const currentQuestion = problems[currentQuestionIndex]

  const isPartialProducts = currentQuestion?.layout?.type === 'partialProducts'
  const isLongDivision = currentQuestion?.layout?.type === 'longDivision'

  const handleAnswerChange = (value: string) => {
    const sanitized = value.replace(/[^\d-]/g, '')
    setUserAnswer(sanitized)
  }

  const handleCheckAnswer = () => {
    if (!currentQuestion || !userAnswer.trim()) return
    const numericAnswer = Number(userAnswer)
    const correct = numericAnswer === Number(currentQuestion.correctAnswer)
    setFeedback(correct ? 'correct' : 'incorrect')
    setShowAnswer(true)
  }

  const goToQuestion = (index: number) => {
    setCurrentQuestionIndex(index)
    setUserAnswer('')
    setFeedback(null)
    setShowAnswer(false)
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

  const progressPercent = problems.length ? ((currentQuestionIndex + 1) / problems.length) * 100 : 0
  const cardCounterDisplay = problems.length ? `${currentQuestionIndex + 1} / ${problems.length}` : '0 / 0'

  return {
    problems,
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
    handleAnswerChange,
    handleCheckAnswer,
    goToQuestion,
    handleMove,
    toggleFlag,
  }
}


