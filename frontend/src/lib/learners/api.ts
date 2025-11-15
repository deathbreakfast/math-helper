import type { ApiLearner, ApiLearnerAchievement, Learner, LearnerAchievement, LearnerStats } from './types'

export const AVATAR_OPTIONS = ['👧', '👦', '🧒', '👨', '👩', '🧑', '👶', '🦸', '🦹', '🧙', '🧚', '🦄']

export const sanitizeStats = (stats: Partial<LearnerStats> | undefined): LearnerStats => ({
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

const mapAchievement = (achievement: ApiLearnerAchievement): LearnerAchievement => ({
  ...achievement,
  earnedAt: achievement.earnedAt ? new Date(achievement.earnedAt) : new Date(),
})

export const mapApiLearner = (payload: ApiLearner): Learner => ({
  id: String(payload.id),
  name: payload.name,
  avatar: payload.avatar || AVATAR_OPTIONS[0],
  pin: payload.pin,
  level: payload.level ?? 1,
  questionsAnswered: payload.questionsAnswered ?? 0,
  weeklyGain: payload.weeklyGain ?? 0,
  averageSpeed: payload.averageSpeed ?? 0,
  achievements: (payload.achievements || []).map(mapAchievement),
  stats: sanitizeStats(payload.stats),
})


