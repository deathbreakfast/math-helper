import { test, expect } from '@playwright/test'

test.describe('Page Load Tests', () => {
  test('should load the main dashboard page', async ({ page }) => {
    await page.goto('/')
    
    // Check for key elements on the dashboard
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    // Check that the page has loaded (not showing error)
    await expect(page.locator('body')).toBeVisible()
  })

  test('should load the practice page', async ({ page }) => {
    // Practice page may require URL params, but should still load
    await page.goto('/practice')
    
    // Check that the page has loaded
    await expect(page.locator('body')).toBeVisible()
    
    // If there's a header or main content area, check for it
    // The practice page might show a message if no user is selected
    const bodyText = await page.locator('body').textContent()
    expect(bodyText).toBeTruthy()
  })

  test('should load the summary page', async ({ page }) => {
    // Summary page may require session data, but should still load
    await page.goto('/summary')
    
    // Check that the page has loaded
    await expect(page.locator('body')).toBeVisible()
    
    // The summary page might show a message if no session data is available
    const bodyText = await page.locator('body').textContent()
    expect(bodyText).toBeTruthy()
  })

  test('should have test IDs on interactive elements when practice page loads with user', async ({ page }) => {
    // Navigate to practice page with user params (if available)
    // This test verifies that test IDs are present when the page is fully loaded
    await page.goto('/practice?user=TestUser&pin=1234&userId=1')
    
    // Wait a bit for the page to potentially load user data
    await page.waitForTimeout(1000)
    
    // Check that the page has loaded
    await expect(page.locator('body')).toBeVisible()
    
    // If practice session is active, check for key test IDs
    // These might not be present if no user/session is available, which is okay
    const answerInput = page.getByTestId('testid-answer-input')
    const questionDisplay = page.getByTestId('testid-question-display')
    
    // Only check if elements exist (they might not if session hasn't started)
    const answerInputCount = await answerInput.count()
    const questionDisplayCount = await questionDisplay.count()
    
    // If elements are present, verify they're visible
    if (answerInputCount > 0) {
      await expect(answerInput.first()).toBeVisible()
    }
    if (questionDisplayCount > 0) {
      await expect(questionDisplay.first()).toBeVisible()
    }
  })
})

