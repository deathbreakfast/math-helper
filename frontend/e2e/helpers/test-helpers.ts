/**
 * Test Helpers - Re-exports from organized modules
 * 
 * This file maintains backward compatibility by re-exporting all helpers
 * from the organized module structure. All imports from './helpers/test-helpers'
 * will continue to work without changes.
 */

// Types
export type { TestUser, PracticeElements } from './types/test-types'

// API Helpers - User
export {
  generateTestUserName,
  createTestUser,
  deleteTestUser,
  getUser,
  listUsers,
} from './api/user-api'

// API Helpers - Practice
export {
  startPracticeSessionViaAPI,
  answerQuestionViaAPI,
} from './api/practice-api'

// API Helpers - Test Setup
export {
  setUserLevelDirectly,
  awardAchievements,
  setupTestUserState,
  createTestUserWithState,
  setupUserForLevelUp,
  getLevelUpEligibility,
  getTestEligibility,
  startTestSession,
  createCompletedPracticeSessions,
  createPassedTestAttempt,
} from './api/test-setup-api'

// UI Helpers - Dashboard
export {
  navigateToDashboard,
  waitForDashboardLoad,
  clickUserCard,
  clickStartPractice,
  enterPin,
  clickStartPracticeInModal,
} from './ui/dashboard-helpers'

// UI Helpers - Journey
export {
  openJourneyModal,
  clickJourneyTab,
  navigateToAchievementsTab,
  navigateToLevelsTab,
  navigateToTestsTab,
} from './ui/journey-helpers'

// UI Helpers - Learner Management
export {
  openAddLearnerModal,
  fillLearnerName,
  selectAvatar,
  completeLearnerCreation,
} from './ui/learner-management-helpers'

// UI Helpers - Practice
export {
  getPracticeElements,
  navigateToPractice,
  answerQuestion,
  moveToNextQuestion,
  isSubmitButtonReady,
  completePracticeSession,
  submitPracticeSession,
  getProgressPercent,
  getQuestionText,
  waitForSummaryPage,
} from './ui/practice-helpers'

// Assertion Helpers
export {
  filterAchievementsByCategory,
  getAchievementStatus,
  getLevelRequirementStatus,
} from './assertions/achievement-helpers'

// Utility Functions
import { Page } from '@playwright/test'

/**
 * Wait for an element to be visible with a timeout
 */
export async function waitForVisible(
  element: any,
  timeout: number = 5000
): Promise<void> {
  await element.waitFor({ state: 'visible', timeout })
}

/**
 * Wait for API response
 */
export async function waitForAPIResponse(
  page: any,
  urlPattern: string | RegExp,
  timeout: number = 10000
): Promise<any> {
  const response = await page.waitForResponse(
    (response: any) => {
      const url = response.url()
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern)
      }
      return urlPattern.test(url)
    },
    { timeout }
  )
  return response.json()
}

/**
 * Reset all data in the database - drops all tables
 * This is useful for E2E test cleanup to ensure a clean state
 */
export async function resetAllData(request: any): Promise<void> {
  const response = await request.delete('/api/reset')

  if (!response.ok()) {
    const error = await response.json()
    throw new Error(`Failed to reset all data: ${JSON.stringify(error)}`)
  }
}
