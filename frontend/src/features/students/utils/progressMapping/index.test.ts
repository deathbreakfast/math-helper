import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mapUserToProgressData } from './index'
import * as achievementConverters from './achievementConverters'
import * as levelRequirementConverters from './levelRequirementConverters'

// Mock converters
vi.mock('./achievementConverters', () => ({
  convertBackendDefinitionToFrontend: vi.fn((code, def, achievements) => ({
    id: code,
    title: def.title || code,
    description: def.description || '',
    icon: def.icon || '🏆',
    type: 'milestone',
    tier: 'Bronze',
    requirement: def.description || '',
    status: achievements.some((a: any) => a.code === code) ? 'unlocked' : 'locked',
    progress: achievements.some((a: any) => a.code === code) ? 1 : 0,
    maxProgress: 1,
    unlockedAt: achievements.find((a: any) => a.code === code)?.earnedAt,
    isHidden: false,
    category: def.category || 'milestone',
    count: achievements.filter((a: any) => a.code === code).length,
    lastEarnedAt: achievements.find((a: any) => a.code === code)?.earnedAt,
    metadata: undefined,
  })),
  convertBackendAchievementToFrontend: vi.fn((achievement, allAchievements) => ({
    id: achievement.code || '',
    title: achievement.title || achievement.code || '',
    description: achievement.description || '',
    icon: achievement.icon || '🏆',
    type: 'milestone',
    tier: 'Bronze',
    requirement: achievement.description || '',
    status: 'unlocked',
    progress: 1,
    maxProgress: 1,
    unlockedAt: achievement.earnedAt,
    isHidden: false,
    category: achievement.category || 'milestone',
    count: allAchievements.filter((a: any) => a.code === achievement.code).length,
    lastEarnedAt: achievement.earnedAt,
    metadata: undefined,
  })),
}))

vi.mock('./levelRequirementConverters', () => ({
  convertBackendRequirementsToFrontend: vi.fn((requirements, achievements, level, nextLevel) => ({
    id: `l${level}-${nextLevel}`,
    level,
    nextLevel,
    title: `Reach Level ${nextLevel}`,
    requirements: requirements.map((req: any) => ({
      description: `Complete: ${req.achievement_code}`,
      achievementIds: [],
      achievementCode: req.achievement_code,
      completed: achievements.some((a: any) => a.code === req.achievement_code),
      progress: achievements.filter((a: any) => a.code === req.achievement_code).length,
      maxProgress: req.quantity || 1,
    })),
    isLocked: level > nextLevel - 1,
  })),
}))

describe('progressMapping/index', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('mapUserToProgressData', () => {
    const mockUser = {
      id: '1',
      name: 'Test User',
      avatar: '👧',
      level: 2,
      questionsAnswered: 50,
      averageSpeed: 3000,
      stats: {
        currentStreak: 5,
        bestStreak: 10,
        additionAccuracy: 90,
        subtractionAccuracy: 85,
        multiplicationAccuracy: 80,
        divisionAccuracy: 75,
        additionSpeed: 3000,
        subtractionSpeed: 3500,
        multiplicationSpeed: 4000,
        divisionSpeed: 4500,
      },
      achievements: [
        {
          code: 'test-achievement',
          title: 'Test Achievement',
          earnedAt: new Date('2024-01-01'),
        },
      ],
    }

    it('should map basic user data', () => {
      const result = mapUserToProgressData(mockUser)

      expect(result.id).toBe('1')
      expect(result.name).toBe('Test User')
      expect(result.avatar).toBe('👧')
      expect(result.level).toBe(2)
      expect(result.currentStreak).toBe(5)
      expect(result.bestStreak).toBe(10)
      expect(result.totalQuestions).toBe(50)
      expect(result.fastestQuestion).toBe(3000)
    })

    it('should use achievement definitions when provided', () => {
      const achievementDefinitions = {
        'test-achievement': {
          title: 'Test Achievement',
          description: 'Test description',
          icon: '⭐',
          category: 'milestone',
        },
        'other-achievement': {
          title: 'Other Achievement',
          description: 'Other description',
          icon: '🌟',
          category: 'speed',
        },
      }

      const result = mapUserToProgressData(mockUser, undefined, achievementDefinitions)

      expect(achievementConverters.convertBackendDefinitionToFrontend).toHaveBeenCalledTimes(2)
      expect(result.achievements).toHaveLength(2)
    })

    it('should use fallback conversion when definitions not provided', () => {
      const result = mapUserToProgressData(mockUser)

      expect(achievementConverters.convertBackendAchievementToFrontend).toHaveBeenCalled()
      expect(result.achievements).toHaveLength(1)
    })

    it('should deduplicate achievements in fallback mode', () => {
      const userWithDuplicates = {
        ...mockUser,
        achievements: [
          { code: 'test-achievement', title: 'Test', earnedAt: new Date('2024-01-01') },
          { code: 'test-achievement', title: 'Test', earnedAt: new Date('2024-01-02') },
        ],
      }

      const result = mapUserToProgressData(userWithDuplicates)

      expect(result.achievements).toHaveLength(1)
    })

    // Level requirement tests removed - level requirements are no longer used
    // levelRequirements array is always empty now

    it('should handle empty achievements array', () => {
      const userWithoutAchievements = {
        ...mockUser,
        achievements: [],
      }

      const result = mapUserToProgressData(userWithoutAchievements)

      expect(result.achievements).toEqual([])
    })

    it('should handle missing stats gracefully', () => {
      const userWithoutStats = {
        ...mockUser,
        stats: {
          currentStreak: 0,
          bestStreak: 0,
          additionAccuracy: 0,
          subtractionAccuracy: 0,
          multiplicationAccuracy: 0,
          divisionAccuracy: 0,
          additionSpeed: 0,
          subtractionSpeed: 0,
          multiplicationSpeed: 0,
          divisionSpeed: 0,
        },
      }

      const result = mapUserToProgressData(userWithoutStats)

      expect(result.currentStreak).toBe(0)
      expect(result.bestStreak).toBe(0)
    })

    it('should always have empty level requirements', () => {
      const result = mapUserToProgressData(mockUser, {})

      expect(result.levelRequirements).toHaveLength(0)
    })
  })
})




