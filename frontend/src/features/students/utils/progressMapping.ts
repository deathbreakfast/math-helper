import type { User } from '../hooks/useLearners'
import type { Achievement, AchievementStatus } from '../data/achievements'
import type { LevelRequirement } from '../data/levelRequirements'
import { ACHIEVEMENT_CODE_TO_FRONTEND_ID } from '../../../lib/levels/achievementMapping'
import type { LevelRequirementsCache, AchievementDefinitionsCache } from '../../../lib/levels/hooks'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import { extractTierFromCode, cleanTitle } from './achievementUtils'

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

/**
 * Convert backend achievement definition to frontend achievement format
 */
const convertBackendDefinitionToFrontend = (
  code: string,
  definition: BackendAchievementDefinition,
  userAchievements: Array<{ code?: string; earnedAt?: Date }>
): Achievement => {
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

  return {
    id: code,
    title: cleanedTitle,
    description: definition.description || '',
    icon: definition.icon || '🏆',
    type,
    tier,
    requirement: definition.description || '',
    status: isUnlocked ? ('unlocked' as AchievementStatus) : ('locked' as AchievementStatus),
    progress: isUnlocked ? 1 : 0,
    maxProgress: 1,
    unlockedAt: earnedAchievement?.earnedAt ? new Date(earnedAchievement.earnedAt) : undefined,
    isHidden: false,
    category,
    count: achievementCount,
    lastEarnedAt: earnedAchievement?.earnedAt ? new Date(earnedAchievement.earnedAt) : undefined,
    testType,
    performanceTier,
  }
}

/**
 * Convert backend level requirements to frontend level requirements format
 */
const convertBackendRequirementsToFrontend = (
  backendRequirements: Array<{ achievement_code: string; order: number; quantity?: number }>,
  userAchievements: Array<{ code?: string; title?: string }>,
  level: number,
  nextLevel: number
): LevelRequirement => {
  // Map backend requirements to frontend format
  const requirements = backendRequirements.map((req) => {
    // Find frontend achievement IDs that satisfy this backend code
    const frontendIds = ACHIEVEMENT_CODE_TO_FRONTEND_ID[req.achievement_code]
    const achievementIds = Array.isArray(frontendIds) ? frontendIds : frontendIds ? [frontendIds] : []

    // Count how many times the user has earned this achievement code
    const quantity = req.quantity ?? 1 // Default to 1 if not specified (backward compatibility)
    
    // All achievement codes are now tiered (no base codes like "addition-basics")
    // Count exact matches only
    const count = userAchievements.filter((a) => a.code === req.achievement_code).length
    
    // Calculate progress based on quantity
    const progress = Math.min(count, quantity)
    const maxProgress = quantity
    const completed = count >= quantity
    
    // Try to get a friendly description from the user's achievements or use the code
    const userAchievement = userAchievements.find((a) => a.code === req.achievement_code)
    const baseDescription = userAchievement?.title 
      ? `Complete: ${userAchievement.title}`
      : `Complete achievement: ${req.achievement_code.replace(/-/g, ' ')}`
    
    // Include quantity in description if > 1
    const description = quantity > 1 
      ? `${baseDescription} (${count}/${quantity})`
      : baseDescription

    return {
      description,
      achievementIds: achievementIds.length > 0 ? achievementIds : undefined,
      achievementCode: req.achievement_code, // Store achievement code for navigation
      completed,
      progress,
      maxProgress,
    }
  })

  return {
    id: `l${level}-${nextLevel}`,
    level,
    nextLevel,
    title: `Reach Level ${nextLevel}`,
    requirements,
    isLocked: level > nextLevel - 1, // Lock if current level is less than target - 1
  }
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
    allAchievements = userBackendAchievements.map((backendAchievement) => {
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
      
      return {
        id: code,
        title: cleanedTitle,
        description: backendAchievement.description || '',
        icon: backendAchievement.icon || '🏆',
        type,
        tier,
        requirement: backendAchievement.description || '',
        status: 'unlocked' as AchievementStatus,
        progress: 1,
        maxProgress: 1,
        unlockedAt: backendAchievement.earnedAt ? new Date(backendAchievement.earnedAt) : undefined,
        isHidden: false,
        category,
        // Count how many times this achievement code appears
        count: userBackendAchievements.filter((a) => a.code === code).length,
        lastEarnedAt: backendAchievement.earnedAt ? new Date(backendAchievement.earnedAt) : undefined,
        testType,
        performanceTier,
      }
    })
    
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
