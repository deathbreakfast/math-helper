import type { Achievement, AchievementStatus } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../../lib/levels/api'
import { extractTierFromCode, cleanTitle } from '../achievementUtils'

/**
 * Convert backend achievement definition to frontend achievement format
 */
export function convertBackendDefinitionToFrontend(
  code: string,
  definition: BackendAchievementDefinition,
  userAchievements: Array<{ code?: string; earnedAt?: Date }>
): Achievement {
  const category = definition.category || 'milestone'
  const earnedAchievement = userAchievements.find((a) => a.code === code)
  const isUnlocked = !!earnedAchievement
  
  // Determine achievement type based on category
  let type: Achievement['type'] = 'milestone'
  if (category === 'speed') {
    type = 'speed-session'
  } else if (category === 'consistency') {
    type = 'streak'
  } else if (category === 'accuracy') {
    type = 'milestone'
  } else if (category === 'test') {
    type = 'test-completion'
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
  
  // Extract test type from code if it's a test achievement
  let testType: Achievement['testType'] = undefined
  let performanceTier: Achievement['performanceTier'] = undefined
  if (category === 'test') {
    // Extract test type (e.g., "addition-1digit" from "addition-1digit-b")
    // Tier suffixes can be: 'b', 'a', 's', 'ss', 'sss'
    const tierSuffixes = ['sss', 'ss', 's', 'a', 'b']
    let tierSuffix: string | undefined
    let testTypeCode = code
    
    // Check for multi-character tier suffixes first (sss, ss) then single (s, a, b)
    for (const suffix of tierSuffixes) {
      if (code.endsWith(`-${suffix}`)) {
        tierSuffix = suffix
        testTypeCode = code.slice(0, -(suffix.length + 1)) // Remove '-{suffix}'
        break
      }
    }
    
    if (tierSuffix) {
      testType = testTypeCode as Achievement['testType']
      performanceTier = tierSuffix.toUpperCase() as Achievement['performanceTier']
    }
  }
  
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
    // Metadata is not available in userAchievements array - it comes from backend requirements
    metadata: undefined,
    xp_reward: definition.xp_reward,
    testType,
    performanceTier,
  }
}

/**
 * Convert a single backend achievement (from user's earned achievements) to frontend format.
 * Used as fallback when achievement definitions are not available.
 */
export function convertBackendAchievementToFrontend(
  backendAchievement: { code?: string; title?: string; description?: string; icon?: string; category?: string; earnedAt?: Date },
  userAchievements: Array<{ code?: string; earnedAt?: Date }>
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
  } else if (category === 'test') {
    type = 'test-completion'
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
  
  // Extract test type from code if it's a test achievement
  let testType: Achievement['testType'] = undefined
  let performanceTier: Achievement['performanceTier'] = undefined
  if (category === 'test') {
    // Extract test type (e.g., "addition-1digit" from "addition-1digit-b")
    // Tier suffixes can be: 'b', 'a', 's', 'ss', 'sss'
    const tierSuffixes = ['sss', 'ss', 's', 'a', 'b']
    let tierSuffix: string | undefined
    let testTypeCode = code
    
    // Check for multi-character tier suffixes first (sss, ss) then single (s, a, b)
    for (const suffix of tierSuffixes) {
      if (code.endsWith(`-${suffix}`)) {
        tierSuffix = suffix
        testTypeCode = code.slice(0, -(suffix.length + 1)) // Remove '-{suffix}'
        break
      }
    }
    
    if (tierSuffix) {
      testType = testTypeCode as Achievement['testType']
      performanceTier = tierSuffix.toUpperCase() as Achievement['performanceTier']
    }
  }
  
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
    // Metadata is not available in LearnerAchievement type - it comes from backend requirements
    metadata: undefined,
    // Not always available in this fallback path (depends on /api/users payload).
    xp_reward: (backendAchievement as any).xp_reward,
    testType,
    performanceTier,
  }
}





