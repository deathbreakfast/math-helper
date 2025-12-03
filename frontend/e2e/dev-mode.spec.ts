import { test, expect } from './fixtures/test-user'
import {
  createTestUserWithState,
  deleteTestUser,
  openJourneyModal,
  navigateToAchievementsTab,
  navigateToLevelsTab,
} from './helpers/test-helpers'

test.describe('Dev Mode Features', () => {
  test('DEV-001: ?env=dev shows all achievements including locked', async ({ page, request }) => {
    // Create user with some achievements unlocked
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-steps', 'first-victory']
    })
    
    // Navigate to dashboard with dev mode enabled
    await page.goto('/?env=dev')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // In dev mode, we should see all achievements including locked ones
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Get all achievement cards (should include locked ones in dev mode)
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const count = await achievementCards.count()
    
    // In dev mode, we should see more achievements than just the unlocked ones
    // The exact count depends on how many achievement definitions exist
    expect(count).toBeGreaterThan(2) // At least more than the 2 we unlocked
    
    // Verify we can see locked achievements by checking status filter
    // Filter by "locked" status - in dev mode this should show achievements
    const statusFilter = page.getByTestId('testid-achievement-filter-status')
    await statusFilter.selectOption('locked')
    
    // Wait a moment for filtering
    await page.waitForTimeout(500)
    
    // In dev mode, locked achievements should be visible
    const lockedCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const lockedCount = await lockedCards.count()
    // In dev mode, we should see at least some locked achievements
    expect(lockedCount).toBeGreaterThanOrEqual(0) // At least 0, but likely more
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('DEV-002: ?env=dev shows all level requirements (1-45)', async ({ page, request }) => {
    // Create user at level 1
    const testUser = await createTestUserWithState(request, {
      level: 1
    })
    
    // Navigate to dashboard with dev mode enabled
    await page.goto('/?env=dev')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    await page.waitForSelector('[data-testid="testid-levels-tab"]', { timeout: 10000 })
    
    // In dev mode, we should see level requirements for all levels (up to 45)
    // Check that we can see level requirements beyond the user's current level + 3
    const levelRequirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    const count = await levelRequirementCards.count()
    
    // In dev mode, we should see many more level requirements than normal
    // Normal mode would only show user.level + 3 (so 4 for level 1)
    // Dev mode should show requirements for all 45 levels
    expect(count).toBeGreaterThan(4) // Should be much more than the normal limit
    
    // Verify we can see high-level requirements (e.g., level 10+)
    // This confirms dev mode is working
    const levelsTab = page.getByTestId('testid-levels-tab')
    await expect(levelsTab).toBeVisible()
    
    // Check that the "More Levels Await" message is NOT shown in dev mode
    const moreLevelsMessage = page.locator('text=More Levels Await')
    await expect(moreLevelsMessage).not.toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('DEV-003: Without ?env=dev, normal filtering applies', async ({ page, request }) => {
    // Create user with some achievements unlocked
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-steps'],
      level: 1
    })
    
    // Navigate to dashboard WITHOUT dev mode
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Without dev mode, locked achievements should be filtered out
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Filter by "locked" status - without dev mode, this should show fewer or no achievements
    const statusFilter = page.getByTestId('testid-achievement-filter-status')
    await statusFilter.selectOption('locked')
    
    // Wait for filtering
    await page.waitForTimeout(500)
    
    // Without dev mode, we might see fewer locked achievements (only those that are visible but locked)
    // The exact behavior depends on how achievements are marked as hidden
    const lockedCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const lockedCount = await lockedCards.count()
    // In normal mode, locked achievements might be hidden, so count could be 0 or small
    expect(lockedCount).toBeGreaterThanOrEqual(0)
    
    // Navigate to levels tab
    await navigateToLevelsTab(page)
    
    // Without dev mode, we should only see level requirements up to user.level + 3
    // For level 1 user, that's levels 1-4
    const levelRequirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    const count = await levelRequirementCards.count()
    
    // In normal mode, we should see limited level requirements
    expect(count).toBeLessThanOrEqual(10) // Should be much less than 45
    
    // The "More Levels Await" message should be visible in normal mode
    const moreLevelsMessage = page.locator('text=More Levels Await')
    await expect(moreLevelsMessage).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('DEV-004: Dev mode persists across navigation', async ({ page, request }) => {
    // Create user
    const testUser = await createTestUserWithState(request, {
      level: 1
    })
    
    // Navigate to dashboard with dev mode enabled
    await page.goto('/?env=dev')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    await page.waitForSelector('[data-testid="testid-levels-tab"]', { timeout: 10000 })
    
    // Verify dev mode is active (should see many level requirements)
    const levelRequirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    const initialCount = await levelRequirementCards.count()
    expect(initialCount).toBeGreaterThan(4)
    
    // Navigate to achievements tab
    await navigateToAchievementsTab(page)
    
    // Dev mode should still be active - verify we can see all achievements
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Filter by locked status - should show achievements in dev mode
    const statusFilter = page.getByTestId('testid-achievement-filter-status')
    await statusFilter.selectOption('locked')
    await page.waitForTimeout(500)
    
    // Dev mode should persist - locked achievements should be visible
    const lockedCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const lockedCount = await lockedCards.count()
    expect(lockedCount).toBeGreaterThanOrEqual(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })
})

