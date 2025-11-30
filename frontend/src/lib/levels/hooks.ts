import { useEffect, useState } from 'react'
import { fetchLevelRequirements, fetchMultipleLevelRequirements, fetchAchievementDefinitions, type BackendLevelRequirement, type BackendAchievementDefinition } from './api'

export type LevelRequirementsCache = {
  [level: number]: BackendLevelRequirement[]
}

export type AchievementDefinitionsCache = Record<string, BackendAchievementDefinition>

/**
 * Hook to fetch and cache level requirements
 * 
 * @param maxLevel - Maximum level to fetch requirements for
 * @param enabled - If false, hook will not fetch (for lazy loading). Default: true
 */
export const useLevelRequirements = (maxLevel: number = 45, enabled: boolean = true) => {
  const [requirements, setRequirements] = useState<LevelRequirementsCache>({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Only fetch if enabled
    if (!enabled) {
      setIsLoading(false)
      return
    }

    const fetchRequirements = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const levels = Array.from({ length: maxLevel }, (_, i) => i + 1)
        
        // Use batch endpoint for better performance
        const fetchedRequirements = await fetchMultipleLevelRequirements(levels)
        
        setRequirements(fetchedRequirements)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch level requirements')
      } finally {
        setIsLoading(false)
      }
    }

    fetchRequirements()
  }, [maxLevel, enabled])

  return { requirements, isLoading, error }
}

/**
 * Hook to fetch and cache achievement definitions
 */
export const useAchievementDefinitions = () => {
  const [definitions, setDefinitions] = useState<AchievementDefinitionsCache>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDefinitions = async () => {
      setIsLoading(true)
      setError(null)
      
      try {
        const data = await fetchAchievementDefinitions()
        setDefinitions(data.achievements)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch achievement definitions')
      } finally {
        setIsLoading(false)
      }
    }

    fetchDefinitions()
  }, [])

  return { definitions, isLoading, error }
}

