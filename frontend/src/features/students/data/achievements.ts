export type AchievementType = 'streak' | 'speed-session' | 'speed-question' | 'milestone' | 'hidden'

export type AchievementStatus = 'locked' | 'unlocked' | 'in-progress'

export type Achievement = {
  id: string
  title: string
  description: string
  icon: string
  type: AchievementType
  tier: string
  requirement: string
  status: AchievementStatus
  progress?: number
  maxProgress?: number
  unlockedAt?: Date
  isHidden: boolean
  hint?: string
  category: string
  count?: number
  lastEarnedAt?: Date
  metadata?: Record<string, any> // Level/operation filters for achievements with metadata
  xp_reward?: {
    bonus_xp: number
    multiplier: number
  }
  speedRequirement?: number // seconds per question
  accuracyRequirement?: number // percentage
  questionCountRequirement?: number
}

// Achievement definitions are fetched from the backend (e.g. `/api/achievements/definitions`).
// This module intentionally contains only TypeScript types shared across the students feature.

