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

// LevelRequirement type is kept for backward compatibility but is no longer used for gating.
// Level requirements are not used - concepts use achievement-based unlock requirements instead.
// The levelRequirements array in UserProgressData is always empty.
