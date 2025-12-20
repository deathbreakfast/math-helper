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
  let metCount = 0
  const evaluatedRequirements = concept.unlockRequirements.map((req) => {
    let completed = false

    if (req.achievementIds && req.achievementIds.length > 0) {
      // Check if user has all required achievements
      completed = req.achievementIds.every((achId) =>
        userAchievements.some((ach) => ach.id === achId && ach.unlockedAt !== null)
      )
    } else if (req.achievementCode) {
      // Check by achievement code
      completed = userAchievements.some(
        (ach) => ach.id === req.achievementCode && ach.unlockedAt !== null
      )
    } else if (req.progress !== undefined && req.maxProgress !== undefined) {
      // Progress-based requirement
      completed = (req.progress || 0) >= (req.maxProgress || 0)
    }

    if (completed) {
      metCount++
    }

    return {
      ...req,
      completed,
    }
  })

  const isUnlocked = metCount === concept.unlockRequirements.length

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
