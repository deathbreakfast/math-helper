import type { LevelRequirement } from '../../data/levelRequirements'
import { ACHIEVEMENT_CODE_TO_FRONTEND_ID } from '../../../../lib/levels/achievementMapping'
import { getTestDisplayName } from './testDisplayNames'

/**
 * Convert backend level requirements to frontend level requirements format
 */
export function convertBackendRequirementsToFrontend(
  backendRequirements: Array<{ achievement_code: string; order: number; quantity?: number; metadata_filter?: Record<string, any> }>,
  userAchievements: Array<{ code?: string; title?: string }>,
  level: number,
  nextLevel: number
): LevelRequirement {
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
    let baseDescription = userAchievement?.title 
      ? `Complete: ${userAchievement.title}`
      : `Complete achievement: ${req.achievement_code.replace(/-/g, ' ')}`
    
    // Add metadata to description if present (test_type or level)
    if (req.metadata_filter) {
      const metadataParts: string[] = []
      
      // Add test_type if present
      if (req.metadata_filter.test_type) {
        const testDisplayName = getTestDisplayName(req.metadata_filter.test_type)
        metadataParts.push(testDisplayName)
      }
      
      // Add level if present
      if (req.metadata_filter.level) {
        metadataParts.push(`Level ${req.metadata_filter.level}`)
      }
      
      // Append metadata to description in parentheses
      if (metadataParts.length > 0) {
        baseDescription = `${baseDescription} (${metadataParts.join(', ')})`
      }
    }
    
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



