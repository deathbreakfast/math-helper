import { useEffect, useMemo, useState } from 'react'
import { fetchConceptRequirements, type BackendConceptRequirement } from './api'

export type ConceptRequirementsCache = Record<string, BackendConceptRequirement[]>

export const useConceptRequirements = (conceptIds: string[], enabled: boolean, userId?: string) => {
  const [requirements, setRequirements] = useState<ConceptRequirementsCache>({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const conceptIdsKey = useMemo(() => conceptIds.slice().sort().join(','), [conceptIds])

  useEffect(() => {
    if (!enabled) {
      setIsLoading(false)
      return
    }

    const run = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await fetchConceptRequirements(conceptIds, userId)
        setRequirements(data.requirements || {})
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch concept requirements')
        setRequirements({})
      } finally {
        setIsLoading(false)
      }
    }

    run()
  }, [conceptIdsKey, enabled, userId])

  return { requirements, isLoading, error }
}





