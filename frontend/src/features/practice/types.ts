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

export type PartialProductsMode = 'easy' | 'normal'

export type NoticeTone = 'indigo' | 'blue' | 'orange' | 'emerald'

export type NoticeConfig = {
  tone?: NoticeTone
  icon?: 'lightbulb' | 'info'
  title?: string
  body: string
}

export type TipConfig = {
  icon?: 'lightbulb' | 'info'
  title?: string
  body: string
}

export type AnswerMode = 'remainder' | 'fraction' | 'decimal'

export type ProblemLayoutType =
  | 'vertical'
  | 'horizontal'
  | 'longDivision'
  | 'work'
  | 'partialProducts'

export type ProblemLayoutConfig = {
  type: ProblemLayoutType
  showWork?: boolean
  workSteps?: WorkStep[]
  partialProductsMode?: PartialProductsMode
  notice?: NoticeConfig
  tip?: TipConfig
  answerFormats?: AnswerMode[]
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
  mathTypeLabel?: string
  question_id?: number | string
}

export type PracticeAttempt = {
  questionId: string
  prompt: string
  submittedAnswer: string
  correctAnswer: string
  isCorrect: boolean
  awardedPoints: number
  elapsedMs?: number
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

