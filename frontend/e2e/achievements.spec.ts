import { test, expect } from './fixtures/test-user'
import {
  createTestUserWithState,
  deleteTestUser,
  navigateToJourneyTab,
  navigateToDashboard,
  filterAchievementsByCategory,
  getAchievementStatus,
  waitForComponent,
  waitForFramerMotion,
  waitForDataLoad,
} from './helpers/test-helpers'

test.describe('Achievements', () => {
  test('ACH-001: Milestone achievements display', async ({ page, request }) => {
    // Create user with milestone achievements for better test visibility
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-victory', 'first-steps', 'century']
    })
    
    try {
      // Navigate directly to achievements tab using router
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'milestone' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
      
      // Verify at least one achievement card is present
      const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
      const count = await achievementCards.count()
      expect(count).toBeGreaterThan(0)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-002: Accuracy achievements display', async ({ page, request }) => {
    // Create user with accuracy achievement unlocked
    const testUser = await createTestUserWithState(request, {
      achievements: ['addition-basics', 'subtraction-basics']
    })
    
    try {
      // Navigate directly to achievements tab with accuracy filter
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'accuracy' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
      
      // Verify at least one achievement card is present
      const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
      const count = await achievementCards.count()
      expect(count).toBeGreaterThan(0)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-003: Speed achievements display', async ({ page, request }) => {
    // Create user with speed achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['fast-session-bronze', 'fast-session-silver']
    })
    
    try {
      // Navigate directly to achievements tab with speed filter
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'speed' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-004: Consistency achievements display', async ({ page, request }) => {
    // Create user with consistency achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['streak-2', 'streak-3']
    })
    
    try {
      // Navigate directly to achievements tab with consistency filter
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'consistency' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-005: Test tier achievements display', async ({ page, testUser, request }) => {
    // Award test achievements to existing test user
    const { awardAchievements } = await import('./helpers/test-helpers')
    await awardAchievements(request, testUser.id, [
      'multiply-by-two-test-a',
      'multiply-by-three-test-s'
    ])
    
    // Navigate directly to achievements tab with test filter
    await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'test' })
    
    // Wait for achievements grid to load
    await waitForComponent(page, 'testid-achievements-grid')
  })

  test('ACH-006: Level mastery achievements display', async ({ page, request }) => {
    // Create user with level mastery achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['level-2-mastery', 'level-5-mastery']
    })
    
    try {
      // Navigate directly to achievements tab with test-mastery filter
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'test-mastery' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-007: Progression achievements display', async ({ page, request }) => {
    // Create user with progression achievements
    const testUser = await createTestUserWithState(request, {
      achievements: ['perfect-sessions-2', 'perfect-sessions-5']
    })
    
    try {
      // Navigate directly to achievements tab with progression filter
      await navigateToJourneyTab(page, testUser.id, 'achievements', { category: 'progression' })
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-008: Achievement status display', async ({ page, request }) => {
    // Create user with mix of achievements
    const testUser = await createTestUserWithState(request, {
      // Use achievements that are guaranteed to exist and unlock as simple milestones
      achievements: ['first-steps', 'first-victory']
    })

    
    try {
      // Navigate directly to achievements tab
      await navigateToJourneyTab(page, testUser.id, 'achievements')
      
      // Wait for achievements grid to load with data
      await waitForDataLoad(page, 'testid-achievements-grid')
      await waitForFramerMotion(page)
      
      // Wait for specific achievement cards to be visible
      const firstStepsCard = page.getByTestId('testid-achievement-card-first-steps')
      const firstVictoryCard = page.getByTestId('testid-achievement-card-first-victory')
      
      // Wait for at least one of our specific achievements to appear
      await expect(
        firstStepsCard.or(firstVictoryCard).first()
      ).toBeVisible({ timeout: 10000 })
      
      // Wait for achievement cards to be ready
      const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
      await expect(achievementCards.first()).toBeVisible({ timeout: 5000 })
      
      const count = await achievementCards.count()
      expect(count).toBeGreaterThan(0)
      
      // Wait for animations to complete
      await waitForFramerMotion(page)
      
      // Verify locked/unlocked states render correctly.
      // Wait for the unlock icon inside a known-unlocked card. This is more reliable than
      // searching globally (which is timing-sensitive when lists are still hydrating).
      const unlockedInFirstSteps = firstStepsCard.getByTestId('testid-achievement-unlock-icon')
      const unlockedInFirstVictory = firstVictoryCard.getByTestId('testid-achievement-unlock-icon')

      await expect(unlockedInFirstSteps.or(unlockedInFirstVictory).first()).toBeVisible({ timeout: 15000 })
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-009: Achievement progress bars display', async ({ page, request }) => {
    // Create user (without achievements to see in-progress ones)
    const testUser = await createTestUserWithState(request, {})
    
    try {
      // Navigate directly to achievements tab
      await navigateToJourneyTab(page, testUser.id, 'achievements')
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
      
      // At least some achievements should be visible
      const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
      const cardCount = await achievementCards.count()
      expect(cardCount).toBeGreaterThan(0)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-010: Achievement filtering works', async ({ page, request }) => {
    // Create user with achievements in different categories
    const testUser = await createTestUserWithState(request, {
      achievements: [
        'first-victory', // milestone
        'addition-1digit-bronze', // test
        'speed-demon-bronze', // speed
        'week-warrior-bronze' // consistency
      ]
    })
    
    try {
      // Navigate directly to achievements tab
      await navigateToJourneyTab(page, testUser.id, 'achievements')
      
      // Wait for achievements grid to load
      await waitForComponent(page, 'testid-achievements-grid')
      
      // Test category filter
      await filterAchievementsByCategory(page, 'speed')
      await waitForFramerMotion(page)
      
      // Verify filtered achievements are shown
      const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
      const count = await achievementCards.count()
      expect(count).toBeGreaterThan(0)
      
      // Test status filter
      const statusFilter = page.getByTestId('testid-achievement-filter-status')
      await statusFilter.selectOption('unlocked')
      await waitForFramerMotion(page)
      
      // Test search filter
      const searchInput = page.getByTestId('testid-achievement-search-input')
      await searchInput.fill('speed')
      await waitForFramerMotion(page)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('ACH-011: Achievements display on dashboard', async ({ page, request }) => {
    // Create user with some achievements for better test visibility
    const testUser = await createTestUserWithState(request, {
      achievements: ['first-victory', 'first-steps']
    })
    
    try {
      // Navigate to dashboard with user selected
      await navigateToDashboard(page, testUser.id)
      
      // Wait for user card to be visible and click it
      const userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
        .filter({ hasText: testUser.name }).first()
      await expect(userCard).toBeVisible({ timeout: 5000 })
      await userCard.click()
      await waitForFramerMotion(page)
      
      // Verify achievements list is visible
      const achievementsList = page.getByTestId('testid-achievements-list')
      await expect(achievementsList).toBeVisible()
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })
})


