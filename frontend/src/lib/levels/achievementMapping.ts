/**
 * Maps backend achievement codes to frontend achievement IDs
 * This mapping connects backend achievement codes (like "addition-basics")
 * to frontend achievement IDs (like test achievement IDs or milestone IDs)
 */

export type AchievementCodeMapping = {
  [backendCode: string]: string | string[] // Frontend ID(s) - can be array for multiple matches
}

/**
 * Maps backend achievement codes to frontend achievement IDs
 * 
 * Backend codes are like: "addition-basics", "multiply-by-two", etc.
 * Frontend IDs are like: "addition-1digit-b", "s1", "m1", etc.
 */
export const ACHIEVEMENT_CODE_TO_FRONTEND_ID: AchievementCodeMapping = {
  // Level progression achievements map to test achievements
  // Note: Any tier (b/a/s/ss/sss) satisfies the requirement
  'addition-basics': ['addition-1digit-b', 'addition-1digit-a', 'addition-1digit-s'], // Level 2 requirement
  'subtraction-intro': ['subtraction-1digit-b', 'subtraction-1digit-a', 'subtraction-1digit-s'], // Level 3 requirement
  'subtraction-basics': ['subtraction-1digit-b', 'subtraction-1digit-a', 'subtraction-1digit-s'], // Level 4 requirement
  'mixed-addition': ['addition-2digit-b', 'addition-2digit-a', 'addition-2digit-s'], // Level 5 requirement
  'mixed-subtraction': ['subtraction-2digit-b', 'subtraction-2digit-a', 'subtraction-2digit-s'], // Level 6 requirement
  'double-addition': ['addition-2digit-b', 'addition-2digit-a', 'addition-2digit-s'], // Level 7 requirement
  'double-subtraction': ['subtraction-2digit-b', 'subtraction-2digit-a', 'subtraction-2digit-s'], // Level 8 requirement
  
  // Multiplication table achievements
  // Note: Frontend uses test achievements like "multiplication-2-b", "multiplication-3-b", etc.
  // Backend codes like "multiply-by-two" should map to any tier (b/a/s/ss/sss) of that test
  'multiply-by-one': ['multiplication-2-b', 'multiplication-2-a', 'multiplication-2-s'], // Level 9 requirement (use ×2 as proxy)
  'multiply-by-two': ['multiplication-2-b', 'multiplication-2-a', 'multiplication-2-s'], // Level 10 requirement
  'multiply-by-three': ['multiplication-3-b', 'multiplication-3-a', 'multiplication-3-s'], // Level 11 requirement
  'multiply-by-four': ['multiplication-4-b', 'multiplication-4-a', 'multiplication-4-s'], // Level 12 requirement
  'multiply-by-five': ['multiplication-5-b', 'multiplication-5-a', 'multiplication-5-s'], // Level 13 requirement
  'multiply-by-six': ['multiplication-6-b', 'multiplication-6-a', 'multiplication-6-s'], // Level 14 requirement
  'multiply-by-seven': ['multiplication-7-b', 'multiplication-7-a', 'multiplication-7-s'], // Level 15 requirement
  'multiply-by-eight': ['multiplication-8-b', 'multiplication-8-a', 'multiplication-8-s'], // Level 16 requirement
  'multiply-by-nine': ['multiplication-9-b', 'multiplication-9-a', 'multiplication-9-s'], // Level 17 requirement
  'multiply-by-zero': ['multiplication-2-b', 'multiplication-2-a', 'multiplication-2-s'], // Level 18 requirement (use ×2 as proxy)
  'multiply-by-ten': ['multiplication-10-b', 'multiplication-10-a', 'multiplication-10-s'], // Level 19 requirement
  'multiply-by-eleven': ['multiplication-11-b', 'multiplication-11-a', 'multiplication-11-s'], // Level 20 requirement
  'multiply-by-twelve': ['multiplication-12-b', 'multiplication-12-a', 'multiplication-12-s'], // Level 21 requirement
  
  // Advanced achievements
  'triple-addition': ['addition-3digit-b', 'addition-3digit-a', 'addition-3digit-s'], // Level 22 requirement
  'triple-subtraction': ['subtraction-3digit-b', 'subtraction-3digit-a', 'subtraction-3digit-s'], // Level 23 requirement
  'multiplication-easy': ['multiplication-2digit-b', 'multiplication-2digit-a', 'multiplication-2digit-s'], // Level 24 requirement
  'multiplication-work': ['multiplication-2digit-b', 'multiplication-2digit-a', 'multiplication-2digit-s'], // Level 25 requirement
  
  // Division achievements
  // Note: Division achievements use 1digit/2digit/3digit test types
  'divide-by-one': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 26 requirement
  'divide-by-two': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 27 requirement
  'divide-by-three': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 28 requirement
  'divide-by-four': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 29 requirement
  'divide-by-five': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 30 requirement
  'divide-by-six': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 31 requirement
  'divide-by-seven': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 32 requirement
  'divide-by-eight': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 33 requirement
  'divide-by-nine': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 34 requirement
  'divide-by-ten': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 35 requirement
  'divide-by-eleven': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 36 requirement
  'divide-by-twelve': ['division-1digit-b', 'division-1digit-a', 'division-1digit-s'], // Level 37 requirement
  'division-remainder': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'], // Level 38 requirement
  'division-double-remainder': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'], // Level 39 requirement
  'division-fraction': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'], // Level 40 requirement
  'division-double-fraction': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'], // Level 41 requirement
  'multiplication-triple': ['multiplication-3digit-b', 'multiplication-3digit-a', 'multiplication-3digit-s'], // Level 42 requirement
  'division-triple-fraction': ['division-3digit-b', 'division-3digit-a', 'division-3digit-s'], // Level 43 requirement
  'division-decimal': ['division-2digit-b', 'division-2digit-a', 'division-2digit-s'], // Level 44 requirement
  'division-double-decimal': ['division-3digit-b', 'division-3digit-a', 'division-3digit-s'], // Level 45 requirement
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

