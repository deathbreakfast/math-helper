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
  // Priority: unlock_status (new system) > level_requirement (backward compatibility)
  let isLocked: boolean
  let unlockRequirements: FrontendTest['unlockRequirements'] | undefined
  let unlockProgress: FrontendTest['unlockProgress'] | undefined

  if (backendTest.unlock_status) {
    // New achievement-based unlock system
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
        level: backendTest.unlock_requirements.level,
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
        level: backendTest.unlock_status.unlock_requirements.level,
        minAccuracy: backendTest.unlock_status.unlock_requirements.min_accuracy,
        operation: backendTest.unlock_status.unlock_requirements.operation,
        metadataFilters: backendTest.unlock_status.unlock_requirements.metadata_filters,
      }
    }
  } else {
    // Backward compatibility: level-based check
    isLocked = userLevel < backendTest.level_requirement
  }

  const testAttempts = userAttempts.filter(attempt => attempt.test_type === backendTest.test_type)
  
  // Find best result (highest tier)
  const bestResult = getTestBestResult(testAttempts)
  
  return {
    test_type: backendTest.test_type,
    display_name: backendTest.display_name || backendTest.test_type.replace(/-/g, ' ').replace(/_/g, ' '),
    operation: backendTest.operation,
    level_requirement: backendTest.level_requirement,
    question_count: backendTest.question_count,
    constraints: backendTest.constraints,
    isLocked,
    bestResult,
    attemptCount: testAttempts.length,
    unlockRequirements,
    unlockProgress,
  }
}




