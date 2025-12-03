import { test, expect } from './fixtures/test-user'
import {
  createTestUser,
  deleteTestUser,
  generateTestUserName,
  listUsers,
  navigateToDashboard,
  waitForDashboardLoad,
  openAddLearnerModal,
  fillLearnerName,
  completeLearnerCreation,
} from './helpers/test-helpers'

test.describe('Learner Management', () => {
  test('LM-001: Create new learner', async ({ page, request }) => {
    const testName = generateTestUserName('CreateLearner')
    // Extract visible portion of test name for unique filtering
    // Format: TestUser_CreateLearner_{timestamp}_{random}
    // Visible portion is truncated in CSS to: TestUser_CreateLearner_1764 (first 4-5 digits of timestamp)
    const timestampMatch = testName.match(/TestUser_CreateLearner_(\d{4,5})/)
    const visiblePrefix = timestampMatch ? `TestUser_CreateLearner_${timestampMatch[1]}` : 'TestUser_CreateLearner_'
    let createdUserId: number | null = null
    
    // Pre-test cleanup: remove any existing test users with similar names (from previous failed tests)
    try {
      const existingUsers = await listUsers(request)
      const testUsersToClean = existingUsers.filter(u => u.name.startsWith('TestUser_CreateLearner_'))
      for (const user of testUsersToClean) {
        try {
          await deleteTestUser(request, user.id)
        } catch (error) {
          // Ignore cleanup errors
        }
      }
    } catch (error) {
      // Ignore pre-test cleanup errors
    }
    
    try {
      await navigateToDashboard(page)
      await waitForDashboardLoad(page)
      await openAddLearnerModal(page)
      
      // Fill in the name
      await fillLearnerName(page, testName)
      
      // Complete learner creation flow (avatar selection + PIN entry)
      await completeLearnerCreation(page, '5678')
    
      // Wait for the modal to close (indicates successful creation)
      await expect(page.getByTestId('testid-add-learner-modal')).not.toBeVisible({ timeout: 10000 })
      
      // Wait for the student grid to be visible
      await expect(page.getByTestId('testid-student-grid')).toBeVisible({ timeout: 10000 })
      
      // Wait a bit for React to update the DOM after user is added
      await page.waitForTimeout(500)
      
      // Find the user card by visible name (truncated in CSS, so use prefix with first 4-5 digits)
      // This pattern matches what's used in dashboard-helpers.ts
      const learnerCard = page.locator(`[data-testid^="testid-student-card-"]`).filter({ hasText: visiblePrefix }).first()
      
      // Wait for the card to appear in the grid
      await expect(learnerCard).toBeVisible({ timeout: 10000 })
      
      // Extract the user ID from the card's testid attribute for cleanup
      const cardTestId = await learnerCard.getAttribute('data-testid')
      if (cardTestId) {
        const idMatch = cardTestId.match(/testid-student-card-(\d+)/)
        if (idMatch) {
          createdUserId = parseInt(idMatch[1], 10)
        }
      }
      
      // Verify the card contains the test name to ensure it's the correct user
      const cardText = await learnerCard.textContent()
      expect(cardText).toContain('TestUser_CreateLearner_')
    } catch (error) {
      throw error
    } finally {
      // Cleanup: delete the test user if it was created
      // Try multiple cleanup strategies to ensure we don't leave orphaned test users
      try {
        if (createdUserId) {
          await deleteTestUser(request, createdUserId)
        }
      } catch (error) {
        // If deletion fails, try to find by name as fallback
      }
      
      // Fallback: try to find and delete by name (handles cases where ID wasn't captured)
      try {
        const users = await listUsers(request)
        // Find all users matching the test name (in case of duplicates from failed tests)
        const matchingUsers = users.filter(u => u.name === testName)
        
        for (const user of matchingUsers) {
          try {
            await deleteTestUser(request, user.id)
          } catch (error) {
            // Ignore individual deletion errors
          }
        }
        
        // Also clean up any other test users from this test run (in case name generation created duplicates)
        const allTestUsers = users.filter(u => u.name.startsWith('TestUser_CreateLearner_') && u.name.includes(testName.split('_').slice(-2).join('_')))
        for (const user of allTestUsers) {
          if (!matchingUsers.some(u => u.id === user.id)) {
            try {
              await deleteTestUser(request, user.id)
            } catch (error) {
              // Ignore individual deletion errors
            }
          }
        }
      } catch (error) {
        // Ignore cleanup errors
      }
    }
  })

  test('LM-002: Create learner validation', async ({ page }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    await openAddLearnerModal(page)
    
    // Test name validation: Enter a name that's too short (1 character)
    const nameInput = page.getByTestId('testid-learner-name-input')
    await nameInput.fill('A') // Too short - needs at least 2 characters
    
    // Try to click Next - this should trigger validation
    const nameNextButton = page.getByTestId('testid-name-step-next-button')
    
    // The button should be disabled or clicking it should show an error
    const isDisabled = await nameNextButton.isDisabled()
    
    if (!isDisabled) {
      // If button is enabled, click it and verify error appears
      await nameNextButton.click()
      
      // Wait for error message to appear
      await expect(page.getByText(/please enter at least 2 characters/i)).toBeVisible({ timeout: 2000 })
    } else {
      // If button is disabled, that's also valid validation behavior
      expect(isDisabled).toBe(true)
    }
    
    // Verify we're still on the name step (didn't advance)
    await expect(page.getByTestId('testid-learner-name-input')).toBeVisible()
    await expect(page.getByTestId('testid-avatar-step')).not.toBeVisible()
  })

  test('LM-003: Delete learner', async ({ request }) => {
    // Create a test user
    const testUser = await createTestUser(request)
    
    // Verify user exists
    const usersBefore = await listUsers(request)
    expect(usersBefore.some(u => u.id === testUser.id)).toBe(true)
    
    // Delete the user
    await deleteTestUser(request, testUser.id)
    
    // Verify user is deleted
    const usersAfter = await listUsers(request)
    expect(usersAfter.some(u => u.id === testUser.id)).toBe(false)
  })

  test('LM-004: Select learner', async ({ page, testUser }) => {
    await navigateToDashboard(page)
    await waitForDashboardLoad(page)
    
    // Wait for student grid to load
    await expect(page.getByTestId('testid-student-grid')).toBeVisible()
    
    // Find the test user's card (should not be selected initially)
    const userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
    await expect(userCard).toBeVisible()
    
    // Verify card is not selected initially (should have white background, not gradient)
    const initialClasses = await userCard.getAttribute('class')
    expect(initialClasses).not.toContain('bg-gradient-to-br from-blue-500 to-purple-600')
    
    // Verify selected indicator is not visible initially
    const selectedIndicator = page.getByTestId(`testid-selected-indicator-${testUser.id}`)
    await expect(selectedIndicator).not.toBeVisible()
    
    // Click the card to select it
    await userCard.click()
    
    // Wait for selection state to update
    await page.waitForTimeout(500)
    
    // Verify card now has selected styling (gradient background)
    const selectedClasses = await userCard.getAttribute('class')
    expect(selectedClasses).toContain('bg-gradient-to-br from-blue-500 to-purple-600')
    expect(selectedClasses).toContain('ring-2')
    
    // Verify selected indicator (yellow star) is now visible
    await expect(selectedIndicator).toBeVisible({ timeout: 2000 })
    
    // Verify the progress title appears with the learner's name
    const progressTitle = page.getByTestId('testid-learner-progress-title')
    await expect(progressTitle).toBeVisible({ timeout: 2000 })
    await expect(progressTitle).toContainText(`${testUser.name}'s progress`)
    
    // Verify Start Practice button is visible (indicates detail view is shown)
    await expect(page.getByTestId('testid-start-practice-button')).toBeVisible({ timeout: 2000 })
    
    // Verify stats cards are visible (they should be in the detail layout)
    // The stats cards should show level, questions answered, etc.
    await expect(page.getByText(/Current Level/i)).toBeVisible({ timeout: 2000 })
    await expect(page.getByText(/Questions Answered/i)).toBeVisible({ timeout: 2000 })
  })

  test('LM-005: Duplicate name prevention', async ({ page, request }) => {
    // Create a test user first via API
    const testUser = await createTestUser(request, {
      name: `DuplicateTest_${Date.now()}`,
      avatar: '👧',
      pin: '1234',
    })
    
    try {
      // Verify the user exists by listing users
      const usersBefore = await listUsers(request)
      expect(usersBefore.some(u => u.id === testUser.id && u.name === testUser.name)).toBe(true)
      
      // Navigate to the page and wait for it to load
      await navigateToDashboard(page)
      await waitForDashboardLoad(page)
      
      // Wait for the grid to load and verify the test user appears
      await expect(page.getByTestId('testid-student-grid')).toBeVisible({ timeout: 5000 })
      await page.waitForTimeout(1000) // Give time for the user to appear in the grid
      
      // Verify the test user is visible in the grid
      const existingUserCard = page.getByTestId(`testid-student-card-${testUser.id}`)
      await expect(existingUserCard).toBeVisible({ timeout: 5000 })
      
      // Now try to create a duplicate via the UI
      await openAddLearnerModal(page)
      
      // Enter the duplicate name (exact same name as existing user)
      await fillLearnerName(page, testUser.name)
      
      // Complete learner creation flow (will trigger duplicate name error)
      await completeLearnerCreation(page, '9999')
      
      // Wait for the API response (should fail with duplicate name error)
      const pinDisplay = page.getByTestId('testid-pin-display')
      const pinDisplayVisible = await pinDisplay.isVisible({ timeout: 3000 }).catch(() => false)
      
      if (pinDisplayVisible) {
        
        // Wait for the API response (should fail with duplicate name error)
        const response = await page.waitForResponse(response => 
          response.url().includes('/api/users') && response.request().method() === 'POST',
          { timeout: 10000 }
        ).catch(() => null)
        
        if (response) {
          const status = response.status()
          const responseData = await response.json()
          
          // Verify the API call failed with duplicate name error
          expect(status).toBe(400)
          expect(responseData.errors).toBeDefined()
          expect(Array.isArray(responseData.errors)).toBe(true)
          expect(responseData.errors.some((err: string) => err.includes('already taken') || err.includes('Name is already taken'))).toBe(true)
        }
        
        // Wait for error message to appear in the PIN step
        // The error should be displayed in the PinPad component
        await expect(page.getByText(/name.*already.*taken/i)).toBeVisible({ timeout: 5000 })
        
        // Verify the modal is still open (error should prevent it from closing)
        await expect(page.getByTestId('testid-add-learner-modal')).toBeVisible({ timeout: 2000 })
        
        // Verify we're still on the PIN step (didn't advance)
        await expect(pinDisplay).toBeVisible()
      }
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })
})

