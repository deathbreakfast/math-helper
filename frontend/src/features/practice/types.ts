export type UserStats = {
  additionAccuracy: number
  subtractionAccuracy: number
  multiplicationAccuracy: number
  divisionAccuracy: number
  additionSpeed: number
  subtractionSpeed: number
  multiplicationSpeed: number
  divisionSpeed: number
  currentStreak: number
  bestStreak: number
}

export type Achievement = {
  id: string
  title: string
  description: string
  icon: string
  earnedAt: Date
  category: string
}

export type User = {
  id: string
  name: string
  avatar: string
  pin: string
  level: number
  achievements: Achievement[]
  stats: UserStats
}

export type Operation = 'addition' | 'subtraction' | 'multiplication' | 'division'

export type PracticeQuestion = {
  id: string
  prompt: string
  operation: Operation
  operand1: number
  operand2: number
  correctAnswer: string
  difficulty: string
  targetMs: number
  hint: string
}

export type PracticeAttempt = {
  questionId: string
  prompt: string
  submittedAnswer: string
  correctAnswer: string
  isCorrect: boolean
  awardedPoints: number
}

export type PracticeSessionSummary = {
  id: string
  submittedAt: string
  status: string
  message?: string
  totals: {
    questions: number
    correct: number
    accuracy: number
  }
  user: {
    id: number
    name: string
    avatar?: string
    level?: number
  }
  attempts: PracticeAttempt[]
}

export type ApiAchievement = Omit<Achievement, 'earnedAt'> & { earnedAt: string }

export type ApiUser = {
  id: number
  name: string
  avatar: string
  pin: string
  level: number
  stats?: Partial<UserStats>
  achievements?: ApiAchievement[]
}

