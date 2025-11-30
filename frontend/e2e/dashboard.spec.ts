import { test, expect } from './fixtures/test-user'
import {
  navigateToDashboard,
  waitForDashboardLoad,
  clickUserCard,
  clickStartPractice,
  enterPin,
  clickStartPracticeInModal,
} from './helpers/test-helpers'

test.describe('Dashboard & Navigation', () => {
  test('DASH-001: Dashboard loads', async ({ page }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    
    // The student grid only appears when there are learners
    // Check if grid exists, or if "No learners yet" message exists
    const studentGrid = page.getByTestId('testid-student-grid')
    const noLearnersMessage = page.locator('text=/No learners yet/i')
    
    const gridCount = await studentGrid.count()
    const messageCount = await noLearnersMessage.count()
    
    // Either the grid should be visible (if learners exist) or the message (if no learners)
    expect(gridCount > 0 || messageCount > 0).toBe(true)
    
    if (gridCount > 0) {
      await expect(studentGrid).toBeVisible()
    } else if (messageCount > 0) {
      await expect(noLearnersMessage).toBeVisible()
    }
    
    // Check that the page has loaded (not showing error)
    await expect(page.locator('body')).toBeVisible()
  })

  test('DASH-002: Learner stats display', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    
    // Verify stats are displayed (the exact elements depend on implementation)
    // At minimum, we should see the user's name
    await expect(page.locator('body')).toContainText(testUser.name)
    
    // Check for stats cards or level information
    const statsSection = page.locator('text=/level|questions|accuracy|speed/i').first()
    await expect(statsSection).toBeVisible({ timeout: 5000 })
  })

  test('DASH-003: Start Practice button', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // PIN modal should appear - wait for PIN display to be visible
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
  })

  test('DASH-004: PIN verification', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal to appear
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Enter incorrect PIN first (9999) using PinPad buttons
    await enterPin(page, '9999')
    
    // Click Start Practice button in the modal (within the dialog)
    await clickStartPracticeInModal(page)
    
    // Should show error for incorrect PIN
    await page.waitForTimeout(1000)
    const errorMessage = page.locator('text=/incorrect|wrong|invalid/i').or(
      page.locator('[role="alert"]')
    )
    const hasError = await errorMessage.first().isVisible({ timeout: 2000 }).catch(() => false)
    expect(hasError).toBe(true)
    
    // PIN is automatically cleared on error, wait for it to reset
    await expect(pinDisplay).toContainText('0 / 4', { timeout: 2000 })
    await page.waitForTimeout(300)
    
    // Now enter correct PIN using PinPad buttons
    await enterPin(page, testUser.pin.toString())
    
    // Click Start Practice button again (button should be re-enabled)
    await clickStartPracticeInModal(page)
    
    // Should navigate to practice page
    await page.waitForURL(/\/practice/, { timeout: 5000 })
    expect(page.url()).toContain('/practice')
  })
})

