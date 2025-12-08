/** Utility functions for mapping backend test data to frontend format. */

import type { TestDefinition } from '../../../lib/tests/testDefinitions'

// New metal/prestige tier system
export type NewTier = 'Bronze' | 'Silver' | 'Gold' | 'Platinum' | 'Diamond' | 'Master' | 'Grandmaster' | 'Legendary' | 'Mythic' | 'Divine' | 'Champion'
export type OldTier = 'B' | 'A' | 'S' | 'SS' | 'SSS'
export type Tier = NewTier | OldTier

// Old to New tier mapping
const OLD_TO_NEW_TIER: Record<OldTier, NewTier> = {
  'B': 'Bronze',
  'A': 'Silver',
  'S': 'Gold',
  'SS': 'Platinum',
  'SSS': 'Diamond',
}

// New tier hierarchy (for comparison/sorting)
const TIER_HIERARCHY: Record<NewTier, number> = {
  'Bronze': 1,
  'Silver': 2,
  'Gold': 3,
  'Platinum': 4,
  'Diamond': 5,
  'Master': 6,
  'Grandmaster': 7,
  'Legendary': 8,
  'Mythic': 9,
  'Divine': 10,
  'Champion': 11,
}

/**
 * Map old tier (B/A/S/SS/SSS) to new tier system (Bronze/Silver/Gold/Platinum/Diamond/...)
 */
export function mapOldTierToNew(oldTier: OldTier | string): NewTier {
  if (oldTier in OLD_TO_NEW_TIER) {
    return OLD_TO_NEW_TIER[oldTier as OldTier]
  }
  // If already a new tier, return as-is (case-insensitive)
  const normalized = oldTier.charAt(0).toUpperCase() + oldTier.slice(1).toLowerCase()
  if (normalized in TIER_HIERARCHY) {
    return normalized as NewTier
  }
  // Default to Bronze if unknown
  return 'Bronze'
}

/**
 * Get tier hierarchy value for comparison
 */
export function getTierHierarchy(tier: Tier | string): number {
  const newTier = mapOldTierToNew(tier)
  return TIER_HIERARCHY[newTier] || 0
}

/**
 * Compare two tiers - returns positive if tier1 > tier2, negative if tier1 < tier2, 0 if equal
 */
export function compareTiers(tier1: Tier | string, tier2: Tier | string): number {
  return getTierHierarchy(tier2) - getTierHierarchy(tier1)
}

export interface BackendTestDefinition {
  test_type: string
  operation: string
  level_requirement: number
  question_count: number
  constraints?: Record<string, unknown>
  display_name?: string
  is_legacy?: boolean
  unlock_requirements?: {
    type: string
    achievement_code?: string
    achievement_codes?: string[]
    quantity: number
    level?: number
    min_accuracy?: number
    operation?: string
    metadata_filters?: Record<string, Record<string, any>>  // Maps achievement code to metadata filter
  }
  unlock_status?: {
    is_unlocked: boolean
    requirements_met: number
    requirements_total: number
    unlock_requirements?: {
      type: string
      achievement_code?: string
      achievement_codes?: string[]
      quantity: number
      level?: number
      min_accuracy?: number
      operation?: string
      metadata_filters?: Record<string, Record<string, any>>
    }
    reason?: string
  }
}

export interface BackendTestAttempt {
  attempt_id: number
  user_id: number
  level: number
  test_type: string
  score: number
  accuracy: number
  avg_time_per_question_ms: number | null
  total_duration_ms: number | null
  passed: boolean
  attempted_at: string | null
  tier: string
}

export interface BackendTestAttemptDetail extends BackendTestAttempt {
  questions: Array<{
    question_id: number
    prompt: string
    operation: string
    operand1: number
    operand2: number
    correct_answer: string
    user_answer: string
    is_correct: boolean
    time_taken_ms: number
    answered_at: string | null
  }>
}

export interface FrontendTest extends TestDefinition {
  isLocked: boolean
  bestResult?: {
    tier: NewTier
    accuracy: number
    attempted_at: string
  }
  attemptCount: number
  unlockRequirements?: {
    achievementCode?: string  // Single code (backward compatible)
    achievementCodes?: string[]  // Multiple codes (new format)
    quantity: number
    level?: number
    minAccuracy?: number
    operation?: string
    metadataFilters?: Record<string, Record<string, any>>  // Maps achievement code to metadata filter (e.g., {"level-master-bronze": {"level": 1}})
  }
  unlockProgress?: {
    met: number
    total: number
  }
}

