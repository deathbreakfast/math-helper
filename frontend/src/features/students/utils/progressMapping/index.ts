import type { User } from '../../hooks/useLearners'
import type { Achievement } from '../../data/achievements'
import type { LevelRequirement } from '../../data/levelRequirements'
import type { AchievementDefinitionsCache } from '../../../../lib/levels/hooks'
import { convertBackendDefinitionToFrontend, convertBackendAchievementToFrontend } from './achievementConverters'

export type UserProgressData = {
  id: string
  name: string
  avatar: string
  level: number
  experience: number
  xp_progress?: {
    level: number
    total_xp: number
    current_level_total_xp: number
    next_level_total_xp: number | null
    xp_into_level: number
    xp_to_next_level: number | null
  }
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
  _levelRequirementsCache?: unknown, // Deprecated: level requirements removed
  achievementDefinitions?: AchievementDefinitionsCache,
  _devMode: boolean = false // Deprecated: dev mode for levels removed
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

  // Level requirements removed - legacy level progression system no longer exists
  // User level is now automatically calculated from XP
  const levelRequirements: LevelRequirement[] = []

  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar,
    level: user.level,
    experience: user.experience ?? 0,
    xp_progress: user.xp_progress,
    currentStreak: user.stats.currentStreak,
    bestStreak: user.stats.bestStreak,
    fastestSession: 0, // Would come from actual session data
    fastestQuestion: user.averageSpeed,
    totalQuestions: user.questionsAnswered,
    achievements: allAchievements,
    levelRequirements,
  }
}





