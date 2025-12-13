import type { LevelRequirement } from '../../data/levelRequirements'
import { ACHIEVEMENT_CODE_TO_FRONTEND_ID } from '../../../../lib/levels/achievementMapping'
import { getTestDisplayName } from './testDisplayNames'

/**
 * Convert backend level requirements to frontend level requirements format
 */
export function convertBackendRequirementsToFrontend(
  backendRequirements: Array<{ 
    achievement_code: string
    order: number
    quantity?: number
    metadata_filter?: Record<string, any>
    user_count?: number  // Server-calculated count (preferred)
    completed?: boolean  // Server-calculated completion status (preferred)
  }>,
  userAchievements: Array<{ code?: string; title?: string; metadata?: Record<string, any> }>,
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
    
    // Use server-calculated count and completion status if available (preferred)
    // Otherwise, calculate client-side
    let count: number
    let completed: boolean
    
    if (req.user_count !== undefined && req.completed !== undefined) {
      // Use server-calculated values
      count = req.user_count
      completed = req.completed
    } else {
      // Fallback: client-side calculation (less accurate for metadata filters)
      // All achievement codes are now tiered (no base codes like "addition-basics")
      // Count achievements matching code AND metadata filter if provided
      count = 0
      for (const achievement of userAchievements) {
        if (achievement.code === req.achievement_code) {
          // If metadata filter is specified, check if achievement metadata matches
          if (req.metadata_filter) {
            // Check if achievement has metadata that matches the filter
            // Note: session_id in metadata should be ignored for filtering
            if (achievement.metadata) {
              const metadataWithoutSessionId = { ...achievement.metadata }
              delete metadataWithoutSessionId.session_id
              
              // Check if metadata matches (all filter keys must match)
              const matches = Object.keys(req.metadata_filter).every(
                key => metadataWithoutSessionId[key] === req.metadata_filter[key]
              )
              if (matches) {
                count++
              }
            }
            // If filter requires metadata but achievement has none, skip it
          } else {
            // No metadata filter - count all achievements with this code
            // But exclude achievements that have metadata (unless it's only session_id)
            if (!achievement.metadata || Object.keys(achievement.metadata).length === 0 || 
                (Object.keys(achievement.metadata).length === 1 && achievement.metadata.session_id)) {
              count++
            }
          }
        }
      }
      completed = count >= quantity
    }
    
    // Calculate progress based on quantity
    const progress = Math.min(count, quantity)
    const maxProgress = quantity
    
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
      completed: completed,
      progress: progress,
      maxProgress: maxProgress,
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




