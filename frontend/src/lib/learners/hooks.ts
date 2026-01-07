import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react'

import { mapApiLearner } from './api'
import type { Learner } from './types'

function mergeLearnerPreservingRichFields(existing: Learner, incoming: Learner): Learner {
  return {
    ...existing,
    ...incoming,
    // When the "minimal" users endpoint returns an empty achievements array, it should not
    // clobber richer data we may have already fetched via /api/users/:id.
    achievements: incoming.achievements.length > 0 ? incoming.achievements : existing.achievements,
  }
}

type UseLearnersState = {
  learners: Learner[]
  isLoading: boolean
  isLoadingFullData: boolean
  error: string | null
  refetch: () => Promise<void>
  refetchFullData: () => Promise<void>
  fetchUserFullData: (userId: string) => Promise<Learner | null>
  setLearners: Dispatch<SetStateAction<Learner[]>>
}

export const useLearners = (): UseLearnersState => {
  const [learners, setLearners] = useState<Learner[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingFullData, setIsLoadingFullData] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch minimal data for fast initial load
  const fetchLearners = useCallback(async (minimal: boolean = true) => {
    setIsLoading(true)
    setError(null)
    try {
      const url = minimal ? '/api/users?minimal=true' : '/api/users'
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error('Unable to load learners.')
      }
      const data = await response.json()
      const parsed = Array.isArray(data.users) ? data.users.map(mapApiLearner) : []
      if (minimal) {
        setLearners((prev) => {
          const prevById = new Map(prev.map((u) => [u.id, u]))

          const merged = parsed.map((incoming: Learner) => {
            const existing = prevById.get(incoming.id)
            return existing ? mergeLearnerPreservingRichFields(existing, incoming) : incoming
          })

          // Preserve any users that existed locally but weren't returned (defensive).
          const mergedIds = new Set(merged.map((u) => u.id))
          for (const existing of prev) {
            if (!mergedIds.has(existing.id)) {
              merged.push(existing)
            }
          }

          return merged
        })
      } else {
        setLearners(parsed)
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load learners.'
      setError(message)
      setLearners([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Refetch with minimal data (for initial load)
  const refetch = useCallback(async () => {
    await fetchLearners(true)
  }, [fetchLearners])

  // Refetch with full data (for journey modal, etc.)
  const refetchFullData = useCallback(async () => {
    setIsLoadingFullData(true)
    try {
      await fetchLearners(false)
    } finally {
      setIsLoadingFullData(false)
    }
  }, [fetchLearners])

  // Fetch full data for a single user (optimized for journey modal)
  const fetchUserFullData = useCallback(async (userId: string): Promise<Learner | null> => {
    setIsLoadingFullData(true)
    try {
      const response = await fetch(`/api/users/${userId}`)
      if (!response.ok) {
        throw new Error('Unable to load user data.')
      }
      const data = await response.json()
      
      // Step 1: Log raw API response to see backend data structure
      if (import.meta.env.DEV) {
        const rawAchievements = data.achievements || []
        const withMetadata = rawAchievements.filter((a: any) => a.metadata?.concept_id)
        const withoutMetadata = rawAchievements.filter((a: any) => !a.metadata?.concept_id)
        
        console.group('🔍 Step 1: Raw API Response (Backend Data)')
        console.log('Raw API Response:', {
          userId: data.id,
          achievementCount: rawAchievements.length,
          withMetadata: withMetadata.length,
          withoutMetadata: withoutMetadata.length,
        })
        console.log('Sample Raw Achievements WITH metadata (first 5):', 
          withMetadata.slice(0, 5).map((a: any) => ({
            code: a.code,
            metadata: a.metadata,
            concept_id: a.metadata?.concept_id,
          }))
        )
        console.log('Sample Raw Achievements WITHOUT metadata (first 5):', 
          withoutMetadata.slice(0, 5).map((a: any) => ({
            code: a.code,
            metadata: a.metadata,
          }))
        )
        // Check for duplicate codes with different metadata
        const codeGroups = new Map<string, any[]>()
        rawAchievements.forEach((a: any) => {
          if (a.code) {
            if (!codeGroups.has(a.code)) {
              codeGroups.set(a.code, [])
            }
            codeGroups.get(a.code)!.push(a)
          }
        })
        const duplicateCodes = Array.from(codeGroups.entries()).filter(([_, achievements]) => achievements.length > 1)
        if (duplicateCodes.length > 0) {
          console.log('⚠️ Duplicate codes with multiple achievements (first 10):', 
            duplicateCodes.slice(0, 10).map(([code, achievements]) => ({
              code,
              count: achievements.length,
              metadataVariants: achievements.map((a: any) => a.metadata?.concept_id || 'no metadata'),
            }))
          )
        }
        console.groupEnd()
      }
      
      const user = mapApiLearner(data)
      
      // Update the user in the learners array
      setLearners((prev) => {
        const index = prev.findIndex((l) => l.id === userId)
        if (index >= 0) {
          const updated = [...prev]
          updated[index] = user
          return updated
        }
        // If user not found, add it
        return [...prev, user]
      })
      
      return user
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to load user data.'
      setError(message)
      return null
    } finally {
      setIsLoadingFullData(false)
    }
  }, [])

  useEffect(() => {
    // Initial load uses minimal data for fast display
    fetchLearners(true)
  }, [fetchLearners])

  return {
    learners,
    isLoading,
    isLoadingFullData,
    error,
    refetch,
    refetchFullData,
    fetchUserFullData,
    setLearners,
  }
}


