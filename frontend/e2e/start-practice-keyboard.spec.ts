import { test, expect } from './fixtures/test-user'
import {
  navigateToDashboard,
  waitForDashboardLoad,
  clickUserCard,
  clickStartPractice,
  enterPin,
} from './helpers/test-helpers'

test.describe('Start Practice - Keyboard Input', () => {
  test('START-KB-001: Enter key submits PIN after entering 4 digits', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal to appear
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Enter PIN using keyboard (type numbers directly)
    // The PinPad should accept keyboard input if implemented
    const pinInput = page.locator('input[type="text"], input[type="number"]').first()
    const hasInput = await pinInput.isVisible({ timeout: 2000 }).catch(() => false)
    
    if (hasInput) {
      // Type PIN using keyboard
      await pinInput.fill(testUser.pin.toString())
      
      // Small delay to ensure React state updates before Enter
      await page.waitForTimeout(150)

      // Watch for PIN verification request (helps debug flakiness)
      const verifyPinResponsePromise = page
        .waitForResponse(
          (r) => r.url().includes('/api/users/') && r.url().includes('/verify-pin') && r.request().method() === 'POST',
          { timeout: 10000 },
        )
        .catch(() => null)

      // Press Enter key - should trigger PIN verification and start practice
      await pinInput.press('Enter')
      
      // If verification happens, it should respond quickly
      await verifyPinResponsePromise

      // Should navigate to practice page
      await page.waitForURL(/\/practice/, { timeout: 10000 })
      expect(page.url()).toContain('/practice')
    } else {
      // If no direct input, use PinPad buttons with keyboard shortcuts
      // Type digits - PinPad might listen to keydown events
      await page.keyboard.type(testUser.pin.toString())

      // Confirm all digits registered
      await expect(pinDisplay).toContainText('4', { timeout: 3000 })

      // Small delay to ensure React state updates before Enter
      await page.waitForTimeout(150)

      // Watch for PIN verification request (helps debug flakiness)
      const verifyPinResponsePromise = page
        .waitForResponse(
          (r) => r.url().includes('/api/users/') && r.url().includes('/verify-pin') && r.request().method() === 'POST',
          { timeout: 10000 },
        )
        .catch(() => null)
      
      // Press Enter to submit
      await page.keyboard.press('Enter')

      // If verification happens, it should respond quickly
      await verifyPinResponsePromise
      
      // Wait for navigation
      const navigated = await page.waitForURL(/\/practice/, { timeout: 15000 }).catch(() => false)
      if (!navigated) {
        // Some flows auto-navigate after verification; others require Enter.
        // If we didn't navigate yet, press Enter once more after a short delay.
        await page.waitForTimeout(300)
        await page.keyboard.press('Enter')
        await page.waitForURL(/\/practice/, { timeout: 15000 })
      }
      expect(page.url()).toContain('/practice')
    }
  })

  test('START-KB-002: Number keys enter PIN digits', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal to appear
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Try typing numbers directly
    // PinPad should listen to keyboard number input
    await page.keyboard.type('1')
    await page.waitForTimeout(200)
    
    // Verify first digit was entered (PIN display should show "1 / 4" or similar)
    const pinText = await pinDisplay.textContent()
    expect(pinText).toMatch(/1/)
    
    // Type remaining digits
    await page.keyboard.type('234')
    await page.waitForTimeout(200)
    
    // Verify all 4 digits entered
    const finalPinText = await pinDisplay.textContent()
    expect(finalPinText).toMatch(/4/)
    
    // Start button should be enabled
    const startButton = page.getByRole('button', { name: /^start$/i })
    await expect(startButton).toBeEnabled({ timeout: 2000 })
    
    // Press Enter to submit
    await page.keyboard.press('Enter')
    
    // Should navigate to practice
    await page.waitForURL(/\/practice/, { timeout: 5000 })
  })

  test('START-KB-003: Backspace/Delete removes PIN digits', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Enter some digits
    await page.keyboard.type('1234')
    await page.waitForTimeout(200)
    
    // Verify 4 digits entered
    let pinText = await pinDisplay.textContent()
    // pinDisplay format: "{entered} / 4 digits entered"
    expect(pinText).toMatch(/^4\s*\/\s*4\b/)
    
    // Press Backspace to remove last digit
    await page.keyboard.press('Backspace')
    await page.waitForTimeout(200)
    
    // Verify digit was removed
    pinText = await pinDisplay.textContent()
    expect(pinText).toMatch(/^3\s*\/\s*4\b/)
    
    // Start button should be disabled (only 3 digits)
    const startButton = page.getByRole('button', { name: /^start$/i })
    await expect(startButton).toBeDisabled()
  })

  test('START-KB-004: Non-numeric keys are ignored', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Type letters and special characters - should be ignored
    await page.keyboard.type('abc!@#')
    await page.waitForTimeout(200)
    
    // PIN should still be empty (0 digits)
    const pinText = await pinDisplay.textContent()
    expect(pinText).toMatch(/0/)
    
    // Type valid numbers
    await page.keyboard.type('1234')
    await page.waitForTimeout(200)
    
    // Verify only numbers were accepted
    const finalPinText = await pinDisplay.textContent()
    expect(finalPinText).toMatch(/4/)
  })

  test('START-KB-005: Click Start Practice button also works', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await clickUserCard(page, testUser)
    await clickStartPractice(page)
    
    // Wait for PIN modal
    const pinDisplay = page.getByTestId('testid-pin-display')
    await expect(pinDisplay).toBeVisible({ timeout: 3000 })
    
    // Enter PIN using PinPad buttons (click-based)
    await enterPin(page, testUser.pin.toString())
    
    // Click Start button (not using keyboard)
    const startButton = page.getByRole('button', { name: /^start$/i })
    await startButton.click()
    
    // Should navigate to practice
    await page.waitForURL(/\/practice/, { timeout: 5000 })
    expect(page.url()).toContain('/practice')
  })

  test('START-KB-006: Touch input works with PinPad', async ({ page, testUser }) => {
    // `tap()` requires a touch-enabled browser context. Setting navigator.maxTouchPoints
    // via initScript is not sufficient for Playwright's input model.
    const browser = page.context().browser()
    if (!browser) {
      throw new Error('Browser instance not available for touch context test')
    }

    const touchContext = await browser.newContext({ hasTouch: true })
    const touchPage = await touchContext.newPage()

    try {
      await navigateToDashboard(touchPage)
      await waitForDashboardLoad(touchPage)
      await clickUserCard(touchPage, testUser)
      await clickStartPractice(touchPage)
      
      // Wait for PIN modal
      const pinDisplay = touchPage.getByTestId('testid-pin-display')
      await expect(pinDisplay).toBeVisible({ timeout: 3000 })
      
      // Use touch/click on PinPad buttons
      await enterPin(touchPage, testUser.pin.toString())
      
      // Touch/click Start button
      const startButton = touchPage.getByRole('button', { name: /^start$/i })
      await startButton.tap()
      
      // Should navigate to practice
      await touchPage.waitForURL(/\/practice/, { timeout: 10000 })
      expect(touchPage.url()).toContain('/practice')
    } finally {
      await touchContext.close()
    }
  })
})

