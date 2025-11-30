import { Page, expect } from '@playwright/test'
import type { TestUser } from '../types/test-types'
import { waitForDashboardLoad } from './dashboard-helpers'

/**
 * Open journey modal for a test user
 */
export async function openJourneyModal(page: Page, testUser?: TestUser): Promise<void> {
  // If testUser is provided, select the user first
  if (testUser) {
    // Wait for dashboard to fully load
    await waitForDashboardLoad(page)
    
    // Wait for student grid to be visible (this indicates users are loaded)
    // This is more reliable than waiting for API responses that might have already completed
    const studentGrid = page.getByTestId('testid-student-grid')
    await expect(studentGrid).toBeVisible({ timeout: 10000 }).catch(() => {
      // Grid might not exist if no users, but we should still try to find the card
    })
    
    // Wait a bit for React to update the DOM after users load
    await page.waitForTimeout(500)
    
    // Find user card by name first (more reliable when user was just created)
    // This avoids the issue where getByTestId fails if the card doesn't exist yet
    const userCard = page.locator(`[data-testid^="testid-student-card-"]`).filter({ hasText: testUser.name }).first()
    
    // Wait for the card to appear
    await expect(userCard).toBeVisible({ timeout: 10000 })
    
    // Verify it's the correct card by checking the test ID attribute
    const cardTestId = await userCard.getAttribute('data-testid')
    if (cardTestId && cardTestId !== `testid-student-card-${testUser.id}`) {
      throw new Error(`Found user card with name "${testUser.name}" but wrong ID: expected testid-student-card-${testUser.id}, got ${cardTestId}`)
    }
    
    await userCard.click()
    await page.waitForTimeout(500)
  }
  
  // Click level card to open journey modal
  const levelCard = page.getByTestId('testid-level-card')
  const levelCardVisible = await levelCard.isVisible({ timeout: 2000 }).catch(() => false)
  
  if (levelCardVisible) {
    await levelCard.click()
    await page.waitForTimeout(500)
  }
}

/**
 * Click a tab in the journey modal
 */
export async function clickJourneyTab(
  page: Page,
  tabName: 'overview' | 'achievements' | 'levels' | 'tests'
): Promise<void> {
  const tab = page.getByTestId(`testid-journey-tab-${tabName}`)
  const tabVisible = await tab.first().isVisible({ timeout: 2000 }).catch(() => false)
  if (tabVisible) {
    await tab.first().click()
    await page.waitForTimeout(500)
  }
}

/**
 * Navigate to achievements tab in journey modal
 */
export async function navigateToAchievementsTab(page: Page): Promise<void> {
  const achievementsTab = page.getByTestId('testid-journey-tab-achievements')
  await achievementsTab.click()
  await page.waitForTimeout(300)
}

/**
 * Navigate to levels tab in journey modal
 * Waits for level requirements to load (lazy loaded)
 */
export async function navigateToLevelsTab(page: Page): Promise<void> {
  const levelsTab = page.getByTestId('testid-journey-tab-levels')
  await levelsTab.click()
  await page.waitForTimeout(300)
  
  // Wait for level requirements to load (they're lazy loaded when tab becomes active)
  // Check for either loading spinner to disappear or requirement cards to appear
  const loadingSpinner = page.locator('text=/Loading level requirements/i')
  const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
  
  // Wait for loading to complete (either spinner disappears or cards appear)
  await Promise.race([
    loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {}),
    requirementCards.first().waitFor({ state: 'visible', timeout: 10000 }).catch(() => {}),
    page.waitForTimeout(2000) // Fallback timeout
  ])
  
  // Additional wait for React to update
  await page.waitForTimeout(500)
}

/**
 * Navigate to tests tab in journey modal
 */
export async function navigateToTestsTab(page: Page): Promise<void> {
  const testsTab = page.getByTestId('testid-journey-tab-tests')
  await testsTab.click()
  await page.waitForTimeout(300)
  
  // Wait for tests tab content to be visible
  const testsTabContent = page.getByTestId('testid-tests-tab')
  await expect(testsTabContent).toBeVisible({ timeout: 5000 })
}

