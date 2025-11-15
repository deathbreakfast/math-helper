import { useEffect, useMemo, useRef, useState } from 'react'

import PracticeDeck from './components/PracticeDeck'
import PracticeHeader from './components/PracticeHeader'
import { ChevronLeft, ChevronRight, Flag } from 'lucide-react'
import { generateProblems } from './utils/generateProblems'
import type { ApiAchievement, ApiUser, PracticeQuestion, User, UserStats } from './types'

const sanitizeStats = (stats: Partial<UserStats> | undefined): UserStats => ({
  additionAccuracy: stats?.additionAccuracy ?? 0,
  subtractionAccuracy: stats?.subtractionAccuracy ?? 0,
  multiplicationAccuracy: stats?.multiplicationAccuracy ?? 0,
  divisionAccuracy: stats?.divisionAccuracy ?? 0,
  additionSpeed: stats?.additionSpeed ?? 0,
  subtractionSpeed: stats?.subtractionSpeed ?? 0,
  multiplicationSpeed: stats?.multiplicationSpeed ?? 0,
  divisionSpeed: stats?.divisionSpeed ?? 0,
  currentStreak: stats?.currentStreak ?? 0,
  bestStreak: stats?.bestStreak ?? 0,
})

const mapAchievement = (achievement: ApiAchievement): Achievement => ({
  ...achievement,
  earnedAt: achievement.earnedAt ? new Date(achievement.earnedAt) : new Date(),
})

const mapUser = (payload: ApiUser): User => ({
  id: String(payload.id),
  name: payload.name,
  avatar: payload.avatar || '👧',
  pin: payload.pin,
  level: payload.level ?? 1,
  achievements: (payload.achievements || []).map(mapAchievement),
  stats: sanitizeStats(payload.stats),
})

const PracticeSessionPage = () => {
  const [users, setUsers] = useState<User[]>([])
  const [isLoadingUsers, setIsLoadingUsers] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
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

  useEffect(() => {
    const fetchUsers = async () => {
      setIsLoadingUsers(true)
      setLoadError(null)
      try {
        const response = await fetch('/api/users')
        if (!response.ok) {
          throw new Error('Unable to load learners.')
        }
        const data = await response.json()
        const parsed = Array.isArray(data.users) ? data.users.map(mapUser) : []
        setUsers(parsed)
        setSelectedUser((prev) => prev ?? parsed[0] ?? null)
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unable to load learners.'
        setLoadError(message)
        setUsers([])
      } finally {
        setIsLoadingUsers(false)
      }
    }

    fetchUsers()
  }, [])

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

        {selectedUser && currentQuestion && problems.length > 0 && (
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
              <button
                onClick={() => handleMove('prev')}
                disabled={currentQuestionIndex === 0}
                className="flex items-center gap-2 rounded-2xl bg-white px-6 py-3 font-semibold text-slate-700 shadow-md transition hover:bg-slate-50 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </button>
              <button
                onClick={toggleFlag}
                className={`flex items-center gap-2 rounded-2xl px-6 py-3 font-semibold shadow-md transition ${
                  flaggedQuestions[currentQuestion.id]
                    ? 'bg-gradient-to-r from-yellow-500 to-amber-600 text-white hover:from-yellow-600 hover:to-amber-700'
                    : 'bg-white text-slate-700 hover:bg-slate-50'
                }`}
              >
                <Flag className={`h-4 w-4 ${flaggedQuestions[currentQuestion.id] ? 'text-white' : ''}`} />
                {flaggedQuestions[currentQuestion.id] ? 'Flagged' : 'Flag for Review'}
              </button>
              <button
                onClick={() => handleMove('next')}
                disabled={currentQuestionIndex >= problems.length - 1}
                className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-3 font-semibold text-white shadow-md transition hover:from-green-600 hover:to-emerald-700 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-40"
              >
                {currentQuestionIndex >= problems.length - 1 ? 'Complete' : 'Next'}
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default PracticeSessionPage


