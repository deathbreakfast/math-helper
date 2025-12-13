export type LearnerStats = {
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

export type LearnerAchievement = {
  id: string
  code?: string
  title: string
  description: string
  icon: string
  earnedAt: Date
  category: string
  metadata?: Record<string, any>  // Achievement metadata (level, test_type, etc.)
}

export type Learner = {
  id: string
  name: string
  avatar: string
  // PIN is not included for security - use /api/users/<id>/verify-pin endpoint
  level: number
  questionsAnswered: number
  weeklyGain?: number
  averageSpeed: number
  achievements: LearnerAchievement[]
  stats: LearnerStats
}

export type ApiLearnerAchievement = Omit<LearnerAchievement, 'earnedAt'> & {
  earnedAt: string
  code?: string
}

export type ApiLearner = {
  id: number
  name: string
  avatar: string
  // PIN is not included in API responses for security
  level: number
  questionsAnswered?: number
  weeklyGain?: number
  averageSpeed?: number
  stats?: Partial<LearnerStats>
  achievements?: ApiLearnerAchievement[]
}


