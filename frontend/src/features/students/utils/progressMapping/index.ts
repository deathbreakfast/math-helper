import type { User } from '../../hooks/useLearners'
import type { Achievement } from '../../data/achievements'
import type { LevelRequirement } from '../../data/levelRequirements'
import type { LevelRequirementsCache, AchievementDefinitionsCache } from '../../../../lib/levels/hooks'
import { convertBackendDefinitionToFrontend, convertBackendAchievementToFrontend } from './achievementConverters'
import { convertBackendRequirementsToFrontend } from './levelRequirementConverters'

export type UserProgressData = {
  id: string
  name: string
  avatar: string
  level: number
  currentStreak: number
  bestStreak: number
  fastestSession: number
  fastestQuestion: number
  totalQuestions: number
  achievements: Achievement[]
  levelRequirements: LevelRequirement[]
}

export const mapUserToProgressData = (
  user: User,
  levelRequirementsCache?: LevelRequirementsCache,
  achievementDefinitions?: AchievementDefinitionsCache,
  devMode: boolean = false
): UserProgressData => {
  // Get user's earned achievements from backend
  const userBackendAchievements = user.achievements || []

  // If achievement definitions are provided, use them to generate all achievements
  // Otherwise, only show earned achievements
  let allAchievements: Achievement[] = []
  
  if (achievementDefinitions) {
    // Convert all backend achievement definitions to frontend format
    allAchievements = Object.entries(achievementDefinitions).map(([code, definition]) =>
      convertBackendDefinitionToFrontend(code, definition, userBackendAchievements)
    )
  } else {
    // Fallback: only show earned achievements (for backward compatibility)
    allAchievements = userBackendAchievements.map((backendAchievement) =>
      convertBackendAchievementToFrontend(backendAchievement, userBackendAchievements)
    )
    
    // Deduplicate by code, keeping the most recent one but preserving the count
    const uniqueAchievements = new Map<string, Achievement>()
    for (const achievement of allAchievements) {
      const existing = uniqueAchievements.get(achievement.id)
      if (!existing || (achievement.unlockedAt && existing.unlockedAt && achievement.unlockedAt > existing.unlockedAt)) {
        // Preserve the count when replacing - it should be the same, but ensure it's set
        uniqueAchievements.set(achievement.id, {
          ...achievement,
          count: achievement.count || existing?.count || 1  // Ensure count is preserved
        })
      } else if (existing) {
        // If keeping existing, ensure count is preserved
        uniqueAchievements.set(achievement.id, {
          ...existing,
          count: existing.count || achievement.count || 1
        })
      }
    }
    allAchievements = Array.from(uniqueAchievements.values())
  }

  // Build level requirements from backend data
  let levelRequirements: LevelRequirement[] = []

  if (levelRequirementsCache) {
    // In dev mode, show all 45 levels. Otherwise, show levels up to user's level + 2
    const maxLevelToShow = devMode ? 45 : Math.min(user.level + 2, 45)
    
    for (let level = 1; level <= maxLevelToShow; level++) {
      const nextLevel = level + 1
      const backendReqs = levelRequirementsCache[nextLevel] || []
      
      if (backendReqs.length > 0) {
        const frontendReq = convertBackendRequirementsToFrontend(
          backendReqs,
          userBackendAchievements,
          level,
          nextLevel
        )
        // In dev mode, don't lock requirements. Otherwise, lock if level > user.level
        frontendReq.isLocked = devMode ? false : level > user.level
        levelRequirements.push(frontendReq)
      }
    }
  } else {
    // Fallback: use hardcoded requirements if cache not available
    levelRequirements = [
      {
        id: 'l1-2',
        level: 1,
        nextLevel: 2,
        title: 'Reach Level 2',
        requirements: [
          {
            description: 'Complete achievement: addition-basics-bronze',
            achievementIds: ['addition-1digit-b'],
            completed: userBackendAchievements.some((a) => a.code === 'addition-basics-bronze'),
          },
        ],
        isLocked: user.level < 1,
      },
    ]
  }

  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar,
    level: user.level,
    currentStreak: user.stats.currentStreak,
    bestStreak: user.stats.bestStreak,
    fastestSession: 0, // Would come from actual session data
    fastestQuestion: user.averageSpeed,
    totalQuestions: user.questionsAnswered,
    achievements: allAchievements,
    levelRequirements,
  }
}





