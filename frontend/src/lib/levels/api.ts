export type BackendLevelRequirement = {
  achievement_code: string
  order: number
  quantity?: number
}

export type BackendLevelRequirementsResponse = {
  level: number
  requirements: BackendLevelRequirement[]
}

export type BackendAchievementDefinition = {
  code: string
  title: string
  description: string
  icon: string
  category: string
  requirements?: Record<string, unknown>
}

export type BackendAchievementDefinitionsResponse = {
  achievements: Record<string, BackendAchievementDefinition>
}

/**
 * Fetch level requirements for a specific level from the backend
 */
export const fetchLevelRequirements = async (level: number): Promise<BackendLevelRequirementsResponse> => {
  const response = await fetch(`/api/levels/${level}/requirements`)
  if (!response.ok) {
    throw new Error(`Failed to fetch level requirements: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch all achievement definitions from the backend
 */
export const fetchAchievementDefinitions = async (): Promise<BackendAchievementDefinitionsResponse> => {
  const response = await fetch('/api/achievements/definitions')
  if (!response.ok) {
    throw new Error(`Failed to fetch achievement definitions: ${response.statusText}`)
  }
  return response.json()
}

/**
 * Fetch level requirements for multiple levels using batch endpoint
 */
export const fetchMultipleLevelRequirements = async (
  levels: number[]
): Promise<Record<number, BackendLevelRequirement[]>> => {
  if (levels.length === 0) {
    return {}
  }
  
  // Use batch endpoint if available (more efficient)
  try {
    const levelsParam = levels.join(',')
    const response = await fetch(`/api/levels/requirements?levels=${levelsParam}`)
    
    if (response.ok) {
      const data = await response.json()
      return data.requirements || {}
    }
    
    // If batch endpoint fails, fall back to individual requests
    console.warn('Batch endpoint failed, falling back to individual requests')
  } catch (error) {
    console.warn('Batch endpoint error, falling back to individual requests:', error)
  }
  
  // Fallback: fetch individually
  const requirements: Record<number, BackendLevelRequirement[]> = {}
  
  await Promise.all(
    levels.map(async (level) => {
      try {
        const data = await fetchLevelRequirements(level)
        requirements[level] = data.requirements
      } catch (error) {
        console.error(`Failed to fetch requirements for level ${level}:`, error)
        requirements[level] = []
      }
    })
  )
  
  return requirements
}

