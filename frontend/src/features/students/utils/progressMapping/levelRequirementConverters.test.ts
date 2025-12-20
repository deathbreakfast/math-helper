import { describe, it, expect, vi, beforeEach } from 'vitest'
import { convertBackendRequirementsToFrontend } from './levelRequirementConverters'
import * as achievementMapping from '../../../../lib/levels/achievementMapping'

// Mock dependencies
vi.mock('../../../../lib/levels/achievementMapping', () => ({
  ACHIEVEMENT_CODE_TO_FRONTEND_ID: {
    'test-achievement': 'test-id',
    'multi-achievement': ['id1', 'id2'],
  },
}))

describe('levelRequirementConverters', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('convertBackendRequirementsToFrontend', () => {
    it('should convert backend requirements to frontend format', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.id).toBe('l1-2')
      expect(result.level).toBe(1)
      expect(result.nextLevel).toBe(2)
      expect(result.title).toBe('Reach Level 2')
      expect(result.requirements).toHaveLength(1)
    })

    it('should map achievement codes to frontend IDs', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].achievementIds).toEqual(['test-id'])
      expect(result.requirements[0].achievementCode).toBe('test-achievement')
    })

    it('should handle multiple achievement IDs for a single code', () => {
      const backendRequirements = [
        {
          achievement_code: 'multi-achievement',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].achievementIds).toEqual(['id1', 'id2'])
    })

    it('should calculate progress based on user achievements', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      const userAchievements = [
        { code: 'test-achievement', title: 'Test Achievement' },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, userAchievements, 1, 2)

      expect(result.requirements[0].completed).toBe(true)
      expect(result.requirements[0].progress).toBe(1)
      expect(result.requirements[0].maxProgress).toBe(1)
    })

    it('should handle quantity requirements', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
          quantity: 3,
        },
      ]

      const userAchievements = [
        { code: 'test-achievement', title: 'Test' },
        { code: 'test-achievement', title: 'Test' },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, userAchievements, 1, 2)

      expect(result.requirements[0].completed).toBe(false)
      expect(result.requirements[0].progress).toBe(2)
      expect(result.requirements[0].maxProgress).toBe(3)
    })

    it('should include quantity in description when > 1', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
          quantity: 3,
        },
      ]

      const userAchievements = [
        { code: 'test-achievement', title: 'Test Achievement' },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, userAchievements, 1, 2)

      expect(result.requirements[0].description).toContain('(1/3)')
    })

    it('should use achievement title in description when available', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      const userAchievements = [
        { code: 'test-achievement', title: 'Test Achievement' },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, userAchievements, 1, 2)

      expect(result.requirements[0].description).toContain('Complete: Test Achievement')
    })

    it('should use code-based description when title not available', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement-code',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].description).toContain('Complete achievement: test achievement code')
    })

    it('should add test type to description from metadata filter', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
          metadata_filter: {
            concept_id: 'c_concept_001',
          },
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].description).toContain('(Basic Single Digit Addition)')
    })

    it('should add level to description from metadata filter', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
          metadata_filter: {
            level: 5,
          },
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].description).toContain('(Level 5)')
    })

    it('should combine test type and level in description', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
          metadata_filter: {
            concept_id: 'c_concept_001',
            level: 5,
          },
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].description).toContain('(Basic Single Digit Addition, Level 5)')
    })

    it('should set isLocked correctly', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      // Level 1 -> Level 2: should not be locked (level <= nextLevel - 1)
      const result1 = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)
      expect(result1.isLocked).toBe(false)

      // Level 2 -> Level 3: should not be locked (level <= nextLevel - 1)
      const result2 = convertBackendRequirementsToFrontend(backendRequirements, [], 2, 3)
      expect(result2.isLocked).toBe(false)

      // Level 3 -> Level 2: should be locked (level > nextLevel - 1)
      const result3 = convertBackendRequirementsToFrontend(backendRequirements, [], 3, 2)
      expect(result3.isLocked).toBe(true)
    })

    it('should handle multiple requirements', () => {
      const backendRequirements = [
        {
          achievement_code: 'achievement-1',
          order: 1,
        },
        {
          achievement_code: 'achievement-2',
          order: 2,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements).toHaveLength(2)
    })

    it('should default quantity to 1 when not specified', () => {
      const backendRequirements = [
        {
          achievement_code: 'test-achievement',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].maxProgress).toBe(1)
    })

    it('should handle empty requirements array', () => {
      const result = convertBackendRequirementsToFrontend([], [], 1, 2)

      expect(result.requirements).toEqual([])
    })

    it('should handle missing achievement mapping gracefully', () => {
      const backendRequirements = [
        {
          achievement_code: 'unknown-achievement',
          order: 1,
        },
      ]

      const result = convertBackendRequirementsToFrontend(backendRequirements, [], 1, 2)

      expect(result.requirements[0].achievementIds).toBeUndefined()
      expect(result.requirements[0].achievementCode).toBe('unknown-achievement')
    })
  })
})




