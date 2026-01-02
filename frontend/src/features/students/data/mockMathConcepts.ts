/**
 * Mock math concept data for testing the force graph
 */

import type { MathConcept } from './mathConcepts'

export const mockMathConcepts: MathConcept[] = [
  {
    id: 'concept-c_add_1s',
    conceptId: 'c_add_1s',
    displayName: 'Single Digit Addition (1s)',
    category: 'Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
    unlockRequirements: [],
    isLocked: false,
    attemptCount: 5,
    bestAccuracy: 0.95,
    lastAttemptedAt: new Date('2024-01-30'),
  },
  {
    id: 'concept-c_add_2s',
    conceptId: 'c_add_2s',
    displayName: 'Single Digit Addition (2s)',
    category: 'Addition',
    operation: 'addition',
    layoutType: 'vertical',
    answerFormat: 'integer',
    unlockRequirements: [],
    isLocked: false,
    attemptCount: 3,
    bestAccuracy: 0.90,
    lastAttemptedAt: new Date('2024-01-31'),
  },
]
