export type LevelRequirement = {
  id: string
  level: number
  nextLevel: number
  title: string
  requirements: {
    description: string
    achievementIds?: string[]
    achievementCode?: string // Backend achievement code for navigation
    alternatives?: Array<{
      description: string
      achievementIds: string[]
    }>
    completed: boolean
    progress?: number
    maxProgress?: number
  }[]
  isLocked: boolean
}

// Level requirements are fetched from the backend (e.g. `/api/levels/requirements`).
// This module intentionally contains only the TypeScript type used by the students feature.
