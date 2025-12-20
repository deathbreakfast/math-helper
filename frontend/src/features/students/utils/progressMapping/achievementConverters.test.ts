import { describe, it, expect, vi, beforeEach } from 'vitest'
import { convertBackendDefinitionToFrontend, convertBackendAchievementToFrontend } from './achievementConverters'
import * as achievementUtils from '../achievementUtils'

// Mock achievementUtils
vi.mock('../achievementUtils', () => ({
  extractTierFromCode: vi.fn((code: string) => {
    // Mock implementation: extract tier from code
    if (code.includes('-bronze')) return { baseCode: code.replace('-bronze', ''), tier: 'Bronze' }
    if (code.includes('-silver')) return { baseCode: code.replace('-silver', ''), tier: 'Silver' }
    if (code.includes('-gold')) return { baseCode: code.replace('-gold', ''), tier: 'Gold' }
    if (code.includes('-b')) return { baseCode: code.replace('-b', ''), tier: 'Bronze' }
    if (code.includes('-a')) return { baseCode: code.replace('-a', ''), tier: 'Silver' }
    if (code.includes('-s')) return { baseCode: code.replace('-s', ''), tier: 'Gold' }
    return { baseCode: code, tier: null }
  }),
  cleanTitle: vi.fn((title: string, tier: string | null) => {
    // Return title as-is for testing (the real implementation removes tier suffix)
    return title
  }),
}))

