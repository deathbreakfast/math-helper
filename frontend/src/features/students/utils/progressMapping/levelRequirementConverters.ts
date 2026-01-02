import type { LevelRequirement } from '../../data/levelRequirements'
import { ACHIEVEMENT_CODE_TO_FRONTEND_ID } from '../../../../lib/levels/achievementMapping'
import { getConceptDisplayNameByConceptId } from '../../data/mathConcepts'
import { extractTierFromCode } from '../achievementUtils'

function _titleizeWords(text: string): string {
  return text
    .split(/\s+/)
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

function _formatAchievementCodeForDisplay(code: string): string {
  const { baseCode, tier } = extractTierFromCode(code)
  const baseTitle = _titleizeWords(baseCode.replace(/-/g, ' '))
  return tier ? `${baseTitle} (${tier})` : baseTitle
}

/**
 * Convert backend achievement requirements to frontend format.
 * This function is repurposed from level requirements to concept unlock requirements.
 * The level/nextLevel parameters are kept for backward compatibility but are not used for gating.
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
    const quantity = req.quantity ?? 1
    
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
    const achievementTitle = userAchievement?.title || _formatAchievementCodeForDisplay(req.achievement_code)
    let baseDescription = `Complete: ${achievementTitle}`
    
    // Add metadata to description if present (concept_id)
    if (req.metadata_filter?.concept_id) {
      const conceptName = getConceptDisplayNameByConceptId(req.metadata_filter.concept_id)
      if (conceptName) {
        baseDescription = `${baseDescription} (${conceptName})`
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

  // This function is repurposed for concept unlock requirements
  // level/nextLevel parameters are kept for backward compatibility but are not used for gating
  // All concept unlock requirements are unlocked (no level-based locking)
  return {
    id: `l${level}-${nextLevel}`,
    level,
    nextLevel,
    title: `Reach Level ${nextLevel}`, // Title kept for backward compatibility
    requirements,
    isLocked: false, // Concept unlock requirements are not locked by level
  }
}