export interface FrontendTestAttempt {
  attempt_id: number
  accuracy: number
  avg_time_per_question_ms: number | null
  tier: 'B' | 'A' | 'S' | 'SS' | 'SSS'
  passed: boolean
  attempted_at: string | null
  question_count?: number
}

export interface FrontendTestAttemptDetail extends FrontendTestAttempt {
  questions: Array<{
    question_id: number
    prompt: string
    correct_answer: string
    user_answer: string
    is_correct: boolean
    time_taken_ms: number
    answered_at: string | null
  }>
}

/**
 * Map backend test definition to frontend format.
 */
export function mapTestDefinitionToFrontend(
  backendTest: BackendTestDefinition,
  userLevel: number,
  userAttempts: BackendTestAttempt[] = []
): FrontendTest {
  // Determine if test is locked
  // Priority: unlock_status (new system) > level_requirement (backward compatibility)
  let isLocked: boolean
  let unlockRequirements: FrontendTest['unlockRequirements'] | undefined
  let unlockProgress: FrontendTest['unlockProgress'] | undefined

  if (backendTest.unlock_status) {
    // New achievement-based unlock system
    isLocked = !backendTest.unlock_status.is_unlocked
    unlockProgress = {
      met: backendTest.unlock_status.requirements_met,
      total: backendTest.unlock_status.requirements_total,
    }
    
    // Map unlock_requirements if available
    if (backendTest.unlock_requirements) {
      unlockRequirements = {
        achievementCode: backendTest.unlock_requirements.achievement_code,
        achievementCodes: backendTest.unlock_requirements.achievement_codes,
        quantity: backendTest.unlock_requirements.quantity,
        level: backendTest.unlock_requirements.level,
        minAccuracy: backendTest.unlock_requirements.min_accuracy,
        operation: backendTest.unlock_requirements.operation,
        metadataFilters: backendTest.unlock_requirements.metadata_filters,
      }
    } else if (backendTest.unlock_status?.unlock_requirements) {
      // Fallback to unlock_status.unlock_requirements
      unlockRequirements = {
        achievementCode: backendTest.unlock_status.unlock_requirements.achievement_code,
        achievementCodes: backendTest.unlock_status.unlock_requirements.achievement_codes,
        quantity: backendTest.unlock_status.unlock_requirements.quantity,
        level: backendTest.unlock_status.unlock_requirements.level,
        minAccuracy: backendTest.unlock_status.unlock_requirements.min_accuracy,
        operation: backendTest.unlock_status.unlock_requirements.operation,
        metadataFilters: backendTest.unlock_status.unlock_requirements.metadata_filters,
      }
    }
  } else {
    // Backward compatibility: level-based check
    isLocked = userLevel < backendTest.level_requirement
  }

  const testAttempts = userAttempts.filter(attempt => attempt.test_type === backendTest.test_type)
  
  // Find best result (highest tier)
  let bestResult: FrontendTest['bestResult'] | undefined
  if (testAttempts.length > 0) {
    const sortedAttempts = [...testAttempts].sort((a, b) => {
      // Use tier hierarchy for comparison
      const tierComparison = compareTiers(b.tier, a.tier)
      if (tierComparison !== 0) return tierComparison
      return b.accuracy - a.accuracy
    })
    
    const best = sortedAttempts[0]
    bestResult = {
      tier: mapOldTierToNew(best.tier),
      accuracy: best.accuracy,
      attempted_at: best.attempted_at || '',
    }
  }
  
  return {
    test_type: backendTest.test_type,
    display_name: backendTest.display_name || backendTest.test_type.replace(/-/g, ' ').replace(/_/g, ' '),
    operation: backendTest.operation,
    level_requirement: backendTest.level_requirement,
    question_count: backendTest.question_count,
    constraints: backendTest.constraints,
    is_legacy: backendTest.is_legacy || false,
    isLocked,
    bestResult,
    attemptCount: testAttempts.length,
    unlockRequirements,
    unlockProgress,
  }
}

/**
 * Get test discovery status based on user level.
 */
