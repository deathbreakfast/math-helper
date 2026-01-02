import { useEffect, useState } from 'react'
import { fetchAchievementDefinitions, type BackendAchievementDefinition } from './api'

export type AchievementDefinitionsCache = Record<string, BackendAchievementDefinition>

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

