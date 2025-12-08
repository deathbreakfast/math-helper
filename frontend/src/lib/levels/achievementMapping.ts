/**
 * Maps backend achievement codes to frontend achievement IDs
 * This mapping connects backend achievement codes (like "first-steps", "speed-demon-bronze")
 * to frontend achievement IDs (like milestone IDs)
 * 
 * NOTE: Test achievements have been removed. All test-specific achievements are no longer used.
 * The system now uses generic achievements (level-master, lightning-fast, speed-demon) with metadata.
 */

export type AchievementCodeMapping = {
  [backendCode: string]: string | string[] // Frontend ID(s) - can be array for multiple matches
}

/**
 * Maps backend achievement codes to frontend achievement IDs
 * 
 * Backend codes are like: "first-steps", "speed-demon-bronze", "level-master-bronze", etc.
 * Frontend IDs are like: "s1", "m1", "s8", etc.
 * 
 * Test achievements have been removed - the system now uses generic achievements with metadata.
 */
export const ACHIEVEMENT_CODE_TO_FRONTEND_ID: AchievementCodeMapping = {
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
  
  // Note: Test achievements (addition-1digit-bronze, multiplication-by-2-silver, etc.) have been removed.
  // The system now uses generic achievements (level-master, lightning-fast) with metadata for level-specific requirements.
  
  // Legacy mappings (kept for backward compatibility with old achievements in database)
  'master-of-all': ['level-grandmaster'], // Renamed to level-grandmaster
  'level-grandmaster': ['level-grandmaster'], // Level Master (Bronze) on all levels
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
