/** Test definitions with metadata.
 * 
 * This file serves as a baseline of all test definitions including:
 * - Test names and identifiers
 * - Question counts
 * - Level requirements to unlock
 * - Achievements (B-SSS tiers) for each test
 */

export interface TestDefinition {
  test_type: string
  display_name: string
  operation: string
  level_requirement: number
  question_count: number
  constraints?: Record<string, unknown>
  is_legacy?: boolean
}

export interface TestTier {
  tier: 'B' | 'A' | 'S' | 'SS' | 'SSS'
  accuracy: number
  question_count?: number
  max_speed_seconds?: number
}

// Test definitions baseline - matches backend NEW_TEST_DEFINITIONS
// This is a reference document showing all available tests
export const TEST_DEFINITIONS_BASELINE: Record<string, Omit<TestDefinition, 'test_type'>> = {
  // Addition Tests
  'addition-1digit': {
    display_name: '1 Digit Addition',
    operation: 'addition',
    level_requirement: 1,
    question_count: 50,
    constraints: { max_digits: 1 },
  },
  'addition-1digit-zeros': {
    display_name: '1 Digit Addition w/ Zeros',
    operation: 'addition',
    level_requirement: 1,
    question_count: 50,
    constraints: { max_digits: 1, allow_zeros: true },
  },
  'addition-1digit-negative': {
    display_name: '1 Digit Addition w/ Negative Numbers',
    operation: 'addition',
    level_requirement: 1,
    question_count: 50,
    constraints: { max_digits: 1, allow_negative: true },
  },
  'addition-2digit': {
    display_name: '2 Digit Addition',
    operation: 'addition',
    level_requirement: 2,
    question_count: 50,
    constraints: { max_digits: 2 },
  },
  'addition-3digit': {
    display_name: '3 Digit Addition',
    operation: 'addition',
    level_requirement: 8,
    question_count: 40,
    constraints: { max_digits: 3 },
  },
  
  // Subtraction Tests
  'subtraction-1digit': {
    display_name: '1 Digit Subtraction',
    operation: 'subtraction',
    level_requirement: 3,
    question_count: 50,
    constraints: { max_digits: 1 },
  },
  'subtraction-1digit-zeros': {
    display_name: '1 Digit Subtraction w/ Zeros',
    operation: 'subtraction',
    level_requirement: 3,
    question_count: 50,
    constraints: { max_digits: 1, allow_zeros: true },
  },
  'subtraction-1digit-negative': {
    display_name: '1 Digit Subtraction w/ Negative Numbers',
    operation: 'subtraction',
    level_requirement: 3,
    question_count: 50,
    constraints: { max_digits: 1, allow_negative: true },
  },
  'subtraction-2digit': {
    display_name: '2 Digit Subtraction',
    operation: 'subtraction',
    level_requirement: 4,
    question_count: 50,
    constraints: { max_digits: 2 },
  },
  'subtraction-3digit': {
    display_name: '3 Digit Subtraction',
    operation: 'subtraction',
    level_requirement: 23,
    question_count: 40,
    constraints: { max_digits: 3 },
  },
  
  // Mixed Tests
  'basic-math-mixed': {
    display_name: 'Basic Math (Mixed)',
    operation: 'mixed',
    level_requirement: 5,
    question_count: 100,
    constraints: { max_digits: 3, operations: ['addition', 'subtraction'] },
  },
  
  // Multiplication Tests
  'multiplication-by-1': {
    display_name: 'Multiplication by 1',
    operation: 'multiplication',
    level_requirement: 7,
    question_count: 100,
    constraints: { multiplication_table: 1 },
  },
  'multiplication-by-2': {
    display_name: 'Multiplication by 2',
    operation: 'multiplication',
    level_requirement: 9,
    question_count: 100,
    constraints: { multiplication_table: 2 },
  },
  'multiplication-by-3': {
    display_name: 'Multiplication by 3',
    operation: 'multiplication',
    level_requirement: 10,
    question_count: 100,
    constraints: { multiplication_table: 3 },
  },
  'multiplication-by-4': {
    display_name: 'Multiplication by 4',
    operation: 'multiplication',
    level_requirement: 11,
    question_count: 100,
    constraints: { multiplication_table: 4 },
  },
  'multiplication-by-5': {
    display_name: 'Multiplication by 5',
    operation: 'multiplication',
    level_requirement: 12,
    question_count: 100,
    constraints: { multiplication_table: 5 },
  },
  'multiplication-by-6': {
    display_name: 'Multiplication by 6',
    operation: 'multiplication',
    level_requirement: 13,
    question_count: 100,
    constraints: { multiplication_table: 6 },
  },
  'multiplication-by-7': {
    display_name: 'Multiplication by 7',
    operation: 'multiplication',
    level_requirement: 14,
    question_count: 100,
    constraints: { multiplication_table: 7 },
  },
  'multiplication-by-8': {
    display_name: 'Multiplication by 8',
    operation: 'multiplication',
    level_requirement: 15,
    question_count: 100,
    constraints: { multiplication_table: 8 },
  },
  'multiplication-by-9': {
    display_name: 'Multiplication by 9',
    operation: 'multiplication',
    level_requirement: 16,
    question_count: 100,
    constraints: { multiplication_table: 9 },
  },
  'multiplication-by-10': {
    display_name: 'Multiplication by 10',
    operation: 'multiplication',
    level_requirement: 19,
    question_count: 100,
    constraints: { multiplication_table: 10 },
  },
  'multiplication-by-11': {
    display_name: 'Multiplication by 11',
    operation: 'multiplication',
    level_requirement: 20,
    question_count: 100,
    constraints: { multiplication_table: 11 },
  },
  'multiplication-by-12': {
    display_name: 'Multiplication by 12',
    operation: 'multiplication',
    level_requirement: 21,
    question_count: 100,
    constraints: { multiplication_table: 12 },
  },
  'multiplication-2digit': {
    display_name: 'Multiplication Double Digit',
    operation: 'multiplication',
    level_requirement: 24,
    question_count: 50,
    constraints: { multiplication_digits: 2 },
  },
  'multiplication-3digit': {
    display_name: 'Multiplication 3 Digit',
    operation: 'multiplication',
    level_requirement: 25,
    question_count: 40,
    constraints: { multiplication_digits: 3 },
  },
  
  // Division Tests
  'division-by-1': {
    display_name: 'Division by 1',
    operation: 'division',
    level_requirement: 25,
    question_count: 100,
    constraints: { division_table: 1 },
  },
  'division-by-2': {
    display_name: 'Division by 2',
    operation: 'division',
    level_requirement: 26,
    question_count: 100,
    constraints: { division_table: 2 },
  },
  'division-by-3': {
    display_name: 'Division by 3',
    operation: 'division',
    level_requirement: 27,
    question_count: 100,
    constraints: { division_table: 3 },
  },
  'division-by-4': {
    display_name: 'Division by 4',
    operation: 'division',
    level_requirement: 28,
    question_count: 100,
    constraints: { division_table: 4 },
  },
  'division-by-5': {
    display_name: 'Division by 5',
    operation: 'division',
    level_requirement: 29,
    question_count: 100,
    constraints: { division_table: 5 },
  },
  'division-by-6': {
    display_name: 'Division by 6',
    operation: 'division',
    level_requirement: 30,
    question_count: 100,
    constraints: { division_table: 6 },
  },
  'division-by-7': {
    display_name: 'Division by 7',
    operation: 'division',
    level_requirement: 31,
    question_count: 100,
    constraints: { division_table: 7 },
  },
  'division-by-8': {
    display_name: 'Division by 8',
    operation: 'division',
    level_requirement: 32,
    question_count: 100,
    constraints: { division_table: 8 },
  },
  'division-by-9': {
    display_name: 'Division by 9',
    operation: 'division',
    level_requirement: 33,
    question_count: 100,
    constraints: { division_table: 9 },
  },
  'division-by-10': {
    display_name: 'Division by 10',
    operation: 'division',
    level_requirement: 35,
    question_count: 100,
    constraints: { division_table: 10 },
  },
  'division-by-11': {
    display_name: 'Division by 11',
    operation: 'division',
    level_requirement: 36,
    question_count: 100,
    constraints: { division_table: 11 },
  },
  'division-by-12': {
    display_name: 'Division by 12',
    operation: 'division',
    level_requirement: 37,
    question_count: 100,
    constraints: { division_table: 12 },
  },
  'division-no-remainder-single': {
    display_name: 'Division (No Remainder, Single Digit)',
    operation: 'division',
    level_requirement: 38,
    question_count: 50,
    constraints: { division_digits: 1, no_remainder: true },
  },
  'division-remainder': {
    display_name: 'Division (Remainder Format)',
    operation: 'division',
    level_requirement: 39,
    question_count: 50,
    constraints: { answer_format: 'remainder' },
  },
  'division-fraction': {
    display_name: 'Division (Fraction Format)',
    operation: 'division',
    level_requirement: 40,
    question_count: 50,
    constraints: { answer_format: 'fraction' },
  },
  'division-decimal': {
    display_name: 'Division (Decimal Format)',
    operation: 'division',
    level_requirement: 44,
    question_count: 40,
    constraints: { answer_format: 'decimal' },
  },
  'division-long': {
    display_name: 'Long Division',
    operation: 'division',
    level_requirement: 45,
    question_count: 25,
    constraints: { answer_format: 'long_division' },
  },
}

// Tier requirements for achievements (B, A, S, SS, SSS)
// Each test has 5 tier achievements
export const TEST_TIER_REQUIREMENTS: Record<string, TestTier[]> = {
  B: [
    { tier: 'B', accuracy: 0, question_count: 30 }, // Complete test (30+ questions)
  ],
  A: [
    { tier: 'A', accuracy: 100, question_count: 29, max_speed_seconds: undefined }, // 100% accuracy, <30 questions
  ],
  S: [
    { tier: 'S', accuracy: 100, question_count: 59, max_speed_seconds: 6 }, // 100% accuracy, 31-59 questions, <6s/question
  ],
  SS: [
    { tier: 'SS', accuracy: 100, question_count: 90, max_speed_seconds: 4 }, // 100% accuracy, <90 questions, <4s/question
  ],
  SSS: [
    { tier: 'SSS', accuracy: 100, question_count: 90, max_speed_seconds: 3 }, // 100% accuracy, 90+ questions, <3s/question
  ],
}

