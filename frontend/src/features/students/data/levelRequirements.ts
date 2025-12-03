import type { Achievement } from './achievements'

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

export const LEVEL_REQUIREMENTS: LevelRequirement[] = [
  {
    id: 'l1-2',
    level: 1,
    nextLevel: 2,
    title: 'Reach Level 2',
    requirements: [
      {
        description: 'Complete a 3-day streak',
        achievementIds: ['s2'],
        completed: false,
      },
    ],
    isLocked: false,
  },
  {
    id: 'l2-3',
    level: 2,
    nextLevel: 3,
    title: 'Reach Level 3',
    requirements: [
      {
        description: 'Complete any 5 test achievements (any rank)',
        completed: false,
        progress: 0,
        maxProgress: 5,
      },
    ],
    isLocked: false,
  },
]

