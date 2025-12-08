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
  // Test-specific fields (deprecated - test achievements removed)
  testType?: TestType
  performanceTier?: PerformanceTier
  speedRequirement?: number // seconds per question
  accuracyRequirement?: number // percentage
  questionCountRequirement?: number
}

// Test achievements are now defined in the backend (achievements_config.py)
// and fetched via the /api/achievements/definitions endpoint.
// This file now only contains TypeScript type definitions.

// Original Achievement Definitions
export const STREAK_ACHIEVEMENTS: Achievement[] = [
  {
    id: 's1',
    title: 'First Steps',
    description: 'Complete a 2-day streak',
    icon: '🔥',
    type: 'streak',
    tier: 'Bronze',
    requirement: '2-day streak',
    status: 'locked',
    isHidden: false,
    category: 'streak',
    count: 0,
  },
  {
    id: 's2',
    title: 'Getting Consistent',
    description: 'Complete a 3-day streak',
    icon: '🔥',
    type: 'streak',
    tier: 'Bronze',
    requirement: '3-day streak',
    status: 'locked',
    isHidden: false,
    category: 'streak',
    count: 0,
  },
  {
    id: 's3',
    title: 'Practice Makes Perfect',
    description: 'Complete a 5-day streak',
    icon: '🔥',
    type: 'streak',
    tier: 'Silver',
    requirement: '5-day streak',
    status: 'locked',
    isHidden: false,
    category: 'streak',
    count: 0,
  },
  {
    id: 's4',
    title: 'Dedicated Learner',
    description: 'Complete a 10-day streak',
    icon: '🔥',
    type: 'streak',
    tier: 'Gold',
    requirement: '10-day streak',
    status: 'locked',
    isHidden: false,
    category: 'streak',
    count: 0,
  },
]

export const MILESTONE_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'm1',
    title: 'First Victory',
    description: 'Answer your first question',
    icon: '🎯',
    type: 'milestone',
    tier: 'Starter',
    requirement: '1 question',
    status: 'locked',
    isHidden: false,
    category: 'milestone',
    count: 0,
  },
  {
    id: 'm2',
    title: 'Century Club',
    description: 'Answer 100 questions',
    icon: '💯',
    type: 'milestone',
    tier: 'Gold',
    requirement: '100 questions',
    status: 'locked',
    isHidden: false,
    category: 'milestone',
    count: 0,
  },
]

