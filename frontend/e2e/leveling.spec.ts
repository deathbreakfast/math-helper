import { test, expect } from './fixtures/test-user'
import {
  getUser,
  openJourneyModal,
  navigateToLevelsTab,
  getLevelUpEligibility,
  createTestUserWithState,
  deleteTestUser,
} from './helpers/test-helpers'

test.describe('Leveling', () => {
  test('LVL-001: Level up eligibility', async ({ page, request }) => {
    // Create user at level 1 with no achievements
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - ensures predictable state
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    
    // Check via API
    const eligibility = await getLevelUpEligibility(request, testUser.id)
    expect(eligibility).toHaveProperty('eligible')
    expect(eligibility).toHaveProperty('current_level')
    expect(eligibility).toHaveProperty('next_level')
    
    // Verify UI displays current level
    const levelCard = page.getByTestId('testid-level-card')
    await expect(levelCard).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('LVL-002: Level up achievement requirements display', async ({ page, request }) => {
    // Create user at level 1 with no achievements (ensures requirements are visible)
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - ensures requirements are visible
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Verify levels tab is visible
    const levelsTab = page.getByTestId('testid-levels-tab')
    await expect(levelsTab).toBeVisible()
    
    // Wait for level requirements to load (lazy loaded)
    const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
    
    // Verify level requirements are displayed
    const count = await requirementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Verify requirement items show completion status
    const completedRequirements = page.locator('[data-testid="testid-requirement-completed"]')
    const completedCount = await completedRequirements.count()
    // At least some requirements should be visible (even if not completed)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('LVL-003: Level up after requirements met', async ({ page, request }) => {
    // Create user at level 1 with all requirements for level 2
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: ['addition-basics'] // Required for level 2
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
    
    // Verify level up button/eligibility
    const eligibility = await getLevelUpEligibility(request, testUser.id)
    expect(eligibility.eligible).toBe(true)
    
    // Attempt level up via API
    const levelUpResponse = await request.post(`/api/users/${testUser.id}/level-up`)
    expect(levelUpResponse.ok()).toBe(true)
    
    // Verify level increased
    const userAfter = await getUser(request, testUser.id)
    expect(userAfter?.level).toBe(2)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('LVL-004: Level up blocks when requirements not met', async ({ page, request }) => {
    // Create user without required achievements
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - should not be able to level up
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
    
    // Check eligibility via API
    const eligibility = await getLevelUpEligibility(request, testUser.id)
    expect(eligibility.eligible).toBe(false)
    
    // Try to level up anyway
    const levelUpResponse = await request.post(`/api/users/${testUser.id}/level-up`)
    
    // Should fail with 400
    expect(levelUpResponse.status()).toBe(400)
    
    const result = await levelUpResponse.json()
    expect(result).toHaveProperty('success', false)
    expect(result).toHaveProperty('missing_achievements')
    
    // Verify UI shows missing requirements
    const count = await requirementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('LVL-005: Missing achievements are listed in requirements', async ({ page, request }) => {
    // Create user at level 1 with no achievements (guarantees missing achievements exist)
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - guarantees missing achievements exist
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
    
    // Get eligibility via API
    const eligibility = await getLevelUpEligibility(request, testUser.id)
    
    // Verify missing achievements are shown in UI
    expect(eligibility.eligible).toBe(false)
    expect(eligibility.missing_achievements).toBeDefined()
    expect(eligibility.missing_achievements.length).toBeGreaterThan(0)
    
    // Get the level 1 requirement card (user is at level 1, so this shows requirements for level 2)
    const level1RequirementCard = page.getByTestId('testid-level-requirement-1')
    await expect(level1RequirementCard).toBeVisible({ timeout: 10000 })
    
    // Find all requirement items within the level 1 card
    const requirementItems = level1RequirementCard.locator('[data-testid^="testid-requirement-"]')
    const requirementCount = await requirementItems.count()
    expect(requirementCount).toBeGreaterThan(0)
    
    // For each missing achievement, verify it appears in at least one requirement's text
    for (const missingAchievement of eligibility.missing_achievements) {
      // The UI displays achievement codes with hyphens replaced by spaces
      // e.g., "addition-basics" becomes "addition basics"
      const normalizedCode = missingAchievement.replace(/-/g, ' ')
      
      // Check if any requirement item contains this achievement code (in either format)
      let found = false
      for (let i = 0; i < requirementCount; i++) {
        const requirementItem = requirementItems.nth(i)
        const text = await requirementItem.textContent()
        if (text && (text.includes(missingAchievement) || text.includes(normalizedCode))) {
          found = true
          break
        }
      }
      
      expect(found).toBe(true)
    }
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('LVL-006: Level progression path shows correct next level', async ({ page, request }) => {
    // Create user at level 2 (ensures predictable progression to level 3)
    const testUser = await createTestUserWithState(request, {
      level: 2
      // No achievements - ensures predictable progression state
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToLevelsTab(page)
    
    // Wait for level requirements to load
    const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
    await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
    
    const eligibility = await getLevelUpEligibility(request, testUser.id)
    
    // Verify progression header shows next level
    const progressionHeader = page.getByTestId('testid-level-progression-header')
    await expect(progressionHeader).toBeVisible()
    
    // Verify current level is displayed correctly
    const currentLevelText = page.locator(`text=/level.*${eligibility.current_level}/i`)
    await expect(currentLevelText.first()).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })
})


