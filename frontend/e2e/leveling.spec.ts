import { test, expect } from './fixtures/test-user'
import {
  getLevelUpEligibility,
  createTestUserWithState,
  deleteTestUser,
  waitForComponent,
  navigateToJourneyTab,
} from './helpers/test-helpers'

test.describe('Leveling', () => {
  test('LVL-001: Level up eligibility', async ({ page, request }) => {
    // Create user at level 1 with no achievements
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - ensures predictable state
    })
    
    try {
      // Navigate directly to journey overview
      await navigateToJourneyTab(page, testUser.id, 'overview')
      
      // Check via API
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      expect(eligibility).toHaveProperty('eligible')
      expect(eligibility).toHaveProperty('current_level')
      expect(eligibility).toHaveProperty('next_level')
      
      // Verify UI displays current level
      // Journey page shows level in JourneyHeader, not in LearnerStatsCards
      await waitForComponent(page, 'testid-current-level-display')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  // LVL-002 through LVL-006 removed - levels tab was deprecated (levels are now shown as cards in journey, not a separate tab)
})


