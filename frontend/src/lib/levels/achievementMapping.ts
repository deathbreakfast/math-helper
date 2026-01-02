/**
 * Maps backend achievement codes to frontend achievement IDs
 * This mapping connects backend achievement codes (like "first-steps", "speed-demon-bronze")
 * to frontend achievement IDs (like milestone IDs)
 */

export type AchievementCodeMapping = {
  [backendCode: string]: string | string[] // Frontend ID(s) - can be array for multiple matches
}

/**
 * Maps backend achievement codes to frontend achievement IDs
 * 
 * Backend codes are like: "first-steps", "speed-demon-bronze", "math-master-bronze", etc.
 * Frontend IDs are like: "s1", "m1", "s8", etc.
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

  // Legacy mappings (kept for backward compatibility with older achievement codes that may exist in the database).
  'master-of-all': ['math-grandmaster'], // Renamed to math-grandmaster
  'level-grandmaster': ['math-grandmaster'], // Legacy code, maps to math-grandmaster
  'math-grandmaster': ['math-grandmaster'], // Math Master (Bronze) on all descriptive concepts
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
