/**
 * Core Testing Framework - Abstractions for common test patterns
 * 
 * Provides reusable functions for test data preparation, component waiting,
 * animation handling, and cleanup orchestration.
 */

import { Page, APIRequestContext, expect as playwrightExpect } from '@playwright/test'
import type { TestUser } from './types/test-types'
import { createTestUserWithState, setupTestUserState } from './api/test-setup-api'
import { deleteTestUser } from './api/user-api'

/**
 * Test scenario configuration for data preparation
 */
export interface TestScenario {
  user?: {
    name?: string
    avatar?: string
    pin?: string
    level?: number
  }
  achievements?: string[]
  sessions?: {
    level: number
    count: number
  }[]
  // Add more scenario options as needed
}

/**
 * Test scenario context returned after setup
 */
export interface TestScenarioContext {
  user: TestUser
  scenario: TestScenario
  cleanup: () => Promise<void>
}

/**
 * Options for component waiting
 */
export interface WaitForComponentOptions {
  timeout?: number
  state?: 'visible' | 'attached' | 'detached' | 'hidden'
  waitForAnimation?: boolean
}

/**
 * Set up a test scenario with user, achievements, sessions, etc.
 * Returns a context object with the created user and cleanup function.
 */
export async function setupTestScenario(
  request: APIRequestContext,
  scenario: TestScenario
): Promise<TestScenarioContext> {
  // Create user with initial state
  const user = await createTestUserWithState(request, {
    name: scenario.user?.name,
    avatar: scenario.user?.avatar,
    pin: scenario.user?.pin,
    level: scenario.user?.level,
    achievements: scenario.achievements,
  })

  // Set up additional state if needed
  if (scenario.user?.level !== undefined || scenario.achievements) {
    await setupTestUserState(request, user.id, {
      level: scenario.user?.level,
      achievements: scenario.achievements,
    })
  }

  // TODO: Handle sessions setup when needed
  // For now, sessions would need to be created via createCompletedPracticeSessions

  // Return context with cleanup function
  return {
    user,
    scenario,
    cleanup: async () => {
      try {
        await deleteTestUser(request, user.id)
      } catch (error) {
        console.warn(`Failed to cleanup test user ${user.id}:`, error)
      }
    },
  }
}

/**
 * Wait for a component to be visible/ready with smart waiting logic
 * Handles animations automatically and provides configurable timeout/retry logic
 */
export async function waitForComponent(
  page: Page,
  testId: string,
  options: WaitForComponentOptions = {}
): Promise<void> {
  const {
    timeout = 10000,
    state = 'visible',
    waitForAnimation = true,
  } = options

  // Wait for component to be in the desired state
  const component = page.getByTestId(testId)
  await component.waitFor({ state, timeout })

  // Wait for animations to complete if requested
  if (waitForAnimation) {
    await waitForAnimationInFramework(page, undefined, 800) // Default 800ms for framer-motion
  }
}

/**
 * Wait for framer-motion animations to complete
 * Default duration matches framer-motion default animation duration (800ms)
 * Note: Use waitForFramerMotion from loading-helpers.ts for more features
 */
async function waitForAnimationInFramework(
  page: Page,
  selector?: string,
  duration: number = 800
): Promise<void> {
  if (selector) {
    // Wait for specific element's animation
    const element = page.locator(selector)
    await element.waitFor({ state: 'visible' })
  }
  
  // Wait for animation duration (framer-motion default is ~800ms)
  await page.waitForTimeout(duration)
  
  // Additional small wait to ensure animations are fully settled
  await page.waitForTimeout(100)
}

/**
 * Clean up test scenario data
 * Handles errors gracefully to avoid masking test failures
 */
export async function cleanupScenario(
  request: APIRequestContext,
  context: TestScenarioContext
): Promise<void> {
  try {
    await context.cleanup()
  } catch (error) {
    console.warn(`Failed to cleanup scenario for user ${context.user.id}:`, error)
    // Don't throw - cleanup failures shouldn't fail tests
  }
}

/**
 * Run a test with automatic scenario setup and cleanup
 * Pattern: beforeEach (data prep) → test logic → afterEach (cleanup)
 */
export async function runTestWithScenario(
  page: Page,
  request: APIRequestContext,
  scenario: TestScenario,
  testFn: (context: TestScenarioContext) => Promise<void>
): Promise<void> {
  // Setup
  const context = await setupTestScenario(request, scenario)

  try {
    // Run test
    await testFn(context)
  } finally {
    // Cleanup
    await cleanupScenario(request, context)
  }
}

/**
 * Wait for multiple components to be ready
 * Useful when waiting for a page/section to fully load
 */
export async function waitForComponents(
  page: Page,
  testIds: string[],
  options: WaitForComponentOptions = {}
): Promise<void> {
  await Promise.all(
    testIds.map((testId) => waitForComponent(page, testId, options))
  )
}

