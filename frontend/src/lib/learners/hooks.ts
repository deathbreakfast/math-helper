import { useCallback, useEffect, useState, type Dispatch, type SetStateAction } from 'react'

import { mapApiLearner } from './api'
import type { Learner } from './types'

type UseLearnersState = {
  learners: Learner[]
  isLoading: boolean
  error: string | null
  refetch: () => Promise<void>
  setLearners: Dispatch<SetStateAction<Learner[]>>
}

export const useLearners = (): UseLearnersState => {
  const [learners, setLearners] = useState<Learner[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLearners = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/users')
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

  useEffect(() => {
    fetchLearners()
  }, [fetchLearners])

  return {
    learners,
    isLoading,
    error,
    refetch: fetchLearners,
    setLearners,
  }
}


