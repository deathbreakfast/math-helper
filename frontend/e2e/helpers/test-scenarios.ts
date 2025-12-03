/**
 * Scenario-Based Test Data Preparation
 * 
 * Provides a fluent API for building test scenarios with users, achievements,
 * sessions, and other test data configurations.
 */

import { APIRequestContext } from '@playwright/test'
import type { TestUser } from './types/test-types'
import { createTestUser, deleteTestUser } from './api/user-api'
import { setupTestUserState, createCompletedPracticeSessions } from './api/test-setup-api'

/**
 * Scenario configuration for test data setup
 */
export interface ScenarioConfig {
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
}

/**
 * Scenario context with created resources and cleanup function
 */
export interface ScenarioContext {
  user: TestUser
  cleanup: () => Promise<void>
}

/**
 * Create a complete test scenario with user, achievements, and sessions
 * Returns a context object with cleanup function
 */
export async function createTestScenario(
  request: APIRequestContext,
  config: ScenarioConfig
): Promise<ScenarioContext> {
  // Create user first
  const user = await createTestUser(request, {
    name: config.user?.name,
    avatar: config.user?.avatar,
    pin: config.user?.pin,
  })

  try {
    // Set up user state (level, achievements)
    if (config.user?.level !== undefined || config.achievements) {
      await setupTestUserState(request, user.id, {
        level: config.user?.level,
        achievements: config.achievements || [],
      })
      
      // Refresh user to get updated level
      const { getUser } = await import('./api/user-api')
      const updatedUser = await getUser(request, user.id)
      if (updatedUser) {
        Object.assign(user, updatedUser)
      }
    }

    // Create practice sessions if specified
    if (config.sessions) {
      for (const sessionConfig of config.sessions) {
        await createCompletedPracticeSessions(
          request,
          user.id,
          sessionConfig.level,
          sessionConfig.count
        )
      }
    }

    // Return context with cleanup
    return {
      user,
      cleanup: async () => {
        try {
          await deleteTestUser(request, user.id)
        } catch (error) {
          console.warn(`Failed to cleanup test user ${user.id}:`, error)
        }
      },
    }
  } catch (error) {
    // If setup fails, try to clean up the user
    try {
      await deleteTestUser(request, user.id)
    } catch (cleanupError) {
      console.warn(`Failed to cleanup user after setup error:`, cleanupError)
    }
    throw error
  }
}

/**
 * Fluent API builder for creating test scenarios
 */
export class ScenarioBuilder {
  private config: ScenarioConfig = {}

  /**
   * Set user configuration
   */
  withUser(userConfig: ScenarioConfig['user']): this {
    this.config.user = { ...this.config.user, ...userConfig }
    return this
  }

  /**
   * Set user level
   */
  withLevel(level: number): this {
    if (!this.config.user) {
      this.config.user = {}
    }
    this.config.user.level = level
    return this
  }

  /**
   * Add achievements
   */
  withAchievements(achievements: string[]): this {
    this.config.achievements = [
      ...(this.config.achievements || []),
      ...achievements,
    ]
    return this
  }

  /**
   * Add completed practice sessions
   */
  withCompletedSessions(level: number, count: number): this {
    if (!this.config.sessions) {
      this.config.sessions = []
    }
    this.config.sessions.push({ level, count })
    return this
  }

  /**
   * Build and create the scenario
   */
  async build(request: APIRequestContext): Promise<ScenarioContext> {
    return createTestScenario(request, this.config)
  }

  /**
   * Reset the builder to start fresh
   */
  reset(): this {
    this.config = {}
    return this
  }
}

/**
 * Helper function to create a scenario builder
 */
export function scenario(): ScenarioBuilder {
  return new ScenarioBuilder()
}

