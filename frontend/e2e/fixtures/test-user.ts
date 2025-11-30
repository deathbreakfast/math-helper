import { test as base, APIRequestContext } from '@playwright/test'
import { createTestUser, deleteTestUser, type TestUser } from '../helpers/test-helpers'

type TestFixtures = {
  testUser: TestUser
  authenticatedPage: any
}

/**
 * Playwright fixtures for E2E tests
 * 
 * Usage:
 *   test('my test', async ({ testUser, page }) => {
 *     // testUser is automatically created and will be cleaned up
 *     console.log(testUser.name) // e.g., "TestUser_MyTest_1701234567_a3f2"
 *   })
 */
export const test = base.extend<TestFixtures>({
  /**
   * Auto-creates a unique test user before each test
   * and deletes it after the test completes
   */
  testUser: async ({ request }, use, testInfo) => {
    // Generate test name from test title
    const testName = testInfo.title.replace(/[^a-zA-Z0-9]/g, '_')
    
    // Create unique test user
    const user = await createTestUser(request, {
      name: `TestUser_${testName}_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
    })

    // Use the test user in the test
    await use(user)

    // Cleanup: delete the test user after test completes
    try {
      await deleteTestUser(request, user.id)
    } catch (error) {
      // Log but don't fail the test if cleanup fails
      console.warn(`Failed to cleanup test user ${user.id}:`, error)
    }
  },

  /**
   * Page with test user already "authenticated" (user context available)
   * This fixture sets up a page with the test user's context
   */
  authenticatedPage: async ({ page, testUser }, use) => {
    // Navigate to dashboard - the user will be available via API
    await page.goto('/')
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle')
    
    await use(page)
  },
})

export { expect } from '@playwright/test'


