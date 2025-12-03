import { useCallback, useEffect, useMemo, useState } from 'react'

import type {
  BackendTestAttempt,
  BackendTestAttemptDetail,
  BackendTestDefinition,
  FrontendTest,
  FrontendTestAttempt,
  FrontendTestAttemptDetail,
} from '../utils/testMapping'
import {
  getTestBestResult,
  mapTestAttemptDetailToFrontend,
  mapTestAttemptToFrontend,
  mapTestDefinitionToFrontend,
} from '../utils/testMapping'

interface UseTestsOptions {
  userId: number | null
  userLevel?: number
}

interface UseTestsResult {
  tests: FrontendTest[]
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
  getTestAttempts: (testType: string) => Promise<FrontendTestAttempt[]>
  getTestAttemptDetail: (attemptId: number) => Promise<FrontendTestAttemptDetail | null>
}

export const useTests = ({ userId, userLevel = 1 }: UseTestsOptions): UseTestsResult => {
  const [tests, setTests] = useState<FrontendTest[]>([])
  const [allAttempts, setAllAttempts] = useState<BackendTestAttempt[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch test definitions
  const fetchTestDefinitions = useCallback(async () => {
    if (!userId) {
      setTests([])
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Request unlock_status when userId is available
      const url = `/api/tests/definitions?user_id=${userId}&include_unlock_status=true`
      const response = await fetch(url)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch test definitions: ${response.statusText}`)
      }

      const data = await response.json()
      const definitions: BackendTestDefinition[] = data.definitions || []

      // Fetch all attempts for this user
      const attemptsUrl = `/api/tests/attempts?user_id=${userId}`
      const attemptsResponse = await fetch(attemptsUrl)
      
      let attempts: BackendTestAttempt[] = []
      if (attemptsResponse.ok) {
        const attemptsData = await attemptsResponse.json()
        attempts = attemptsData.attempts || []
      }

      setAllAttempts(attempts)

      // Map definitions to frontend format
      const mappedTests = definitions.map((def) =>
        mapTestDefinitionToFrontend(def, userLevel, attempts)
      )

      setTests(mappedTests)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tests')
      setTests([])
    } finally {
      setIsLoading(false)
    }
  }, [userId, userLevel])

  // Fetch test attempts for a specific test type
  const getTestAttempts = useCallback(
    async (testType: string): Promise<FrontendTestAttempt[]> => {
      if (!userId) {
        return []
      }

      try {
        const url = `/api/tests/${encodeURIComponent(testType)}/attempts?user_id=${userId}`
        const response = await fetch(url)

        if (!response.ok) {
          throw new Error(`Failed to fetch test attempts: ${response.statusText}`)
        }

        const data = await response.json()
        const attempts: BackendTestAttempt[] = data.attempts || []

        return attempts.map(mapTestAttemptToFrontend)
      } catch (err) {
        console.error('Error fetching test attempts:', err)
        return []
      }
    },
    [userId]
  )

  // Fetch detailed test attempt with questions
  const getTestAttemptDetail = useCallback(
    async (attemptId: number): Promise<FrontendTestAttemptDetail | null> => {
      try {
        const url = `/api/tests/attempts/${attemptId}/details`
        const response = await fetch(url)

        if (!response.ok) {
          if (response.status === 404) {
            return null
          }
          throw new Error(`Failed to fetch test attempt detail: ${response.statusText}`)
        }

        const data: BackendTestAttemptDetail = await response.json()
        return mapTestAttemptDetailToFrontend(data)
      } catch (err) {
        console.error('Error fetching test attempt detail:', err)
        return null
      }
    },
    []
  )

  // Refetch function
  const refetch = useCallback(async () => {
    await fetchTestDefinitions()
  }, [fetchTestDefinitions])

  // Initial fetch
  useEffect(() => {
    fetchTestDefinitions()
  }, [fetchTestDefinitions])

  return {
    tests,
    isLoading,
    error,
    refetch,
    getTestAttempts,
    getTestAttemptDetail,
  }
}

