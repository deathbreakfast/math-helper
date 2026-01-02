/**
 * Utilities for calculating concept unlock status and progress
 */

import type { MathConcept, MathConceptUnlockRequirement } from '../data/mathConcepts'
import type { Achievement } from '../data/achievements'
import { useDevMode } from '../../../utils/devMode'

/**
 * Check if a concept's unlock requirements are met
 */
export function evaluateConceptUnlock(
  concept: MathConcept,
  userAchievements: Achievement[],
  devMode: boolean = false
): {
  isUnlocked: boolean
  unlockProgress: {
    met: number
    total: number
  }
  requirements: MathConceptUnlockRequirement[]
} {
  // Dev mode: unlock all concepts
  if (devMode) {
    return {
      isUnlocked: true,
      unlockProgress: { met: 1, total: 1 },
      requirements: concept.unlockRequirements.map(req => ({ ...req, completed: true })),
    }
  }

  // If no unlock requirements, concept is unlocked by default
  if (concept.unlockRequirements.length === 0) {
    return {
      isUnlocked: true,
      unlockProgress: { met: 1, total: 1 },
      requirements: [],
    }
  }

  // Evaluate each requirement
  // Requirements already have completed/progress calculated by convertBackendRequirementsToFrontend
  // which handles quantities and metadata filters. We just need to check the completed status.
  let metCount = 0
  const evaluatedRequirements = concept.unlockRequirements.map((req) => {
    // Use the already-calculated completed status if available
    // Otherwise fall back to simple checks
    let completed = req.completed ?? false

    if (!completed && req.progress !== undefined && req.maxProgress !== undefined) {
      // Progress-based requirement: check if progress meets threshold
      completed = (req.progress || 0) >= (req.maxProgress || 0)
    } else if (!completed && req.achievementIds && req.achievementIds.length > 0) {
      // Fallback: Check if user has all required achievements (simple check, no quantities/metadata)
      completed = req.achievementIds.every((achId) =>
        userAchievements.some((ach) => ach.id === achId && ach.unlockedAt !== null)
      )
    } else if (!completed && req.achievementCode) {
      // Fallback: Check by achievement code (simple check, no quantities/metadata)
      completed = userAchievements.some(
        (ach) => ach.id === req.achievementCode && ach.unlockedAt !== null
      )
    }

    if (completed) {
      metCount++
    }

    return {
      ...req,
      completed,
    }
  })

  // Concept is unlocked when ALL requirements are met (order is display-only)
  const isUnlocked = metCount === concept.unlockRequirements.length && concept.unlockRequirements.length > 0

  return {
    isUnlocked,
    unlockProgress: {
      met: metCount,
      total: concept.unlockRequirements.length,
    },
    requirements: evaluatedRequirements,
  }
}

/**
 * Get all unlocked concepts for a user
 */
export function getUnlockedConcepts(
  concepts: MathConcept[],
  userAchievements: Achievement[],
  devMode: boolean = false
): MathConcept[] {
  return concepts.filter((concept) => {
    const { isUnlocked } = evaluateConceptUnlock(concept, userAchievements, devMode)
    return isUnlocked
  })
}

/**
 * Get all locked concepts for a user
 */
export function getLockedConcepts(
  concepts: MathConcept[],
  userAchievements: Achievement[],
  devMode: boolean = false
): MathConcept[] {
  return concepts.filter((concept) => {
    const { isUnlocked } = evaluateConceptUnlock(concept, userAchievements, devMode)
    return !isUnlocked
  })
}
