import type { TestDefinition } from '../../../../lib/tests/testDefinitions'
import type { NewTier } from './tierUtils'

export interface BackendTestDefinition {
  test_type: string
  operation: string
  level_requirement: number
  question_count: number
  constraints?: Record<string, unknown>
  display_name?: string
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





