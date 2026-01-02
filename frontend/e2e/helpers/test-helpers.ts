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
  completeSessionViaAPI,
  getIncompleteSession,
  analyzeQuestionDistribution,
  createMissedQuestions,
  createSlowResponses,
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
  createCompletedPracticeSessions,
} from './api/test-setup-api'

// UI Helpers - Dashboard
// Note: navigateToDashboard is now exported from routing-helpers (router-based)
export {
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
  handlePinVerification,
} from './ui/journey-helpers'

// UI Helpers - Learner Management
export {
  openAddLearnerModal,
  fillLearnerName,
  selectAvatar,
  completeLearnerCreation,
} from './ui/learner-management-helpers'

// UI Helpers - Practice
// Note: navigateToPractice is now exported from routing-helpers (router-based)
export {
  getPracticeElements,
  answerQuestion,
  moveToNextQuestion,
  isSubmitButtonReady,
  completePracticeSession,
  submitPracticeSession,
  getProgressPercent,
  getQuestionText,
  waitForSummaryPage,
  waitForSessionRestoration,
  handleSessionRestorationAndAnswerToSubmit,
  waitForAndDismissLevelUpModal,
} from './ui/practice-helpers'

// Assertion Helpers
export {
  filterAchievementsByCategory,
  getAchievementStatus,
  getLevelRequirementStatus,
} from './assertions/achievement-helpers'

// Testing Framework Core
export {
  setupTestScenario,
  waitForComponent,
  cleanupScenario,
  runTestWithScenario,
  waitForComponents,
  type TestScenario,
  type TestScenarioContext,
  type WaitForComponentOptions,
} from './test-framework'

// Router Navigation Helpers
export {
  navigateToRoute,
  navigateToJourneyTab,
  navigateToDashboard,
  waitForRoute,
  getCurrentRoute,
  getCurrentQueryParams,
  navigateToPractice,
  navigateToSummary,
} from './routing-helpers'

// Loading & Animation Helpers
export {
  waitForFramerMotion,
  waitForDataLoad,
  waitForNetworkIdle,
  waitForAPIResponse,
  waitForFullLoad,
} from './ui/loading-helpers'

// Test Scenarios Builder
export {
  createTestScenario,
  ScenarioBuilder,
  scenario,
  type ScenarioConfig,
  type ScenarioContext,
} from './test-scenarios'

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
