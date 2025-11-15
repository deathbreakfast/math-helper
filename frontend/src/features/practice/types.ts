import type { Learner, LearnerAchievement, LearnerStats } from '../../lib/learners/types'

export type UserStats = LearnerStats
export type Achievement = LearnerAchievement
export type User = Learner

export type AnswerFormat = 'integer' | 'remainder' | 'fraction' | 'decimal' | 'mixed'

export type WorkStep = {
  id: string
  description: string
  value?: string
  isEditable?: boolean
}

export type ProblemLayoutType = 'vertical' | 'horizontal' | 'longDivision' | 'work'

export type ProblemLayoutConfig = {
  type: ProblemLayoutType
  showWork?: boolean
  workSteps?: WorkStep[]
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
  layout?: ProblemLayoutConfig
  answerFormat?: AnswerFormat
  acceptedAnswers?: string[]
  decimalPlaces?: number
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

