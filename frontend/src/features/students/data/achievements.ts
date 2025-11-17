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
  // Test-specific fields
  testType?: TestType
  performanceTier?: PerformanceTier
  speedRequirement?: number // seconds per question
  accuracyRequirement?: number // percentage
  questionCountRequirement?: number
}

// Helper to create test achievements
export const createTestAchievements = (testType: TestType, displayName: string): Achievement[] => {
  const baseId = testType
  return [
    // B Tier - Complete test
    {
      id: `${baseId}-b`,
      title: `${displayName} - Rank B`,
      description: `Complete ${displayName} test`,
      icon: '📘',
      type: 'test-completion',
      tier: 'B',
      requirement: 'Complete test',
      status: 'locked',
      isHidden: false,
      category: 'test',
      count: 0,
      testType,
      performanceTier: 'B',
      accuracyRequirement: 0,
      questionCountRequirement: 30,
    },
    // A Tier - 100% accuracy, <30 questions
    {
      id: `${baseId}-a`,
      title: `${displayName} - Rank A`,
      description: `100% accuracy on ${displayName} (under 30 questions)`,
      icon: '📗',
      type: 'test-completion',
      tier: 'A',
      requirement: '100% accuracy, <30 questions',
      status: 'locked',
      isHidden: false,
      category: 'test',
      count: 0,
      testType,
      performanceTier: 'A',
      accuracyRequirement: 100,
      questionCountRequirement: 30,
    },
    // S Tier - 100%, <60 questions, speed requirement
    {
      id: `${baseId}-s`,
      title: `${displayName} - Rank S`,
      description: `Perfect score with speed on ${displayName}`,
      icon: '⭐',
      type: 'test-completion',
      tier: 'S',
      requirement: '100%, <60q, <6s/question',
      status: 'locked',
      isHidden: false,
      category: 'test',
      count: 0,
      testType,
      performanceTier: 'S',
      accuracyRequirement: 100,
      questionCountRequirement: 60,
      speedRequirement: 6,
    },
    // SS Tier - 100%, <90 questions, faster speed
    {
      id: `${baseId}-ss`,
      title: `${displayName} - Rank SS`,
      description: `Elite performance on ${displayName}`,
      icon: '🌟',
      type: 'test-completion',
      tier: 'SS',
      requirement: '100%, <90q, <4s/question',
      status: 'locked',
      isHidden: false,
      category: 'test',
      count: 0,
      testType,
      performanceTier: 'SS',
      accuracyRequirement: 100,
      questionCountRequirement: 90,
      speedRequirement: 4,
    },
    // SSS Tier - 100%, 100 questions, fastest speed
    {
      id: `${baseId}-sss`,
      title: `${displayName} - Rank SSS`,
      description: `Legendary mastery of ${displayName}`,
      icon: '💎',
      type: 'test-completion',
      tier: 'SSS',
      requirement: '100%, 100q, <2s/question',
      status: 'locked',
      isHidden: false,
      category: 'test',
      count: 0,
      testType,
      performanceTier: 'SSS',
      accuracyRequirement: 100,
      questionCountRequirement: 100,
      speedRequirement: 2,
    },
  ]
}

// Test Achievement Definitions
export const TEST_ACHIEVEMENTS: Achievement[] = [
  // Addition Tests
  ...createTestAchievements('addition-1digit', '1-Digit Addition'),
  ...createTestAchievements('addition-2digit', '2-Digit Addition'),
  ...createTestAchievements('addition-3digit', '3-Digit Addition'),
  // Subtraction Tests
  ...createTestAchievements('subtraction-1digit', '1-Digit Subtraction'),
  ...createTestAchievements('subtraction-2digit', '2-Digit Subtraction'),
  ...createTestAchievements('subtraction-3digit', '3-Digit Subtraction'),
  // Multiplication Tables (×2 through ×12)
  ...createTestAchievements('multiplication-2', 'Times Table ×2'),
  ...createTestAchievements('multiplication-3', 'Times Table ×3'),
  ...createTestAchievements('multiplication-4', 'Times Table ×4'),
  ...createTestAchievements('multiplication-5', 'Times Table ×5'),
  ...createTestAchievements('multiplication-6', 'Times Table ×6'),
  ...createTestAchievements('multiplication-7', 'Times Table ×7'),
  ...createTestAchievements('multiplication-8', 'Times Table ×8'),
  ...createTestAchievements('multiplication-9', 'Times Table ×9'),
  ...createTestAchievements('multiplication-10', 'Times Table ×10'),
  ...createTestAchievements('multiplication-11', 'Times Table ×11'),
  ...createTestAchievements('multiplication-12', 'Times Table ×12'),
  // Multi-digit Multiplication
  ...createTestAchievements('multiplication-2digit', '2-Digit Multiplication'),
  ...createTestAchievements('multiplication-3digit', '3-Digit Multiplication'),
  // Division Tests
  ...createTestAchievements('division-1digit', '1-Digit Division'),
  ...createTestAchievements('division-2digit', '2-Digit Division'),
  ...createTestAchievements('division-3digit', '3-Digit Division'),
]

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

