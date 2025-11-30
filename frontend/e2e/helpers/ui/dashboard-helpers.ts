import { Page, expect } from '@playwright/test'
import type { TestUser } from '../types/test-types'

/**
 * Navigate to dashboard and wait for load
 */
export async function navigateToDashboard(page: Page): Promise<void> {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
}

/**
 * Wait for dashboard to load (header visible)
 */
export async function waitForDashboardLoad(page: Page): Promise<void> {
  await page.getByTestId('testid-select-learner-header').waitFor({ state: 'visible', timeout: 5000 })
  
  // Wait for loading to complete (loading message should disappear)
  const loadingMessage = page.locator('text=/Loading learners/i')
  await loadingMessage.waitFor({ state: 'hidden', timeout: 5000 }).catch(() => {
    // Loading might already be done, continue
  })
}

/**
 * Click user card and wait for details to load
 * Filters by user name to avoid matching other parallel test runs
 */
export async function clickUserCard(page: Page, testUser: TestUser): Promise<void> {
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
  await page.waitForTimeout(1000) // Wait for learner details to load
}

/**
 * Click Start Practice button
 */
export async function clickStartPractice(page: Page): Promise<void> {
  const startPracticeButton = page.getByTestId('testid-start-practice-button')
  await startPracticeButton.click()
}

/**
 * Enter PIN using PinPad buttons
 */
export async function enterPin(page: Page, pin: string): Promise<void> {
  const pinDisplay = page.getByTestId('testid-pin-display')
  
  for (const digit of pin.split('')) {
    const digitButton = page.getByRole('button', { name: digit, exact: true })
    await digitButton.click()
    await page.waitForTimeout(200) // Small delay between clicks
  }
  
  // Wait for PIN to be complete (4 digits)
  await expect(pinDisplay).toContainText('4 / 4', { timeout: 2000 })
  await page.waitForTimeout(300)
}

/**
 * Click Start Practice button in the PIN modal
 */
export async function clickStartPracticeInModal(page: Page): Promise<void> {
  const modalSubmitButton = page.locator('[role="dialog"]').getByRole('button', { name: /start practice/i })
  await expect(modalSubmitButton).toBeEnabled({ timeout: 2000 })
  await modalSubmitButton.click()
}

