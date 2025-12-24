export type BackendConceptRequirement = {
  achievement_code: string
  order: number
  quantity?: number
  metadata_filter?: Record<string, any>
  user_count?: number
  completed?: boolean
}

export type BackendConceptRequirementsResponse = {
  requirements: Record<string, BackendConceptRequirement[]>
}

export async function fetchConceptRequirements(
  conceptIds: string[],
  userId?: string
): Promise<BackendConceptRequirementsResponse> {
  if (conceptIds.length === 0) {
    return { requirements: {} }
  }

  const conceptIdsParam = conceptIds.join(',')
  const url = userId
    ? `/api/concepts/requirements?concept_ids=${encodeURIComponent(conceptIdsParam)}&user_id=${encodeURIComponent(userId)}`
    : `/api/concepts/requirements?concept_ids=${encodeURIComponent(conceptIdsParam)}`

  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Failed to fetch concept requirements: ${response.statusText}`)
  }
  return response.json()
}






