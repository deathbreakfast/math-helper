/**
 * Loading and Animation Utilities
 * 
 * Provides utilities for handling loading states, animations, and network activity
 * in E2E tests.
 */

import { Page, expect } from '@playwright/test'

/**
 * Wait for framer-motion animations to complete
 * Default duration matches framer-motion default animation duration (800ms)
 */
export async function waitForFramerMotion(
  page: Page,
  selector?: string,
  duration: number = 800
): Promise<void> {
  if (selector) {
    // Wait for specific element to be visible first
    const element = page.locator(selector)
    await element.waitFor({ state: 'visible' }).catch(() => {
      // Element might not exist, continue anyway
    })
  }
  
  // Wait for animation duration (framer-motion default is ~800ms)
  await page.waitForTimeout(duration)
  
  // Additional small wait to ensure animations are fully settled
  await page.waitForTimeout(100)
}

/**
 * Wait for data to load by checking for loading spinners and content appearance
 * Handles API response timing and loading states
 */
export async function waitForDataLoad(
  page: Page,
  testId: string,
  timeout: number = 10000
): Promise<void> {
  // First, wait for any loading spinner to disappear
  const loadingSelectors = [
    '[data-testid*="loading"]',
    '[data-testid*="spinner"]',
    'text=/Loading/i',
    'text=/loading/i',
  ]

  for (const selector of loadingSelectors) {
    try {
      const loadingElement = page.locator(selector).first()
      const isVisible = await loadingElement.isVisible({ timeout: 2000 }).catch(() => false)
      if (isVisible) {
        await loadingElement.waitFor({ state: 'hidden', timeout: timeout - 2000 })
      }
    } catch (error) {
      // Loading element might not exist, continue
    }
  }

  // Wait for the target content to appear
  const contentElement = page.getByTestId(testId)
  await expect(contentElement).toBeVisible({ timeout })
  
  // Small additional wait for React to finish rendering
  await page.waitForTimeout(200)
}

/**
 * Wait for network activity to complete
 * Waits for all API calls to finish before proceeding
 * Useful before assertions to ensure data is loaded
 */
export async function waitForNetworkIdle(
  page: Page,
  timeout: number = 10000
): Promise<void> {
  try {
    await page.waitForLoadState('networkidle', { timeout })
  } catch (error) {
    // Network idle might timeout if there's ongoing polling
    // Wait a bit more and continue
    await page.waitForTimeout(1000)
  }
}

/**
 * Wait for a specific API response
 * Useful when you know a specific endpoint should be called
 */
export async function waitForAPIResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = 10000
): Promise<Response> {
  const response = await page.waitForResponse(
    (response) => {
      const url = response.url()
      if (typeof urlPattern === 'string') {
        return url.includes(urlPattern)
      }
      return urlPattern.test(url)
    },
    { timeout }
  )
  
  // Wait a bit for the response to be processed
  await page.waitForTimeout(200)
  
  return response
}

/**
 * Wait for loading state to complete and content to be ready
 * Combines waiting for loading spinners, network idle, and content
 */
export async function waitForFullLoad(
  page: Page,
  contentTestId: string,
  timeout: number = 15000
): Promise<void> {
  // Wait for loading to complete
  await waitForDataLoad(page, contentTestId, timeout)
  
  // Wait for network to be idle
  await waitForNetworkIdle(page, 5000)
  
  // Wait for animations to settle
  await waitForFramerMotion(page)
}

/**
 * Helper type for Response (from page.waitForResponse)
 */
type Response = {
  url(): string
  status(): number
  json(): Promise<any>
  ok(): boolean
}

