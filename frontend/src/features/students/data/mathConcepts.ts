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
  conceptId: string // Stable identifier like "c_concept_001" (new format) or "c_add_1s" (descriptive)
  displayName: string // User-friendly name like "Basic Single Digit Addition"
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

type ConceptConfig = {
  displayName: string
  operation: string
  layoutType: string
  answerFormat: string
}

/**
 * Concept configuration keyed by concept_id.
 * Contains display name, operation, layout type, and answer format for each concept.
 */
const CONCEPT_CONFIG_BY_ID: Record<string, ConceptConfig> = {
  // c_concept_XXX concepts (numbered concepts)
  'c_concept_001': {
    displayName: 'Basic Single Digit Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_003': {
    displayName: 'Basic Single Digit Subtraction',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_005': {
    displayName: 'Single and Two Digit Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_006': {
    displayName: 'Single and Two Digit Subtraction',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_007': {
    displayName: 'Two Digit Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_008': {
    displayName: 'Two Digit Subtraction',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_010': {
    displayName: 'Negative Number Subtraction',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_011': {
    displayName: 'Multiplication by 1',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_012': {
    displayName: 'Multiplication by 4',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_013': {
    displayName: 'Multiplication by 5',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_014': {
    displayName: 'Multiplication by 6',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_015': {
    displayName: 'Multiplication by 7',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_016': {
    displayName: 'Multiplication by 8',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_017': {
    displayName: 'Multiplication by 9',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_018': {
    displayName: 'Multiplication by 0',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_019': {
    displayName: 'Multiplication by 10',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_020': {
    displayName: 'Multiplication by 11',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_021': {
    displayName: 'Multiplication by 12',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_022': {
    displayName: 'Three Digit Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_023': {
    displayName: 'Three Digit Subtraction',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_concept_024': {
    displayName: 'Two Digit by Single Digit Multiplication (Partial Products)',
    operation: 'multiplication',
    layoutType: 'partialProducts',
    answerFormat: 'integer',
  },
  'c_concept_025': {
    displayName: 'Two Digit by Two Digit Multiplication (Partial Products)',
    operation: 'multiplication',
    layoutType: 'partialProducts',
    answerFormat: 'integer',
  },
  'c_concept_026': {
    displayName: 'Division by 1',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_027': {
    displayName: 'Division by 2',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_028': {
    displayName: 'Division by 3',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_029': {
    displayName: 'Division by 4',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_030': {
    displayName: 'Division by 5',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_031': {
    displayName: 'Division by 6',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_032': {
    displayName: 'Division by 7',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_033': {
    displayName: 'Division by 8',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_034': {
    displayName: 'Division by 9',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_035': {
    displayName: 'Division by 10',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_036': {
    displayName: 'Division by 11',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_037': {
    displayName: 'Division by 0 (Special Case)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_038': {
    displayName: 'Division by 10 (Repeated)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'integer',
  },
  'c_concept_039': {
    displayName: 'Division with Remainders (Single Digit Divisors)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'remainder',
  },
  'c_concept_040': {
    displayName: 'Division with Remainders (Two Digit Dividends)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'remainder',
  },
  'c_concept_041': {
    displayName: 'Division with Fractional Answers (Single Digit Divisors)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'fraction',
  },
  'c_concept_042': {
    displayName: 'Division with Fractional Answers (Two Digit Dividends)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'fraction',
  },
  'c_concept_043': {
    displayName: 'Three Digit by Two Digit Multiplication (Partial Products)',
    operation: 'multiplication',
    layoutType: 'partialProducts',
    answerFormat: 'integer',
  },
  'c_concept_044': {
    displayName: 'Division with Fractional Answers (Three Digit Dividends)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'fraction',
  },
  'c_concept_045': {
    displayName: 'Division with Decimal Answers (Single Digit Divisors)',
    operation: 'division',
    layoutType: 'longDivision',
    answerFormat: 'decimal',
  },
  // Descriptive concept IDs
  'c_add_0s': {
    displayName: 'Single Digit Addition (0s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_1s': {
    displayName: 'Single Digit Addition (1s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_2s': {
    displayName: 'Single Digit Addition (2s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_3s': {
    displayName: 'Single Digit Addition (3s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_4s': {
    displayName: 'Single Digit Addition (4s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_5s': {
    displayName: 'Single Digit Addition (5s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_6s': {
    displayName: 'Single Digit Addition (6s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_7s': {
    displayName: 'Single Digit Addition (7s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_8s': {
    displayName: 'Single Digit Addition (8s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_9s': {
    displayName: 'Single Digit Addition (9s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_add_10s': {
    displayName: 'Single Digit Addition (10s)',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_0s': {
    displayName: 'Single Digit Subtraction (0s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_1s': {
    displayName: 'Single Digit Subtraction (1s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_2s': {
    displayName: 'Single Digit Subtraction (2s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_3s': {
    displayName: 'Single Digit Subtraction (3s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_4s': {
    displayName: 'Single Digit Subtraction (4s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_5s': {
    displayName: 'Single Digit Subtraction (5s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_6s': {
    displayName: 'Single Digit Subtraction (6s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_7s': {
    displayName: 'Single Digit Subtraction (7s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_8s': {
    displayName: 'Single Digit Subtraction (8s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_9s': {
    displayName: 'Single Digit Subtraction (9s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_sub_10s': {
    displayName: 'Single Digit Subtraction (10s)',
    operation: 'subtraction',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_mul_2s': {
    displayName: 'Multiplication by 2',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
  'c_mul_3s': {
    displayName: 'Multiplication by 3',
    operation: 'multiplication',
    layoutType: 'vertical',
    answerFormat: 'integer',
  },
}

/**
 * Get display name for a concept by concept_id
 */
export function getConceptDisplayNameByConceptId(conceptId: string | undefined | null): string | null {
  if (!conceptId) return null
  return CONCEPT_CONFIG_BY_ID[conceptId]?.displayName || null
}

/**
 * Create a math concept from a concept_id
 */
function createConceptFromId(
  conceptId: string,
  unlockRequirements: MathConceptUnlockRequirement[] = [],
  isLocked: boolean = false,
  attemptCount: number = 0
): MathConcept | null {
  const config = CONCEPT_CONFIG_BY_ID[conceptId]
  if (!config) return null

  const category = config.operation.charAt(0).toUpperCase() + config.operation.slice(1)
  return {
    id: `concept-${conceptId}`,
    conceptId,
    displayName: config.displayName,
    category,
    operation: config.operation,
    layoutType: config.layoutType,
    answerFormat: config.answerFormat,
    unlockRequirements,
    isLocked,
    attemptCount,
  }
}

/**
 * Get all math concepts
 */
export function getAllMathConcepts(): MathConcept[] {
  const concepts: MathConcept[] = []

  // Get all concept_ids from the config
  const conceptIds = Object.keys(CONCEPT_CONFIG_BY_ID)

  for (const conceptId of conceptIds) {
    const concept = createConceptFromId(conceptId)
    if (concept) {
      concepts.push(concept)
    }
  }

  return concepts
}
