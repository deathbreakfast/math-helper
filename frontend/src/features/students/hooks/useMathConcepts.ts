import { useMemo } from 'react'
import { getAllMathConcepts, type MathConcept } from '../data/mathConcepts'
import { evaluateConceptUnlock, getUnlockedConcepts, getLockedConcepts } from '../utils/conceptUnlock'
import type { Achievement } from '../data/achievements'
import { useDevMode } from '../../../utils/devMode'
import { useAchievementDefinitions } from '../../../lib/levels/hooks'
import type { UserProgressData } from '../utils/progressMapping'
import { convertBackendRequirementsToFrontend } from '../utils/progressMapping/levelRequirementConverters'
import { useConceptRequirements } from '../../../lib/concepts/hooks'

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
  const { definitions: achievementDefinitions } = useAchievementDefinitions()

  const allConcepts = useMemo(() => getAllMathConcepts(), [])
  const conceptIds = useMemo(() => allConcepts.map(c => c.conceptId), [allConcepts])
  const { requirements: conceptRequirementsCache, isLoading: isLoadingRequirements, error: requirementsError } =
    useConceptRequirements(conceptIds, isActive, userId)

  // Generate concepts from levels
  const concepts = useMemo(() => {
    const userAchievements = userData.achievements || []

    // Map concepts with unlock requirements from level requirements
    return allConcepts.map((concept) => {
      const backendReqs = conceptRequirementsCache[concept.conceptId] || []
      
      let unlockRequirements = concept.unlockRequirements
      
      if (backendReqs.length > 0 && userData.id) {
        // Convert backend requirements to frontend format
        // We need user achievements for this - get from userData
        // Include metadata from achievements if available (for filtering stage/concept achievements)
        const userBackendAchievements = userAchievements.map(ach => ({
          code: ach.id,
          title: ach.title,
          metadata: ach.metadata || {}, // Pass through metadata for filtering
        }))
        
        const frontendReq = convertBackendRequirementsToFrontend(
          backendReqs,
          userBackendAchievements,
          0,
          0
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
  }, [allConcepts, conceptRequirementsCache, userData, devMode])

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
