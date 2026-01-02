export type BackendAchievementDefinition = {
  code: string
  title: string
  description: string
  icon: string
  category: string
  requirements?: Record<string, unknown>
  xp_reward?: {
    bonus_xp: number
    multiplier: number
  }
}

export type BackendAchievementDefinitionsResponse = {
  achievements: Record<string, BackendAchievementDefinition>
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


