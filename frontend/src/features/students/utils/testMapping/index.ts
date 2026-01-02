/** Utility functions for mapping backend test data to frontend format. */

import type { BackendTestDefinition, BackendTestAttempt } from './types'
import type { FrontendTest } from './types'
import { mapOldTierToNew, compareTiers } from './tierUtils'
import { getTestBestResult } from './testConverters'

// Re-export types and utilities
export type { NewTier, OldTier, Tier } from './tierUtils'
export type {
  BackendTestDefinition,
  BackendTestAttempt,
  BackendTestAttemptDetail,
  FrontendTest,
  FrontendTestAttempt,
  FrontendTestAttemptDetail,
} from './types'
export {
  mapOldTierToNew,
  getTierHierarchy,
  compareTiers,
} from './tierUtils'
export {
  getTestDiscoveryStatus,
  getTestBestResult,
  calculateTestTier,
  mapTestAttemptToFrontend,
  mapTestAttemptDetailToFrontend,
} from './testConverters'

/**
 * Map backend test definition to frontend format.
 */
export function mapTestDefinitionToFrontend(
  backendTest: BackendTestDefinition,
  userLevel: number,
  userAttempts: BackendTestAttempt[] = []
): FrontendTest {
  // Determine if test is locked
  // Tests are unlocked by default unless unlock_status indicates otherwise
  let isLocked: boolean = false
  let unlockRequirements: FrontendTest['unlockRequirements'] | undefined
  let unlockProgress: FrontendTest['unlockProgress'] | undefined

  if (backendTest.unlock_status) {
    // Achievement-based unlock system
    isLocked = !backendTest.unlock_status.is_unlocked
    unlockProgress = {
      met: backendTest.unlock_status.requirements_met,
      total: backendTest.unlock_status.requirements_total,
    }
    
    // Map unlock_requirements if available
    if (backendTest.unlock_requirements) {
      unlockRequirements = {
        achievementCode: backendTest.unlock_requirements.achievement_code,
        achievementCodes: backendTest.unlock_requirements.achievement_codes,
        quantity: backendTest.unlock_requirements.quantity,
        minAccuracy: backendTest.unlock_requirements.min_accuracy,
        operation: backendTest.unlock_requirements.operation,
        metadataFilters: backendTest.unlock_requirements.metadata_filters,
      }
    } else if (backendTest.unlock_status?.unlock_requirements) {
      // Fallback to unlock_status.unlock_requirements
      unlockRequirements = {
        achievementCode: backendTest.unlock_status.unlock_requirements.achievement_code,
        achievementCodes: backendTest.unlock_status.unlock_requirements.achievement_codes,
        quantity: backendTest.unlock_status.unlock_requirements.quantity,
        minAccuracy: backendTest.unlock_status.unlock_requirements.min_accuracy,
        operation: backendTest.unlock_status.unlock_requirements.operation,
        metadataFilters: backendTest.unlock_status.unlock_requirements.metadata_filters,
      }
    }
  }

  const testAttempts = userAttempts.filter(attempt => attempt.test_type === backendTest.test_type)
  
  // Find best result (highest tier)
  const bestResult = getTestBestResult(testAttempts)
  
  return {
    test_type: backendTest.test_type,
    display_name: backendTest.display_name || backendTest.test_type.replace(/-/g, ' ').replace(/_/g, ' '),
    operation: backendTest.operation,
    level_requirement: backendTest.level_requirement, // Kept for backward compatibility but not used for gating
    question_count: backendTest.question_count,
    constraints: backendTest.constraints,
    isLocked,
    bestResult,
    attemptCount: testAttempts.length,
    unlockRequirements,
    unlockProgress,
  }
}





