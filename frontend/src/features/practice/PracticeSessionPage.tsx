import { useEffect, useMemo, useRef, useState } from 'react'

/* eslint-disable react-hooks/set-state-in-effect */
import PracticeDeck from './components/PracticeDeck'
import PracticeHeader from './components/PracticeHeader'
import { ChevronLeft, ChevronRight, Flag } from 'lucide-react'
import { generateProblems } from './utils/generateProblems'
import type { PracticeQuestion, User } from './types'
import { PillButton } from '../../components/ui'
import { useLearners } from '../../lib/learners/hooks'

const PracticeSessionPage = () => {
  const { learners, isLoading: isLoadingLearners, error: learnersError } = useLearners()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [problems, setProblems] = useState<PracticeQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswer, setUserAnswer] = useState('')
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | null>(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [flaggedQuestions, setFlaggedQuestions] = useState<Record<string, boolean>>({})
  const practiceSectionRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const [hasAppliedShareLink, setHasAppliedShareLink] = useState(false)

  const searchParams = useMemo(() => new URLSearchParams(window.location.search), [])
  const users = learners
  const loadError = learnersError
  const isLoadingUsers = isLoadingLearners

  useEffect(() => {
    if (!selectedUser && users.length > 0) {
      setSelectedUser(users[0])
    }
  }, [users, selectedUser])

  useEffect(() => {
    if (selectedUser && !users.some((user) => user.id === selectedUser.id)) {
      setSelectedUser(null)
    }
  }, [selectedUser, users])

  useEffect(() => {
    if (hasAppliedShareLink || users.length === 0) return

    const sharedUserId = searchParams.get('userId')
    const sharedName = searchParams.get('user')
    let match: User | null = null
    if (sharedUserId) {
      match = users.find((user) => user.id === sharedUserId) || null
    }
    if (!match && sharedName) {
      match =
        users.find((user) => user.name.toLowerCase() === sharedName.toLowerCase()) || null
    }

    if (match) {
      setSelectedUser(match)
      setCurrentQuestionIndex(0)
    }

    setHasAppliedShareLink(true)
  }, [hasAppliedShareLink, searchParams, users])

  useEffect(() => {
    if (!selectedUser) {
      setProblems([])
      return
    }
    setProblems(generateProblems(selectedUser.level ?? 1))
    setCurrentQuestionIndex(0)
    setUserAnswer('')
    setFeedback(null)
    setShowAnswer(false)
  }, [selectedUser])

  useEffect(() => {
    setUserAnswer('')
    setFeedback(null)
    setShowAnswer(false)
    inputRef.current?.focus()
  }, [currentQuestionIndex])

  useEffect(() => {
    if (!selectedUser || !practiceSectionRef.current) return
    practiceSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [selectedUser])

  const currentQuestion = problems[currentQuestionIndex]

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <PracticeHeader
          selectedUser={selectedUser}
          cardCounterDisplay={cardCounterDisplay}
          currentQuestion={currentQuestion}
          progressPercent={progressPercent}
        />

        {loadError && (
          <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{loadError}</div>
        )}

        {!loadError && !isLoadingUsers && !selectedUser && (
          <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
            No learner selected. Use a dashboard share link to launch practice for a specific student.
          </div>
        )}

        {selectedUser &&
          currentQuestion &&
          problems.length > 0 &&
          (() => {
            const isFlagged = Boolean(flaggedQuestions[currentQuestion.id])
            return (
              <>
                <PracticeDeck
                  practiceSectionRef={practiceSectionRef}
                  question={currentQuestion}
                  userAnswer={userAnswer}
                  onAnswerChange={handleAnswerChange}
                  onSubmit={handleCheckAnswer}
                  feedback={feedback}
                  showAnswer={showAnswer}
                  inputRef={inputRef}
                />

                <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                  <PillButton
                    variant="surface"
                    onClick={() => handleMove('prev')}
                    disabled={currentQuestionIndex === 0}
                    leftIcon={<ChevronLeft className="h-4 w-4" />}
                  >
                    Previous
                  </PillButton>
                  <PillButton
                    variant={isFlagged ? 'solid' : 'surface'}
                    tone="amber"
                    onClick={toggleFlag}
                    leftIcon={<Flag className="h-4 w-4" />}
                  >
                    {isFlagged ? 'Flagged' : 'Flag for Review'}
                  </PillButton>
                  <PillButton
                    tone="emerald"
                    onClick={() => handleMove('next')}
                    disabled={currentQuestionIndex >= problems.length - 1}
                    rightIcon={<ChevronRight className="h-4 w-4" />}
                  >
                    {currentQuestionIndex >= problems.length - 1 ? 'Complete' : 'Next'}
                  </PillButton>
                </div>
              </>
            )
          })()}
      </div>
    </div>
  )
}

export default PracticeSessionPage


