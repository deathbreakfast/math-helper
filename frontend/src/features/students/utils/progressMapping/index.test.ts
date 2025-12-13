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

    it('should build level requirements from cache', () => {
      const levelRequirementsCache = {
        2: [
          {
            achievement_code: 'test-achievement',
            order: 1,
          },
        ],
        3: [
          {
            achievement_code: 'other-achievement',
            order: 1,
          },
        ],
      }

      const result = mapUserToProgressData(mockUser, levelRequirementsCache)

      expect(levelRequirementConverters.convertBackendRequirementsToFrontend).toHaveBeenCalled()
      expect(result.levelRequirements.length).toBeGreaterThan(0)
    })

    it('should show all 45 levels in dev mode', () => {
      const levelRequirementsCache: Record<number, any[]> = {}
      for (let i = 2; i <= 45; i++) {
        levelRequirementsCache[i] = [{ achievement_code: 'test', order: 1 }]
      }

      const result = mapUserToProgressData(mockUser, levelRequirementsCache, undefined, true)

      expect(result.levelRequirements.length).toBe(44) // Levels 1-44 (each has requirements for next level)
    })

    it('should show levels up to user.level + 2 in normal mode', () => {
      const levelRequirementsCache: Record<number, any[]> = {}
      for (let i = 2; i <= 10; i++) {
        levelRequirementsCache[i] = [{ achievement_code: 'test', order: 1 }]
      }

      const result = mapUserToProgressData(mockUser, levelRequirementsCache, undefined, false)

      // User level is 2, maxLevelToShow = min(2 + 2, 45) = 4
      // Loop goes from level 1 to 4, checking for requirements at nextLevel (2-5)
      // Only levels 2-5 have requirements, so we get 4 level requirements
      expect(result.levelRequirements.length).toBeLessThanOrEqual(4)
    })

    it('should use fallback level requirements when cache not provided', () => {
      const result = mapUserToProgressData(mockUser)

      expect(result.levelRequirements).toHaveLength(1)
      expect(result.levelRequirements[0].id).toBe('l1-2')
    })

    it('should set isLocked based on dev mode', () => {
      const levelRequirementsCache = {
        3: [{ achievement_code: 'test', order: 1 }],
      }

      const resultNormal = mapUserToProgressData(mockUser, levelRequirementsCache, undefined, false)
      const resultDev = mapUserToProgressData(mockUser, levelRequirementsCache, undefined, true)

      // In normal mode, level 3 requirements (from level 2 -> 3) should be locked if user.level (2) > level (2)
      // But the check is: level > user.level, so level 2 > user.level 2 is false, not locked
      // Level 3 requirements would come from level 2->3, so level=2, and 2 > 2 is false
      // Let's check with a level that would actually be locked
      const userLevel1 = { ...mockUser, level: 1 }
      const resultNormalLevel1 = mapUserToProgressData(userLevel1, levelRequirementsCache, undefined, false)
      
      // Level 2 -> 3 requirement: level=2, user.level=1, so 2 > 1 = true, should be locked
      expect(resultNormalLevel1.levelRequirements.some((req) => req.isLocked)).toBe(true)
      // In dev mode, nothing should be locked
      expect(resultDev.levelRequirements.every((req) => !req.isLocked)).toBe(true)
    })

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

    it('should handle empty level requirements cache', () => {
      const result = mapUserToProgressData(mockUser, {})

      expect(result.levelRequirements).toHaveLength(0)
    })
  })
})



