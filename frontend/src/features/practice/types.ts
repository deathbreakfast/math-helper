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

export type LevelUpResult = {
  eligible?: boolean
  new_level?: number
  missing_achievements?: string[]
  errors?: string[]

  // XP-based leveling payload (see MATH_CONCEPTS.md)
  earned_xp?: number
  previous_total_xp?: number
  total_xp?: number
  previous_level?: number
  leveled_up?: boolean
  xp_progress?: {
    level: number
    total_xp: number
    current_level_total_xp: number
    next_level_total_xp: number | null
    xp_into_level: number
    xp_to_next_level: number | null
  }
  xp_breakdown?: {
    concept_id?: string | null
    xp_per_correct?: number
    correct_count?: number
    base_xp?: number
    multipliers?: Array<{ achievement_code?: string; multiplier?: number }>
    total_multiplier?: number
    multiplied_xp?: number
    bonus_xp?: number
    bonus_xp_sources?: Array<{ achievement_code?: string; bonus_xp?: number }>
    total_awarded_xp_raw?: number
  }
}

export type PracticeSessionSummary = {
  id: string
  submittedAt: string
  status: string
  message?: string
  concept_id?: string
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
  achievements?: Array<{
    id?: string
    code?: string
    title?: string
    description?: string
    icon?: string
    category?: string
    earnedAt?: string
  }>
  level_up?: LevelUpResult
}

