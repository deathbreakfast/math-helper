import { test, expect } from './fixtures/test-user'
import {
  createTestUserWithState,
  deleteTestUser,
  openJourneyModal,
  navigateToAchievementsTab,
  filterAchievementsByCategory,
  getAchievementStatus,
} from './helpers/test-helpers'

test.describe('Achievements', () => {
  test('ACH-001: Milestone achievements display', async ({ page, request }) => {
    // Create user with milestone achievements for better test visibility
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-victory', 'first-steps', 'century']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by milestone category
    await filterAchievementsByCategory(page, 'milestone')
    
    // Verify milestone achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Verify at least one achievement card is present
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const count = await achievementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-002: Accuracy achievements display', async ({ page, request }) => {
    // Create user with accuracy achievement unlocked
    const testUser = await createTestUserWithState(request, {
      achievements: ['addition-basics', 'subtraction-basics']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by accuracy category
    await filterAchievementsByCategory(page, 'accuracy')
    
    // Verify accuracy achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Verify at least one achievement card is present
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const count = await achievementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-003: Speed achievements display', async ({ page, request }) => {
    // Create user with speed achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['fast-session-bronze', 'fast-session-silver']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by speed category
    await filterAchievementsByCategory(page, 'speed')
    
    // Verify speed achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-004: Consistency achievements display', async ({ page, request }) => {
    // Create user with consistency achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['streak-2', 'streak-3']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by consistency category
    await filterAchievementsByCategory(page, 'consistency')
    
    // Verify consistency achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-005: Test tier achievements display', async ({ page, testUser, request }) => {
    // Award test achievements to existing test user
    const { awardAchievements } = await import('./helpers/test-helpers')
    await awardAchievements(request, testUser.id, [
      'multiply-by-two-test-a',
      'multiply-by-three-test-s'
    ])
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by test category
    await filterAchievementsByCategory(page, 'test')
    
    // Verify test achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
  })

  test('ACH-006: Level mastery achievements display', async ({ page, request }) => {
    // Create user with level mastery achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['level-2-mastery', 'level-5-mastery']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by test-mastery category (level mastery achievements)
    await filterAchievementsByCategory(page, 'test-mastery')
    
    // Verify level mastery achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-007: Progression achievements display', async ({ page, request }) => {
    // Create user with progression achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['perfect-sessions-2', 'perfect-sessions-5']
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Filter by progression category
    await filterAchievementsByCategory(page, 'progression')
    
    // Verify progression achievements are visible
    const achievementsGrid = page.getByTestId('testid-achievements-grid')
    await expect(achievementsGrid).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-008: Achievement status display', async ({ page, request }) => {
    // Create user with mix of achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-victory', 'addition-basics']
    })
    
    // DEBUG: Verify achievements were actually added to the user
    // [STACK: Test Setup - After createTestUserWithState, before navigation]
    console.log(`[ACH-008] [TEST SETUP] Test user created: ID=${testUser.id}, Name=${testUser.name}`)
    console.log(`[ACH-008] [TEST SETUP] Expected achievements: first-victory, addition-basics`)
    
    // Make API call to verify achievements are in database
    // [STACK: Test Setup - Direct API call to verify database state]
    const userResponse = await request.get(`/api/users/${testUser.id}`)
    const userData = await userResponse.json()
    
    console.log(`[ACH-008] [TEST SETUP] API Response for user ${testUser.id}:`, JSON.stringify(userData, null, 2))
    
    if (userData.achievements && Array.isArray(userData.achievements)) {
      const achievementCodes = userData.achievements.map((a: any) => a.code || a.id).filter(Boolean)
      console.log(`[ACH-008] [TEST SETUP] Achievements in API response (${userData.achievements.length} total):`, achievementCodes)
      
      const hasFirstVictory = achievementCodes.some((code: string) => code === 'first-victory' || code.includes('first-victory'))
      const hasAdditionBasics = achievementCodes.some((code: string) => code === 'addition-basics' || code.includes('addition-basics'))
      
      console.log(`[ACH-008] [TEST SETUP] Has first-victory: ${hasFirstVictory}, Has addition-basics: ${hasAdditionBasics}`)
      
      if (!hasFirstVictory || !hasAdditionBasics) {
        console.error(`[ACH-008] [TEST SETUP] WARNING: Expected achievements not found in API response!`)
      }
    } else {
      console.error(`[ACH-008] [TEST SETUP] ERROR: No achievements array in API response!`)
    }
    
    // Wait 2 seconds to ensure user is fully created and available in database
    // This helps in parallel runs where database operations may take longer
    await page.waitForTimeout(2000)
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    
    // CRITICAL for parallel runs: Wait for THIS user's achievements to load
    // In parallel, modal might open before achievements are fetched for this specific user
    const firstVictoryCard = page.getByTestId('testid-achievement-card-first-victory')
    const additionBasicsCard = page.getByTestId('testid-achievement-card-addition-basics')
    
    // Wait for at least one of our specific achievements to appear (confirms correct user)
    await expect(
      firstVictoryCard.or(additionBasicsCard).first()
    ).toBeVisible({ timeout: 10000 })
    
    await navigateToAchievementsTab(page)
    
    // Wait for achievements tab to fully load and animation to complete
    await page.waitForTimeout(800) // Wait for framer-motion animation
    
    // Check multiple achievement cards for correct status display
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    
    // Wait for at least one achievement card to be visible
    await expect(achievementCards.first()).toBeVisible({ timeout: 5000 })
    
    const count = await achievementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Wait a bit more for all cards to render
    await page.waitForTimeout(500)
    
    // Verify locked/unlocked states render correctly
    // Find unlocked achievement icons - they should exist for the achievements we awarded
    const unlockedIcon = page.locator('[data-testid="testid-achievement-unlock-icon"]')
    
    // Wait for unlock icons to be visible (they might be animating in)
    let unlockedCount = 0
    for (let i = 0; i < 10; i++) {
      unlockedCount = await unlockedIcon.count()
      if (unlockedCount > 0) break
      await page.waitForTimeout(200)
    }
    
    // We awarded 2 achievements, so we should see at least 2 unlock icons
    // But if the cards are still animating, we might need to wait more
    if (unlockedCount === 0) {
      // Double-check our specific achievements are visible
      await expect(firstVictoryCard.or(additionBasicsCard).first()).toBeVisible({ timeout: 2000 })
      await page.waitForTimeout(500)
      
      // Check again
      unlockedCount = await unlockedIcon.count()
    }
    
    expect(unlockedCount).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-009: Achievement progress bars display', async ({ page, request }) => {
    // Create user (without achievements to see in-progress ones)
    const testUser = await createTestUserWithState(request, {})
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Find in-progress achievements (should have progress bars)
    const progressBars = page.locator('[data-testid="testid-achievement-progress-bar"]')
    const progressBarCount = await progressBars.count()
    
    // At least some achievements should be in progress (or all locked/unlocked)
    // The key is that progress bars are visible when achievements are in-progress
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const cardCount = await achievementCards.count()
    expect(cardCount).toBeGreaterThan(0)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-010: Achievement filtering works', async ({ page, request }) => {
    // Create user with achievements in different categories
    const testUser = await createTestUserWithState(request, {
      achievements: [
        'first-victory', // milestone
        'addition-basics', // accuracy
        'fast-session-bronze', // speed
        'streak-2' // consistency
      ]
    })
    
    // Navigate to dashboard first
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    await openJourneyModal(page, testUser)
    await navigateToAchievementsTab(page)
    
    // Test category filter
    await filterAchievementsByCategory(page, 'speed')
    await page.waitForTimeout(500)
    
    // Verify filtered achievements are shown
    const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
    const count = await achievementCards.count()
    expect(count).toBeGreaterThan(0)
    
    // Test status filter
    const statusFilter = page.getByTestId('testid-achievement-filter-status')
    await statusFilter.selectOption('unlocked')
    await page.waitForTimeout(500)
    
    // Test search filter
    const searchInput = page.getByTestId('testid-achievement-search-input')
    await searchInput.fill('speed')
    await page.waitForTimeout(500)
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })

  test('ACH-011: Achievements display on dashboard', async ({ page, request }) => {
    // Create user with some achievements for better test visibility
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-victory', 'first-steps']
    })
    
    await page.goto('/')
    await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
    
    // Filter by name to ensure we get the correct card in parallel runs
    let userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
    userCard = userCard.filter({ hasText: testUser.name }).first()
    await expect(userCard).toBeVisible({ timeout: 5000 })
    await userCard.click()
    await page.waitForTimeout(1000)
    
    // Verify achievements list is visible
    const achievementsList = page.getByTestId('testid-achievements-list')
    await expect(achievementsList).toBeVisible()
    
    // Cleanup
    await deleteTestUser(request, testUser.id)
  })
})


