/**
 * Math Concepts - Free-form math practice concepts that replace sequential leveling.
 * Each concept has independent unlock requirements and can be practiced in any order.
 */

import { conceptIdFromLegacyLevel } from '../utils/conceptIdUtils'

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
  conceptId: string // Stable identifier like "c_concept_001" (new format) or "c_add_1s" (descriptive)
  displayName: string // User-friendly name like "Basic Single Digit Addition"
  legacyLevel: number // The level number this concept maps to (1:1 for now) - internal use only
  category: string // Addition, Subtraction, Multiplication, Division
  operation: string // addition, subtraction, multiplication, division
  layoutType?: string // vertical, longDivision, partialProducts, etc.
  answerFormat?: string // integer, remainder, fraction, decimal, mixed
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

const CONCEPT_OPERATION_BY_LEVEL: Record<number, string> = {
  1: 'addition',
  2: 'addition',
  3: 'subtraction',
  4: 'subtraction',
  5: 'addition',
  6: 'subtraction',
  7: 'addition',
  8: 'subtraction',
  9: 'subtraction',
  10: 'subtraction',
  11: 'multiplication',
  12: 'multiplication',
  13: 'multiplication',
  14: 'multiplication',
  15: 'multiplication',
  16: 'multiplication',
  17: 'multiplication',
  18: 'multiplication',
  19: 'multiplication',
  20: 'multiplication',
  21: 'multiplication',
  22: 'addition',
  23: 'subtraction',
  24: 'multiplication',
  25: 'multiplication',
  26: 'division',
  27: 'division',
  28: 'division',
  29: 'division',
  30: 'division',
  31: 'division',
  32: 'division',
  33: 'division',
  34: 'division',
  35: 'division',
  36: 'division',
  37: 'division',
  38: 'division',
  39: 'division',
  40: 'division',
  41: 'division',
  42: 'division',
  43: 'multiplication',
  44: 'division',
  45: 'division',
}

const CONCEPT_LAYOUT_BY_LEVEL: Record<number, string> = {
  // Most arithmetic concepts
  1: 'vertical',
  2: 'vertical',
  3: 'vertical',
  4: 'vertical',
  5: 'vertical',
  6: 'vertical',
  7: 'vertical',
  8: 'vertical',
  9: 'vertical',
  10: 'vertical',
  11: 'vertical',
  12: 'vertical',
  13: 'vertical',
  14: 'vertical',
  15: 'vertical',
  16: 'vertical',
  17: 'vertical',
  18: 'vertical',
  19: 'vertical',
  20: 'vertical',
  21: 'vertical',
  22: 'vertical',
  23: 'vertical',

  // Partial products multiplication concepts
  24: 'partialProducts',
  25: 'partialProducts',
  43: 'partialProducts',

  // Division concepts
  26: 'longDivision',
  27: 'longDivision',
  28: 'longDivision',
  29: 'longDivision',
  30: 'longDivision',
  31: 'longDivision',
  32: 'longDivision',
  33: 'longDivision',
  34: 'longDivision',
  35: 'longDivision',
  36: 'longDivision',
  37: 'longDivision',
  38: 'longDivision',
  39: 'longDivision',
  40: 'longDivision',
  41: 'longDivision',
  42: 'longDivision',
  44: 'longDivision',
  45: 'longDivision',
}

const CONCEPT_ANSWER_FORMAT_BY_LEVEL: Record<number, string> = {
  // Defaults
  1: 'integer',
  2: 'integer',
  3: 'integer',
  4: 'integer',
  5: 'integer',
  6: 'integer',
  7: 'integer',
  8: 'integer',
  9: 'integer',
  10: 'integer',
  11: 'integer',
  12: 'integer',
  13: 'integer',
  14: 'integer',
  15: 'integer',
  16: 'integer',
  17: 'integer',
  18: 'integer',
  19: 'integer',
  20: 'integer',
  21: 'integer',
  22: 'integer',
  23: 'integer',
  24: 'integer',
  25: 'integer',
  26: 'integer',
  27: 'integer',
  28: 'integer',
  29: 'integer',
  30: 'integer',
  31: 'integer',
  32: 'integer',
  33: 'integer',
  34: 'integer',
  35: 'integer',
  36: 'integer',
  37: 'integer',
  38: 'integer',
  // Special answer formats from doc
  39: 'remainder',
  40: 'remainder',
  41: 'fraction',
  42: 'fraction',
  43: 'integer',
  44: 'fraction',
  45: 'decimal',
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
  const category = operation.charAt(0).toUpperCase() + operation.slice(1)
  return {
    id: `concept-${level}`,
    conceptId: conceptIdFromLegacyLevel(level), // Use new format: c_concept_001, c_concept_002, etc.
    displayName: generateDisplayName(level, operation),
    legacyLevel: level, // Keep for internal mapping/backward compatibility
    category,
    operation,
    layoutType: CONCEPT_LAYOUT_BY_LEVEL[level],
    answerFormat: CONCEPT_ANSWER_FORMAT_BY_LEVEL[level],
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
  const concepts: MathConcept[] = []

  for (let level = 1; level <= 45; level++) {
    const operation = CONCEPT_OPERATION_BY_LEVEL[level] || 'addition'
    concepts.push(createConceptFromLevel(level, operation))
  }

  return concepts
}