describe('achievementConverters', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('convertBackendDefinitionToFrontend', () => {
    it('should convert backend definition to frontend format', () => {
      const definition = {
        title: 'Test Achievement',
        description: 'Test description',
        icon: '⭐',
        category: 'milestone',
      }

      const result = convertBackendDefinitionToFrontend('test-achievement', definition, [])

      expect(result.id).toBe('test-achievement')
      expect(result.title).toBe('Test Achievement')
      expect(result.description).toBe('Test description')
      expect(result.icon).toBe('⭐')
      expect(result.type).toBe('milestone')
      expect(result.status).toBe('locked')
      expect(result.progress).toBe(0)
    })

    it('should mark achievement as unlocked if user has earned it', () => {
      const definition = {
        title: 'Test Achievement',
        description: 'Test description',
        category: 'milestone',
      }

      const userAchievements = [
        { code: 'test-achievement', earnedAt: new Date('2024-01-01') },
      ]

      const result = convertBackendDefinitionToFrontend('test-achievement', definition, userAchievements)

      expect(result.status).toBe('unlocked')
      expect(result.progress).toBe(1)
      expect(result.unlockedAt).toBeInstanceOf(Date)
      expect(result.count).toBe(1)
    })

    it('should map category to correct type', () => {
      const categories = [
        { category: 'speed', expectedType: 'speed-session' },
        { category: 'consistency', expectedType: 'streak' },
        { category: 'accuracy', expectedType: 'milestone' },
        { category: 'test', expectedType: 'test-completion' },
        { category: 'milestone', expectedType: 'milestone' },
      ]

      categories.forEach(({ category, expectedType }) => {
        const definition = { title: 'Test', category }
        const result = convertBackendDefinitionToFrontend('test', definition, [])
        expect(result.type).toBe(expectedType)
      })
    })

    it('should extract tier from code when available', () => {
      const definition = { title: 'Test', category: 'milestone' }
      const result = convertBackendDefinitionToFrontend('test-bronze', definition, [])
      expect(achievementUtils.extractTierFromCode).toHaveBeenCalledWith('test-bronze')
      // Tier will be set based on mock result
    })

    it('should use fallback tier logic for non-tiered achievements', () => {
      vi.mocked(achievementUtils.extractTierFromCode).mockReturnValue({ baseCode: 'accuracy-ace', tier: null })
      
      const definition = { title: 'Accuracy Ace', category: 'accuracy' }
      const result = convertBackendDefinitionToFrontend('accuracy-ace', definition, [])

      expect(result.tier).toBe('Silver') // From fallback logic
    })

    it('should handle first-steps achievement', () => {
      vi.mocked(achievementUtils.extractTierFromCode).mockReturnValue({ baseCode: 'first-steps', tier: null })
      
      const definition = { title: 'First Steps', category: 'milestone' }
      const result = convertBackendDefinitionToFrontend('first-steps', definition, [])

      expect(result.tier).toBe('Bronze')
    })

    it('should handle streak achievements', () => {
      vi.mocked(achievementUtils.extractTierFromCode).mockReturnValue({ baseCode: 'streak-10', tier: null })
      
      const definition = { title: 'Streak 10', category: 'consistency' }
      const result = convertBackendDefinitionToFrontend('streak-10', definition, [])

      expect(result.tier).toBe('Gold')
    })

    it('should count multiple achievements with same code', () => {
      const definition = { title: 'Test', category: 'milestone' }
      const userAchievements = [
        { code: 'test-achievement', earnedAt: new Date('2024-01-01') },
        { code: 'test-achievement', earnedAt: new Date('2024-01-02') },
        { code: 'test-achievement', earnedAt: new Date('2024-01-03') },
      ]

      const result = convertBackendDefinitionToFrontend('test-achievement', definition, userAchievements)

      expect(result.count).toBe(3)
    })

    it('should extract test type and performance tier from test achievements', () => {
      const definition = { title: 'Test Achievement', category: 'test' }
      const result = convertBackendDefinitionToFrontend('addition-1digit-b', definition, [])

      expect(result.testType).toBe('addition-1digit')
      expect(result.performanceTier).toBe('B')
    })

    it('should handle test achievements with multi-character tier suffixes', () => {
      const definition = { title: 'Test Achievement', category: 'test' }
      const result = convertBackendDefinitionToFrontend('addition-1digit-sss', definition, [])

      expect(result.testType).toBe('addition-1digit')
      expect(result.performanceTier).toBe('SSS')
    })

    it('should use code as title if title is missing', () => {
      const definition = { description: 'Test', category: 'milestone' }
      const result = convertBackendDefinitionToFrontend('test-achievement', definition, [])

      expect(result.title).toBe('test-achievement')
    })

    it('should clean title to remove tier suffix', () => {
      vi.mocked(achievementUtils.cleanTitle).mockReturnValue('Test Achievement')
      
      const definition = { title: 'Test Achievement (Bronze)', category: 'milestone' }
      convertBackendDefinitionToFrontend('test-bronze', definition, [])

      expect(achievementUtils.cleanTitle).toHaveBeenCalledWith('Test Achievement (Bronze)', 'Bronze')
    })

    it('should provide default icon if missing', () => {
      const definition = { title: 'Test', category: 'milestone' }
      const result = convertBackendDefinitionToFrontend('test', definition, [])

      expect(result.icon).toBe('🏆')
    })

    it('should format Lightning Fast requirement with min_questions and max_speed_seconds', () => {
      const definition = {
        title: 'Lightning Fast (Bronze)',
        description: 'Average <5s per question at a specific level',
        category: 'speed',
        requirements: {
          max_speed_seconds: 5.0,
          min_questions: 50,
        },
      }

      const result = convertBackendDefinitionToFrontend('lightning-fast-bronze', definition, [])

      expect(result.requirement).toBe('Avg <5s/question with 50+ correct (per level)')
    })

    it('should format Lightning Fast requirement with only max_speed_seconds if min_questions missing', () => {
      const definition = {
        title: 'Lightning Fast (Bronze)',
        description: 'Average <5s per question at a specific level',
        category: 'speed',
        requirements: {
          max_speed_seconds: 5.0,
        },
      }

      const result = convertBackendDefinitionToFrontend('lightning-fast-bronze', definition, [])

      expect(result.requirement).toBe('Avg <5s/question (per level)')
    })

    it('should use description as requirement for non-Lightning Fast achievements', () => {
      const definition = {
        title: 'Test Achievement',
        description: 'Test description',
        category: 'milestone',
        requirements: {
          some_field: 'value',
        },
      }

      const result = convertBackendDefinitionToFrontend('test-achievement', definition, [])

      expect(result.requirement).toBe('Test description')
    })
  })

  describe('convertBackendAchievementToFrontend', () => {
    it('should convert backend achievement to frontend format', () => {
      const backendAchievement = {
        code: 'test-achievement',
        title: 'Test Achievement',
        description: 'Test description',
        icon: '⭐',
        category: 'milestone',
        earnedAt: new Date('2024-01-01'),
      }

      const result = convertBackendAchievementToFrontend(backendAchievement, [])

      expect(result.id).toBe('test-achievement')
      expect(result.title).toBe('Test Achievement') // Title is cleaned, but mock returns title as-is
      expect(result.status).toBe('unlocked')
      expect(result.unlockedAt).toBeInstanceOf(Date)
    })

    it('should always mark as unlocked', () => {
      const backendAchievement = {
        code: 'test',
        category: 'milestone',
      }

      const result = convertBackendAchievementToFrontend(backendAchievement, [])

      expect(result.status).toBe('unlocked')
      expect(result.progress).toBe(1)
    })

    it('should count achievements with same code', () => {
      const backendAchievement = {
        code: 'test-achievement',
        category: 'milestone',
      }

      const userAchievements = [
        { code: 'test-achievement', earnedAt: new Date('2024-01-01') },
        { code: 'test-achievement', earnedAt: new Date('2024-01-02') },
      ]

      const result = convertBackendAchievementToFrontend(backendAchievement, userAchievements)

      expect(result.count).toBe(2)
    })

    it('should handle missing fields with defaults', () => {
      // Reset mock to return input as-is
      vi.mocked(achievementUtils.cleanTitle).mockImplementation((title: string) => title)

      const backendAchievement = {
        code: 'test-code',
      }

      const result = convertBackendAchievementToFrontend(backendAchievement, [])

      // Title uses code if title is missing (backendAchievement.title || code)
      // Since title is missing, it should use code 'test-code'
      // Then cleanTitle is called, which our mock returns as-is
      expect(result.title).toBe('test-code')
      expect(result.description).toBe('')
      expect(result.icon).toBe('🏆')
      expect(result.category).toBe('milestone')
    })

    it('should map category to correct type', () => {
      const categories = [
        { category: 'speed', expectedType: 'speed-session' },
        { category: 'consistency', expectedType: 'streak' },
        { category: 'accuracy', expectedType: 'milestone' },
        { category: 'test', expectedType: 'test-completion' },
      ]

      categories.forEach(({ category, expectedType }) => {
        const backendAchievement = { code: 'test', category }
        const result = convertBackendAchievementToFrontend(backendAchievement, [])
        expect(result.type).toBe(expectedType)
      })
    })
  })
})




