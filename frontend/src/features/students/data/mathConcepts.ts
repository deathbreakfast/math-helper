/**
 * Math Concepts - Free-form math practice concepts that replace sequential leveling.
 * Each concept has independent unlock requirements and can be practiced in any order.
 */

export type MathConceptUnlockRequirement = {
  description: string
  achievementIds?: string[]
  achievementCode?: string
  alternatives?: Array<{
    description: string
    achievementIds: string[]
  }>
  completed: boolean
  progress?: number
  maxProgress?: number
}

export type MathConcept = {
  id: string
  conceptId: string // Stable identifier like "c_level_1"
  displayName: string // User-friendly name like "Basic Single Digit Addition"
  legacyLevel: number // The level number this concept maps to (1:1 for now)
  operation: string // addition, subtraction, multiplication, division
  unlockRequirements: MathConceptUnlockRequirement[]
  isLocked: boolean
  attemptCount: number
  bestAccuracy?: number
  lastAttemptedAt?: Date
}

/**
 * Concept display names mapped by legacy level number
 * These match the names defined in MATH_CONCEPTS.md (Name field, without "Level" prefix)
 */
const CONCEPT_DISPLAY_NAMES: Record<number, string> = {
  1: 'Basic Single Digit Addition',
  2: 'Addition with Zero (Adding 0)',
  3: 'Basic Single Digit Subtraction',
  4: 'Subtraction with Zero (Subtracting 0)',
  5: 'Single and Two Digit Addition',
  6: 'Single and Two Digit Subtraction',
  7: 'Two Digit Addition',
  8: 'Two Digit Subtraction',
  9: 'Subtraction with Borrowing (Small Numbers)',
  10: 'Negative Number Subtraction',
  11: 'Multiplication by 1',
  12: 'Multiplication by 4',
  13: 'Multiplication by 5',
  14: 'Multiplication by 6',
  15: 'Multiplication by 7',
  16: 'Multiplication by 8',
  17: 'Multiplication by 9',
  18: 'Multiplication by 0',
  19: 'Multiplication by 10',
  20: 'Multiplication by 11',
  21: 'Multiplication by 12',
  22: 'Three Digit Addition',
  23: 'Three Digit Subtraction',
  24: 'Two Digit by Single Digit Multiplication (Partial Products)',
  25: 'Two Digit by Two Digit Multiplication (Partial Products)',
  26: 'Division by 1',
  27: 'Division by 2',
  28: 'Division by 3',
  29: 'Division by 4',
  30: 'Division by 5',
  31: 'Division by 6',
  32: 'Division by 7',
  33: 'Division by 8',
  34: 'Division by 9',
  35: 'Division by 10',
  36: 'Division by 11',
  37: 'Division by 0 (Special Case)',
  38: 'Division by 10 (Repeated)',
  39: 'Division with Remainders (Single Digit Divisors)',
  40: 'Division with Remainders (Two Digit Dividends)',
  41: 'Division with Fractional Answers (Single Digit Divisors)',
  42: 'Division with Fractional Answers (Two Digit Dividends)',
  43: 'Three Digit by Two Digit Multiplication (Partial Products)',
  44: 'Division with Fractional Answers (Three Digit Dividends)',
  45: 'Division with Decimal Answers (Single Digit Divisors)',
}

/**
 * Generate display name from level config
 * Uses descriptive names from CONCEPT_DISPLAY_NAMES mapping (no "Level" prefix)
 */
function generateDisplayName(level: number, operation: string): string {
  // Use the descriptive name from the mapping if available
  if (CONCEPT_DISPLAY_NAMES[level]) {
    return CONCEPT_DISPLAY_NAMES[level]
  }
  
  // Fallback to operation name only (no "Level" prefix)
  const operationNames: Record<string, string> = {
    addition: 'Addition',
    subtraction: 'Subtraction',
    multiplication: 'Multiplication',
    division: 'Division',
  }
  
  return operationNames[operation] || operation
}

/**
 * Create a math concept from a level number
 * This is a 1:1 mapping initially - each level becomes a concept
 */
export function createConceptFromLevel(
  level: number,
  operation: string,
  unlockRequirements: MathConceptUnlockRequirement[] = [],
  isLocked: boolean = false,
  attemptCount: number = 0
): MathConcept {
  return {
    id: `concept-${level}`,
    conceptId: `c_level_${level}`,
    displayName: generateDisplayName(level, operation),
    legacyLevel: level,
    operation,
    unlockRequirements,
    isLocked,
    attemptCount,
  }
}

/**
 * Get all math concepts (1:1 with levels 1-45 for now)
 * This will be replaced with a proper data source later
 */
export function getAllMathConcepts(): MathConcept[] {
  // For now, return placeholder concepts for levels 1-45
  // In the future, this should read from a config file or API
  const concepts: MathConcept[] = []
  
  // Basic mapping: levels 1-4 are addition/subtraction, then it varies
  // This is a simplified version - should be enhanced to read from level config
  const levelOperations: Record<number, string> = {
    1: 'addition',
    2: 'addition',
    3: 'subtraction',
    4: 'subtraction',
  }
  
  for (let level = 1; level <= 45; level++) {
    const operation = levelOperations[level] || 
      (level <= 20 ? 'addition' : level <= 30 ? 'subtraction' : level <= 40 ? 'multiplication' : 'division')
    concepts.push(createConceptFromLevel(level, operation))
  }
  
  return concepts
}
