/**
 * Router Navigation Helpers
 * 
 * Provides URL-based navigation helpers for tests, leveraging React Router.
 * Use URL navigation when the navigation mechanism (button click, etc.) is already
 * tested elsewhere. This allows tests to focus on the destination state/feature
 * rather than the navigation path.
 */

import { Page, expect } from '@playwright/test'

/**
 * Navigate to a route via URL
 * Use when navigation mechanism is already tested elsewhere
 * 
 * @param page - Playwright page object
 * @param route - Route path (e.g., '/journey/123/achievements')
 * @param params - Query parameters as key-value pairs
 */
export async function navigateToRoute(
  page: Page,
  route: string,
  params?: Record<string, string | null>
): Promise<void> {
  // Build URL with query parameters
  let url = route
  if (params && Object.keys(params).length > 0) {
    const queryString = Object.entries(params)
      .filter(([_, value]) => value !== null && value !== undefined)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value!)}`)
      .join('&')
    
    if (queryString) {
      url = `${route}?${queryString}`
    }
  }

  // Navigate to the route
  await page.goto(url)
  
  // Wait for route to load
  await waitForRoute(page, route)
}

/**
 * Navigate to a specific journey tab with optional filters
 * 
 * @param page - Playwright page object
 * @param userId - User ID for the journey
 * @param tab - Journey tab: 'overview' | 'achievements' | 'levels' | 'tests'
 * @param filters - Optional filters as key-value pairs (e.g., { filter: 'addition-basics' })
 */
export async function navigateToJourneyTab(
  page: Page,
  userId: number,
  tab: 'overview' | 'achievements' | 'levels' | 'tests',
  filters?: Record<string, string | null>
): Promise<void> {
  const route = `/journey/${userId}/${tab}`
  await navigateToRoute(page, route, filters)
  
  // Wait for the tab content to be visible
  const tabContentSelectors: Record<string, string> = {
    overview: 'testid-overview-tab',
    achievements: 'testid-achievements-grid',
    levels: 'testid-levels-tab',
    tests: 'testid-tests-tab',
  }
  
  const testId = tabContentSelectors[tab]
  if (testId) {
    await expect(page.getByTestId(testId)).toBeVisible({ timeout: 10000 })
  }
}

/**
 * Navigate to dashboard with optional user selection
 * 
 * @param page - Playwright page object
 * @param selectedUserId - Optional user ID to select via query param
 */
export async function navigateToDashboard(
  page: Page,
  selectedUserId?: number
): Promise<void> {
  const params = selectedUserId ? { selectedUserId: selectedUserId.toString() } : undefined
  await navigateToRoute(page, '/', params)
  
  // Wait for dashboard to load
  await expect(page.getByTestId('testid-select-learner-header')).toBeVisible({ timeout: 10000 })
}

/**
 * Wait for route to load and verify navigation completed
 * 
 * @param page - Playwright page object
 * @param expectedRoute - Expected route path (without query params)
 */
export async function waitForRoute(
  page: Page,
  expectedRoute: string
): Promise<void> {
  // Wait for page to load
  await page.waitForLoadState('domcontentloaded')
  
  // Verify route matches (allowing for query params)
  const currentUrl = new URL(page.url())
  const currentPath = currentUrl.pathname
  
  if (!currentPath.startsWith(expectedRoute)) {
    throw new Error(
      `Route mismatch: expected path starting with "${expectedRoute}", got "${currentPath}"`
    )
  }
  
  // Wait a bit for React Router to finish navigation
  await page.waitForTimeout(200)
}

/**
 * Get current route path from URL
 * 
 * @param page - Playwright page object
 * @returns Current route path
 */
export function getCurrentRoute(page: Page): string {
  const url = new URL(page.url())
  return url.pathname
}

/**
 * Get current query parameters from URL
 * 
 * @param page - Playwright page object
 * @returns Query parameters as key-value pairs
 */
export function getCurrentQueryParams(page: Page): Record<string, string> {
  const url = new URL(page.url())
  const params: Record<string, string> = {}
  
  url.searchParams.forEach((value, key) => {
    params[key] = value
  })
  
  return params
}

/**
 * Navigate to practice page with optional parameters
 * 
 * @param page - Playwright page object
 * @param params - Practice session parameters (userId, level, etc.)
 */
export async function navigateToPractice(
  page: Page,
  params?: Record<string, string | null>
): Promise<void> {
  await navigateToRoute(page, '/practice', params)
}

/**
 * Navigate to summary page with optional parameters
 * 
 * @param page - Playwright page object
 * @param params - Summary page parameters (sessionId, etc.)
 */
export async function navigateToSummary(
  page: Page,
  params?: Record<string, string | null>
): Promise<void> {
  await navigateToRoute(page, '/summary', params)
}

