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
  title: string
  description: string
  icon: string
  earnedAt: Date
  category: string
}

export type Learner = {
  id: string
  name: string
  avatar: string
  pin: string
  level: number
  questionsAnswered: number
  weeklyGain?: number
  averageSpeed: number
  achievements: LearnerAchievement[]
  stats: LearnerStats
}

export type ApiLearnerAchievement = Omit<LearnerAchievement, 'earnedAt'> & {
  earnedAt: string
}

export type ApiLearner = {
  id: number
  name: string
  avatar: string
  pin: string
  level: number
  questionsAnswered?: number
  weeklyGain?: number
  averageSpeed?: number
  stats?: Partial<LearnerStats>
  achievements?: ApiLearnerAchievement[]
}


