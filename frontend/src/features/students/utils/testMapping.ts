/** Utility functions for mapping backend test data to frontend format. */

import type { TestDefinition } from '../../lib/tests/testDefinitions'

export interface BackendTestDefinition {
  test_type: string
  operation: string
  level_requirement: number
  question_count: number
  constraints?: Record<string, unknown>
  display_name?: string
  is_legacy?: boolean
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
    tier: 'B' | 'A' | 'S' | 'SS' | 'SSS'
    accuracy: number
    attempted_at: string
  }
  attemptCount: number
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
  const isLocked = userLevel < backendTest.level_requirement
  const testAttempts = userAttempts.filter(attempt => attempt.test_type === backendTest.test_type)
  
  // Find best result (highest tier)
  let bestResult: FrontendTest['bestResult'] | undefined
  if (testAttempts.length > 0) {
    const sortedAttempts = [...testAttempts].sort((a, b) => {
      const tierOrder = { 'SSS': 5, 'SS': 4, 'S': 3, 'A': 2, 'B': 1 }
      const aTier = (tierOrder[a.tier as keyof typeof tierOrder] || 0) as number
      const bTier = (tierOrder[b.tier as keyof typeof tierOrder] || 0) as number
      if (aTier !== bTier) return bTier - aTier
      return b.accuracy - a.accuracy
    })
    
    const best = sortedAttempts[0]
    bestResult = {
      tier: best.tier as 'B' | 'A' | 'S' | 'SS' | 'SSS',
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
    const tierOrder = { 'SSS': 5, 'SS': 4, 'S': 3, 'A': 2, 'B': 1 }
    const aTier = (tierOrder[a.tier as keyof typeof tierOrder] || 0) as number
    const bTier = (tierOrder[b.tier as keyof typeof tierOrder] || 0) as number
    if (aTier !== bTier) return bTier - aTier
    return b.accuracy - a.accuracy
  })
  
  const best = sortedAttempts[0]
  return {
    tier: best.tier as 'B' | 'A' | 'S' | 'SS' | 'SSS',
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

