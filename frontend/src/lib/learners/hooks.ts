import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react'

import { mapApiLearner } from './api'
import type { Learner } from './types'

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
      setLearners(parsed)
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


