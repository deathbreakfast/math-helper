import { useMemo } from 'react'
import { getAllMathConcepts, createConceptFromLevel, type MathConcept } from '../data/mathConcepts'
import { evaluateConceptUnlock, getUnlockedConcepts, getLockedConcepts } from '../utils/conceptUnlock'
import type { Achievement } from '../data/achievements'
import { useDevMode } from '../../../utils/devMode'
import { useLevelRequirements, useAchievementDefinitions } from '../../../lib/levels/hooks'
import type { UserProgressData } from '../utils/progressMapping'
import { convertBackendRequirementsToFrontend } from '../utils/progressMapping/levelRequirementConverters'
import type { BackendLevelRequirement } from '../../../lib/levels/api'

type UseMathConceptsOptions = {
  userData: UserProgressData
  isActive: boolean
  userId?: string
}

type UseMathConceptsResult = {
  concepts: MathConcept[]
  unlockedConcepts: MathConcept[]
  lockedConcepts: MathConcept[]
  isLoading: boolean
  error: string | null
}

/**
 * Hook to fetch and compute math concepts with unlock status
 */
export function useMathConcepts({ userData, isActive, userId }: UseMathConceptsOptions): UseMathConceptsResult {
  const devMode = useDevMode()
  
  // Fetch level requirements to determine unlock requirements for concepts
  // In dev mode, fetch all 45 levels. Otherwise, fetch levels up to user's level + 3
  const maxLevel = devMode ? 45 : Math.min((userData.level || 1) + 3, 45)
  const { requirements: levelRequirementsCache, isLoading: isLoadingRequirements, error: requirementsError } = 
    useLevelRequirements(maxLevel, isActive, userId)
  const { definitions: achievementDefinitions } = useAchievementDefinitions()

  // Generate concepts from levels
  const concepts = useMemo(() => {
    const allConcepts = getAllMathConcepts()
    const userAchievements = userData.achievements || []

    // Map concepts with unlock requirements from level requirements
    return allConcepts.map((concept) => {
      // Get unlock requirements from level requirements cache
      // For concept at level N, we look at requirements for level N (what unlocks that level)
      const targetLevel = concept.legacyLevel
      const backendReqs = levelRequirementsCache[targetLevel] || []
      
      let unlockRequirements = concept.unlockRequirements
      
      if (backendReqs.length > 0 && userData.id) {
        // Convert backend requirements to frontend format
        // We need user achievements for this - get from userData
        const userBackendAchievements = userAchievements.map(ach => ({
          code: ach.id,
          title: ach.title,
          metadata: {},
        }))
        
        const frontendReq = convertBackendRequirementsToFrontend(
          backendReqs,
          userBackendAchievements,
          targetLevel - 1, // Previous level
          targetLevel
        )
        
        unlockRequirements = frontendReq.requirements.map(req => ({
          description: req.description,
          achievementIds: req.achievementIds,
          achievementCode: req.achievementCode,
          alternatives: req.alternatives,
          completed: req.completed,
          progress: req.progress,
          maxProgress: req.maxProgress,
        }))
      }

      // Evaluate unlock status
      // In dev mode, all concepts are unlocked
      // Otherwise, check if user meets the requirements
      let isUnlocked = false
      if (devMode) {
        isUnlocked = true
      } else if (unlockRequirements.length === 0) {
        // No requirements = unlocked by default (for level 1)
        isUnlocked = true
      } else {
        const { isUnlocked: evaluated } = evaluateConceptUnlock(
          { ...concept, unlockRequirements },
          userAchievements,
          devMode
        )
        isUnlocked = evaluated
      }

      return {
        ...concept,
        unlockRequirements,
        isLocked: !isUnlocked,
      }
    })
  }, [levelRequirementsCache, userData, devMode])

  // Separate unlocked and locked concepts
  const unlockedConcepts = useMemo(() => {
    return concepts.filter(c => !c.isLocked)
  }, [concepts])

  const lockedConcepts = useMemo(() => {
    return concepts.filter(c => c.isLocked)
  }, [concepts])

  return {
    concepts,
    unlockedConcepts,
    lockedConcepts,
    isLoading: isLoadingRequirements,
    error: requirementsError,
  }
}
