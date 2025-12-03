/**
 * Maps backend achievement codes to frontend achievement IDs
 * This mapping connects backend achievement codes (like "addition-basics-bronze")
 * to frontend achievement IDs (like test achievement IDs or milestone IDs)
 * 
 * Updated for Phase 10: Unified tier system (Bronze through Champion)
 * All achievements are now tiered - no base codes like "addition-basics"
 */

export type AchievementCodeMapping = {
  [backendCode: string]: string | string[] // Frontend ID(s) - can be array for multiple matches
}

/**
 * Maps backend achievement codes to frontend achievement IDs
 * 
 * Backend codes are like: "addition-basics-bronze", "addition-1digit-bronze", etc.
 * Frontend IDs are like: "addition-1digit-b", "s1", "m1", etc.
 * 
 * Note: Backend now uses metal/prestige tiers (bronze, silver, gold, etc.)
 * Frontend still uses old tier system (b, a, s, ss, sss) for display
 * Mapping: bronze->b, silver->a, gold->s, platinum->ss, diamond->sss
 * All achievements are tiered - no base codes without tier suffixes
 */
export const ACHIEVEMENT_CODE_TO_FRONTEND_ID: AchievementCodeMapping = {
  // {operation}-basics achievements removed - they're redundant and covered by test achievements
  // All level progression now uses test achievements directly
  
  // Milestone achievements
  'first-steps': ['s1'], // First question answered
  'first-victory': ['m1'], // First session completed
  'perfect-streak-bronze': ['m2'], // 3 consecutive perfect sessions
  'perfect-streak-silver': ['m3'], // 5 consecutive perfect sessions
  'perfect-streak-gold': ['m4'], // 10 consecutive perfect sessions
  'week-warrior-bronze': ['s2'], // 7 day streak
  'week-warrior-silver': ['s3'], // 14 day streak
  'week-warrior-gold': ['s4'], // 30 day streak
  'question-master-bronze': ['s5'], // 100 questions
  'question-master-silver': ['s6'], // 500 questions
  'question-master-gold': ['s7'], // 1000 questions
  'speed-demon-bronze': ['s8'], // Average <5s per question
  'speed-demon-silver': ['s9'], // Average <4s per question
  'speed-demon-gold': ['s10'], // Average <3s per question
  
  // Test achievements with new tier system
  // Backend: {test-type}-{tier} -> Frontend: {test-type}-{old-tier}
  // Tier mapping: bronze->b, silver->a, gold->s, platinum->ss, diamond->sss
  'addition-1digit-bronze': ['addition-1digit-b'],
  'addition-1digit-silver': ['addition-1digit-a'],
  'addition-1digit-gold': ['addition-1digit-s'],
  'addition-1digit-platinum': ['addition-1digit-ss'],
  'addition-1digit-diamond': ['addition-1digit-sss'],
  
  // Multiplication test achievements
  // Backend uses "multiplication-by-N" format, frontend uses "multiplication-N"
  'multiplication-by-2-silver': ['multiplication-2-a'],
  'multiplication-by-3-silver': ['multiplication-3-a'],
  'multiplication-by-4-silver': ['multiplication-4-a'],
  'multiplication-by-5-silver': ['multiplication-5-a'],
  'multiplication-by-6-silver': ['multiplication-6-a'],
  'multiplication-by-7-silver': ['multiplication-7-a'],
  'multiplication-by-8-silver': ['multiplication-8-a'],
  'multiplication-by-9-silver': ['multiplication-9-a'],
  'multiplication-by-10-silver': ['multiplication-10-a'],
  'multiplication-by-11-silver': ['multiplication-11-a'],
  'multiplication-by-12-silver': ['multiplication-12-a'],
  
  // Division test achievements
  // Backend uses "division-by-N" format, frontend uses "division-1digit" for single digit
  'division-by-2-silver': ['division-1digit-a'],
  'division-by-3-silver': ['division-1digit-a'],
  'division-by-4-silver': ['division-1digit-a'],
  'division-by-5-silver': ['division-1digit-a'],
  'division-by-6-silver': ['division-1digit-a'],
  'division-by-7-silver': ['division-1digit-a'],
  'division-by-8-silver': ['division-1digit-a'],
  'division-by-9-silver': ['division-1digit-a'],
  'division-by-10-silver': ['division-1digit-a'],
  'division-by-11-silver': ['division-1digit-a'],
  'division-by-12-silver': ['division-1digit-a'],
  
  // Legacy mappings (kept for backward compatibility with old achievements in database)
  'subtraction-intro': ['subtraction-1digit-b', 'subtraction-1digit-a', 'subtraction-1digit-s'],
  'mixed-addition': ['addition-2digit-b', 'addition-2digit-a', 'addition-2digit-s'],
  'mixed-subtraction': ['subtraction-2digit-b', 'subtraction-2digit-a', 'subtraction-2digit-s'],
  'double-addition': ['addition-2digit-b', 'addition-2digit-a', 'addition-2digit-s'],
  'double-subtraction': ['subtraction-2digit-b', 'subtraction-2digit-a', 'subtraction-2digit-s'],
  'triple-addition': ['addition-3digit-b', 'addition-3digit-a', 'addition-3digit-s'],
  'triple-subtraction': ['subtraction-3digit-b', 'subtraction-3digit-a', 'subtraction-3digit-s'],
  'multiplication-easy': ['multiplication-2digit-b', 'multiplication-2digit-a', 'multiplication-2digit-s'],
  'multiplication-work': ['multiplication-2digit-b', 'multiplication-2digit-a', 'multiplication-2digit-s'],
  'multiplication-triple': ['multiplication-3digit-b', 'multiplication-3digit-a', 'multiplication-3digit-s'],
  'division-remainder': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'],
  'division-double-remainder': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'],
  'division-fraction': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'],
  'division-double-fraction': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'],
  'division-triple-fraction': ['division-3digit-b', 'division-3digit-a', 'division-3digit-s'],
  'division-decimal': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'],
  'division-double-decimal': ['division-3digit-b', 'division-3digit-a', 'division-3digit-s'],
}

/**
 * Reverse mapping: frontend achievement ID to backend achievement codes
 * Useful for checking if a frontend achievement satisfies a backend requirement
 */
export const FRONTEND_ID_TO_ACHIEVEMENT_CODES: Record<string, string[]> = {}

// Build reverse mapping
Object.entries(ACHIEVEMENT_CODE_TO_FRONTEND_ID).forEach(([code, idOrIds]) => {
  const ids = Array.isArray(idOrIds) ? idOrIds : [idOrIds]
  ids.forEach((id) => {
    if (!FRONTEND_ID_TO_ACHIEVEMENT_CODES[id]) {
      FRONTEND_ID_TO_ACHIEVEMENT_CODES[id] = []
    }
    FRONTEND_ID_TO_ACHIEVEMENT_CODES[id].push(code)
  })
})

/**
 * Check if a frontend achievement ID satisfies a backend achievement code requirement
 */
export const doesAchievementSatisfyRequirement = (
  frontendAchievementId: string,
  backendAchievementCode: string
): boolean => {
  const mappedIds = ACHIEVEMENT_CODE_TO_FRONTEND_ID[backendAchievementCode]
  if (!mappedIds) return false
  
  const ids = Array.isArray(mappedIds) ? mappedIds : [mappedIds]
  return ids.includes(frontendAchievementId)
}

/**
 * Get all backend achievement codes that a frontend achievement ID satisfies
 */
export const getBackendCodesForFrontendId = (frontendAchievementId: string): string[] => {
  return FRONTEND_ID_TO_ACHIEVEMENT_CODES[frontendAchievementId] || []
}
