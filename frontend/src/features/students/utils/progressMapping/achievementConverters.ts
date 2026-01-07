import type { Achievement, AchievementStatus } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../../lib/levels/api'
import { extractTierFromCode, cleanTitle } from '../achievementUtils'

/**
 * Convert backend achievement definition to frontend achievement format
 */
export function convertBackendDefinitionToFrontend(
  code: string,
  definition: BackendAchievementDefinition,
  userAchievements: Array<{ code?: string; earnedAt?: Date; metadata?: Record<string, any> }>
): Achievement {
  const category = definition.category || 'milestone'
  
  // Step 4: Log conversion step to show which achievement is selected
  const matchingAchievements = userAchievements.filter((a) => a.code === code)
  const earnedAchievement = matchingAchievements[0] // .find() gets first match
  const isUnlocked = !!earnedAchievement
  
  if (import.meta.env.DEV && matchingAchievements.length > 1) {
    // Only log if there are multiple matches (potential data loss)
    console.warn(`⚠️ convertBackendDefinitionToFrontend: Code "${code}" has ${matchingAchievements.length} achievements, but only using first one:`, {
      selected: {
        metadata: earnedAchievement?.metadata,
        concept_id: earnedAchievement?.metadata?.concept_id,
        earnedAt: earnedAchievement?.earnedAt,
      },
      ignored: matchingAchievements.slice(1).map(a => ({
        metadata: a.metadata,
        concept_id: a.metadata?.concept_id,
        earnedAt: a.earnedAt,
      })),
    })
  }
  
  // Determine achievement type based on category
  let type: Achievement['type'] = 'milestone'
  if (category === 'speed') {
    type = 'speed-session'
  } else if (category === 'consistency') {
    type = 'streak'
  } else if (category === 'accuracy') {
    type = 'milestone'
  }
  
  // Extract tier from code (handles both old and new formats)
  const { tier: extractedTier } = extractTierFromCode(code)
  
  // Determine tier based on extraction or fallback logic
  let tier: Achievement['tier'] = 'Bronze'
  
  if (extractedTier) {
    // Use extracted tier from code
    tier = extractedTier as Achievement['tier']
  } else {
    // Fallback to old logic for non-tiered achievements
    // Specific achievement overrides
    if (code === 'accuracy-ace') {
      tier = 'Silver'
    } else if (code === 'first-steps') {
      tier = 'Bronze'
    } else if (code.includes('streak-10') || code === 'century') {
      tier = 'Gold'
    } else if (code.includes('streak-5')) {
      tier = 'Silver'
    } else if (category === 'speed') {
      tier = 'Gold'
    } else if (category === 'accuracy') {
      // Default accuracy achievements to Bronze unless overridden above
      tier = 'Bronze'
    }
  }
  
  // Clean title to remove tier suffix if present
  const rawTitle = definition.title || code
  const cleanedTitle = cleanTitle(rawTitle, tier)
  
  // Count how many times this achievement was earned (count achievements with same code)
  const achievementCount = userAchievements.filter((a) => a.code === code).length

  // Format requirement text - special handling for Lightning Fast to include min_questions
  let requirementText = definition.description || ''
  if (code.startsWith('lightning-fast-') && definition.requirements) {
    const reqs = definition.requirements as { max_speed_seconds?: number; min_questions?: number }
    const maxSpeed = reqs.max_speed_seconds
    const minQuestions = reqs.min_questions
    
    if (maxSpeed !== undefined && minQuestions !== undefined) {
      requirementText = `Avg <${maxSpeed}s/question with ${minQuestions}+ correct (per level)`
    } else if (maxSpeed !== undefined) {
      requirementText = `Avg <${maxSpeed}s/question (per level)`
    }
  }

  return {
    id: code,
    title: cleanedTitle,
    description: definition.description || '',
    icon: definition.icon || '🏆',
    type,
    tier,
    requirement: requirementText,
    status: isUnlocked ? ('unlocked' as AchievementStatus) : ('locked' as AchievementStatus),
    progress: isUnlocked ? 1 : 0,
    maxProgress: 1,
    unlockedAt: earnedAchievement?.earnedAt ? new Date(earnedAchievement.earnedAt) : undefined,
    isHidden: false,
    category,
    count: achievementCount,
    lastEarnedAt: earnedAchievement?.earnedAt ? new Date(earnedAchievement.earnedAt) : undefined,
    // Pass through metadata from earned achievement (contains concept_id, level, operation, etc.)
    metadata: earnedAchievement?.metadata,
    xp_reward: definition.xp_reward,
  }
}

/**
 * Convert a single backend achievement (from user's earned achievements) to frontend format.
 * Used as fallback when achievement definitions are not available.
 */
export function convertBackendAchievementToFrontend(
  backendAchievement: { code?: string; title?: string; description?: string; icon?: string; category?: string; earnedAt?: Date; metadata?: Record<string, any> },
  userAchievements: Array<{ code?: string; earnedAt?: Date; metadata?: Record<string, any> }>
): Achievement {
  const code = backendAchievement.code || ''
  const category = backendAchievement.category || 'milestone'
  
  // Determine achievement type based on category
  let type: Achievement['type'] = 'milestone'
  if (category === 'speed') {
    type = 'speed-session'
  } else if (category === 'consistency') {
    type = 'streak'
  } else if (category === 'accuracy') {
    type = 'milestone'
  }
  
  // Extract tier from code (handles both old and new formats)
  const { tier: extractedTier } = extractTierFromCode(code)
  
  // Determine tier based on extraction or fallback logic
  let tier: Achievement['tier'] = 'Bronze'
  
  if (extractedTier) {
    // Use extracted tier from code
    tier = extractedTier as Achievement['tier']
  } else {
    // Fallback to old logic for non-tiered achievements
    // Specific achievement overrides
    if (code === 'accuracy-ace') {
      tier = 'Silver'
    } else if (code === 'first-steps') {
      tier = 'Bronze'
    } else if (code.includes('streak-10') || code === 'century') {
      tier = 'Gold'
    } else if (code.includes('streak-5')) {
      tier = 'Silver'
    } else if (category === 'speed') {
      tier = 'Gold'
    } else if (category === 'accuracy') {
      // Default accuracy achievements to Bronze unless overridden above
      tier = 'Bronze'
    }
  }
  
  // Clean title to remove tier suffix if present
  const rawTitle = backendAchievement.title || code
  const cleanedTitle = cleanTitle(rawTitle, tier)
  
  // Format requirement text - special handling for Lightning Fast
  // Note: convertBackendAchievementToFrontend doesn't have access to definition.requirements
  // so we can't format Lightning Fast requirements here. This is a fallback converter.
  let requirementText = backendAchievement.description || ''

  return {
    id: code,
    title: cleanedTitle,
    description: backendAchievement.description || '',
    icon: backendAchievement.icon || '🏆',
    type,
    tier,
    requirement: requirementText,
    status: 'unlocked' as AchievementStatus,
    progress: 1,
    maxProgress: 1,
    unlockedAt: backendAchievement.earnedAt ? new Date(backendAchievement.earnedAt) : undefined,
    isHidden: false,
    category,
    // Count how many times this achievement code appears
    count: userAchievements.filter((a) => a.code === code).length,
    lastEarnedAt: backendAchievement.earnedAt ? new Date(backendAchievement.earnedAt) : undefined,
    // Pass through metadata from backend (contains concept_id, level, operation, etc.)
    metadata: backendAchievement.metadata,
    // Not always available in this fallback path (depends on /api/users payload).
    xp_reward: (backendAchievement as any).xp_reward,
  }
}