export function getTestDiscoveryStatus(
  test: TestDefinition | FrontendTest,
  userLevel: number
): 'locked' | 'unlocked' | 'attempted' {
  if (userLevel < test.level_requirement) {
    return 'locked'
  }
  
  if ('attemptCount' in test && test.attemptCount > 0) {
    return 'attempted'
  }
  
  return 'unlocked'
}

/**
 * Get best test result from attempts.
 */
export function getTestBestResult(
  attempts: BackendTestAttempt[]
): FrontendTest['bestResult'] | undefined {
  if (attempts.length === 0) {
    return undefined
  }
  
  const sortedAttempts = [...attempts].sort((a, b) => {
    // Use tier hierarchy for comparison
    const tierComparison = compareTiers(b.tier, a.tier)
    if (tierComparison !== 0) return tierComparison
    return b.accuracy - a.accuracy
  })
  
  const best = sortedAttempts[0]
  return {
    tier: mapOldTierToNew(best.tier),
    accuracy: best.accuracy,
    attempted_at: best.attempted_at || '',
  }
}

/**
 * Calculate test tier from accuracy, speed, and question count.
 */
export function calculateTestTier(
  accuracy: number,
  avgTimePerQuestionMs: number | null,
  questionCount: number | null
): 'B' | 'A' | 'S' | 'SS' | 'SSS' {
  // Not 100% accurate = B tier
  if (accuracy < 100) {
    return 'B'
  }
  
  // 100% accuracy required for higher tiers
  if (questionCount === null || questionCount === undefined) {
    // Use time-based tiering if question count not available
    if (avgTimePerQuestionMs === null) {
      return 'B'
    }
    const avgTimeSeconds = avgTimePerQuestionMs / 1000
    if (avgTimeSeconds <= 3) return 'SSS'
    if (avgTimeSeconds <= 4) return 'SS'
    if (avgTimeSeconds <= 6) return 'S'
    return 'A'
  }
  
  // Tier calculation with question count
  if (questionCount < 30) {
    return 'A' // 100% accuracy, <30 questions
  }
  
  if (questionCount >= 90) {
    // 90+ questions
    if (avgTimePerQuestionMs === null) {
      return 'B'
    }
    const avgTimeSeconds = avgTimePerQuestionMs / 1000
    if (avgTimeSeconds <= 3) {
      return 'SSS'
    }
    return 'SS'
  }
  
  // 31-89 questions
  if (avgTimePerQuestionMs === null) {
    return 'B'
  }
  
  const avgTimeSeconds = avgTimePerQuestionMs / 1000
  
  if (questionCount <= 59) {
    // 31-59 questions
    if (avgTimeSeconds <= 6) {
      return 'S'
    }
    return 'B'
  } else {
    // 60-89 questions
    if (avgTimeSeconds <= 4) {
      return 'SS'
    }
    return 'S'
  }
}

/**
 * Map backend test attempt to frontend format.
 */
export function mapTestAttemptToFrontend(
  backendAttempt: BackendTestAttempt
): FrontendTestAttempt {
  return {
    attempt_id: backendAttempt.attempt_id,
    accuracy: backendAttempt.accuracy,
    avg_time_per_question_ms: backendAttempt.avg_time_per_question_ms,
    tier: backendAttempt.tier as 'B' | 'A' | 'S' | 'SS' | 'SSS',
    passed: backendAttempt.passed,
    attempted_at: backendAttempt.attempted_at,
  }
}

/**
 * Map backend test attempt detail to frontend format.
 */
export function mapTestAttemptDetailToFrontend(
  backendDetail: BackendTestAttemptDetail
): FrontendTestAttemptDetail {
  return {
    attempt_id: backendDetail.attempt_id,
    accuracy: backendDetail.accuracy,
    avg_time_per_question_ms: backendDetail.avg_time_per_question_ms,
    tier: backendDetail.tier as 'B' | 'A' | 'S' | 'SS' | 'SSS',
    passed: backendDetail.passed,
    attempted_at: backendDetail.attempted_at,
    question_count: backendDetail.questions.length,
    questions: backendDetail.questions.map(q => ({
      question_id: q.question_id,
      prompt: q.prompt,
      correct_answer: q.correct_answer,
      user_answer: q.user_answer,
      is_correct: q.is_correct,
      time_taken_ms: q.time_taken_ms,
      answered_at: q.answered_at,
    })),
  }
}

