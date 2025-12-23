export type AchievementType = 'streak' | 'speed-session' | 'speed-question' | 'milestone' | 'test-completion' | 'hidden'

export type AchievementStatus = 'locked' | 'unlocked' | 'in-progress'

export type PerformanceTier = 'B' | 'A' | 'S' | 'SS' | 'SSS'

export type TestType =
  | 'addition-1digit'
  | 'addition-2digit'
  | 'addition-3digit'
  | 'subtraction-1digit'
  | 'subtraction-2digit'
  | 'subtraction-3digit'
  | 'multiplication-2'
  | 'multiplication-3'
  | 'multiplication-4'
  | 'multiplication-5'
  | 'multiplication-6'
  | 'multiplication-7'
  | 'multiplication-8'
  | 'multiplication-9'
  | 'multiplication-10'
  | 'multiplication-11'
  | 'multiplication-12'
  | 'multiplication-2digit'
  | 'multiplication-3digit'
  | 'division-1digit'
  | 'division-2digit'
  | 'division-3digit'

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
  // Test-specific fields (deprecated - test achievements removed)
  testType?: TestType
  performanceTier?: PerformanceTier
  speedRequirement?: number // seconds per question
  accuracyRequirement?: number // percentage
  questionCountRequirement?: number
}

// Achievement definitions are fetched from the backend (e.g. `/api/achievements/definitions`).
// This module intentionally contains only TypeScript types shared across the students feature.

