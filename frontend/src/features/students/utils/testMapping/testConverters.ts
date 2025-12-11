import type { TestDefinition } from '../../../../lib/tests/testDefinitions'
import type { BackendTestAttempt, BackendTestAttemptDetail } from './types'
import type { FrontendTest, FrontendTestAttempt, FrontendTestAttemptDetail } from './types'
import { mapOldTierToNew, compareTiers } from './tierUtils'

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



