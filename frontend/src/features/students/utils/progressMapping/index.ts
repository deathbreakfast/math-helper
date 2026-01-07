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
  _levelRequirementsCache?: unknown,
  achievementDefinitions?: AchievementDefinitionsCache,
  _devMode: boolean = false
): UserProgressData => {
  // Get user's earned achievements from backend
  const userBackendAchievements = user.achievements || []

  // Step 3: Log pre-conversion to show userBackendAchievements structure
  if (import.meta.env.DEV) {
    const withMetadata = userBackendAchievements.filter(a => a.metadata?.concept_id)
    const withoutMetadata = userBackendAchievements.filter(a => !a.metadata?.concept_id)
    
    // Group by code to find duplicates
    const codeGroups = new Map<string, typeof userBackendAchievements>()
    userBackendAchievements.forEach(a => {
      if (a.code) {
        if (!codeGroups.has(a.code)) {
          codeGroups.set(a.code, [])
        }
        codeGroups.get(a.code)!.push(a)
      }
    })
    const duplicateCodes = Array.from(codeGroups.entries()).filter(([_, achievements]) => achievements.length > 1)
    
    console.group('🔍 Step 3: Pre-Conversion (userBackendAchievements)')
    console.log('User Backend Achievements:', {
      totalCount: userBackendAchievements.length,
      withMetadata: withMetadata.length,
      withoutMetadata: withoutMetadata.length,
      uniqueCodes: codeGroups.size,
      duplicateCodes: duplicateCodes.length,
    })
    if (duplicateCodes.length > 0) {
      console.log('⚠️ Duplicate codes with different metadata (first 10):', 
        duplicateCodes.slice(0, 10).map(([code, achievements]) => ({
          code,
          count: achievements.length,
          metadataVariants: achievements.map(a => ({
            concept_id: a.metadata?.concept_id || 'no metadata',
            earnedAt: a.earnedAt,
          })),
        }))
      )
    }
    console.log('Sample Achievements WITH metadata (first 5):', 
      withMetadata.slice(0, 5).map(a => ({
        id: a.id,
        code: a.code,
        metadata: a.metadata,
        concept_id: a.metadata?.concept_id,
      }))
    )
    console.log('Sample Achievements WITHOUT metadata (first 5):', 
      withoutMetadata.slice(0, 5).map(a => ({
        id: a.id,
        code: a.code,
        metadata: a.metadata,
      }))
    )
    console.groupEnd()
  }

  // If achievement definitions are provided, use them to generate all achievements
  // Otherwise, only show earned achievements
  let allAchievements: Achievement[] = []
  
  if (achievementDefinitions) {
    // Convert all backend achievement definitions to frontend format
    allAchievements = Object.entries(achievementDefinitions).map(([code, definition]) =>
      convertBackendDefinitionToFrontend(code, definition, userBackendAchievements)
    )
    
    // Step 4 (continued): Log post-conversion results
    if (import.meta.env.DEV) {
      const withMetadata = allAchievements.filter(a => a.metadata?.concept_id)
      const withoutMetadata = allAchievements.filter(a => !a.metadata?.concept_id)
      
      console.group('🔍 Step 4: Post-Conversion (convertBackendDefinitionToFrontend)')
      console.log('Converted Achievements:', {
        totalCount: allAchievements.length,
        withMetadata: withMetadata.length,
        withoutMetadata: withoutMetadata.length,
      })
      console.log('Sample Converted Achievements WITH metadata (first 5):', 
        withMetadata.slice(0, 5).map(a => ({
          id: a.id,
          metadata: a.metadata,
          concept_id: a.metadata?.concept_id,
        }))
      )
      console.log('Sample Converted Achievements WITHOUT metadata (first 5):', 
        withoutMetadata.slice(0, 5).map(a => ({
          id: a.id,
          metadata: a.metadata,
        }))
      )
      console.groupEnd()
    }
  } else {
    // Fallback: only show earned achievements
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

  // Level requirements are no longer used - concepts use achievement-based unlock requirements
  // Keeping empty array for backward compatibility with type definition
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





