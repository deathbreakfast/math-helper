import { Page, expect } from '@playwright/test'
import { enterPin } from './dashboard-helpers'

/**
 * Open Add Learner modal
 */
export async function openAddLearnerModal(page: Page): Promise<void> {
  const addLearnerButton = page.getByTestId('testid-add-learner-button')
  await addLearnerButton.click()
  await expect(page.getByTestId('testid-add-learner-modal')).toBeVisible({ timeout: 3000 })
}

/**
 * Fill learner name in the modal
 */
export async function fillLearnerName(page: Page, name: string): Promise<void> {
  const nameInput = page.getByTestId('testid-learner-name-input')
  await nameInput.fill(name)
}

/**
 * Select avatar in the modal (default: first avatar)
 */
export async function selectAvatar(page: Page, avatarIndex: number = 0): Promise<void> {
  const avatarOptionsContainer = page.getByTestId('testid-avatar-options')
  await expect(avatarOptionsContainer).toBeVisible({ timeout: 2000 })
  
  const avatarButton = avatarOptionsContainer.locator('button').nth(avatarIndex)
  await expect(avatarButton).toBeVisible({ timeout: 2000 })
  await avatarButton.click({ force: true })
  await page.waitForTimeout(500)
}

/**
 * Complete learner creation flow (handles PIN entry and completion)
 */
export async function completeLearnerCreation(page: Page, pin: string = '5678'): Promise<void> {
  // Step 1: Fill name and click next
  const nameNextButton = page.getByTestId('testid-name-step-next-button')
  await nameNextButton.click()
  
  // Wait for avatar step to appear
  await expect(page.getByTestId('testid-avatar-step')).toBeVisible({ timeout: 3000 })
  
  // Step 2: Select avatar and click next
  await selectAvatar(page)
  const avatarNextButton = page.getByTestId('testid-avatar-step-next-button')
  await expect(avatarNextButton).toBeVisible({ timeout: 2000 })
  await avatarNextButton.click()
  await page.waitForTimeout(1000)
  
  // Step 3: Enter PIN
  const pinDisplay = page.getByTestId('testid-pin-display')
  const pinDisplayVisible = await pinDisplay.isVisible({ timeout: 3000 }).catch(() => false)
  
  if (pinDisplayVisible) {
    await enterPin(page, pin)
    
    // Wait for the complete button to be enabled and stable
    const pinCompleteButton = page.getByTestId('testid-pin-complete-button')
    await expect(pinCompleteButton).toBeEnabled({ timeout: 2000 })
    await expect(pinCompleteButton).toBeVisible({ timeout: 2000 })
    
    // Scroll into view if needed
    await pinCompleteButton.scrollIntoViewIfNeeded()
    
    // Click complete button
    await pinCompleteButton.click()
  }
}

