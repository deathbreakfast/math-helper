import { useState } from 'react'
import type { AchievementType, AchievementStatus, PerformanceTier } from '../data/achievements'

export const useJourneyFilters = () => {
  const [achievementFilter, setAchievementFilter] = useState<'all' | AchievementType | string>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | AchievementStatus>('all')
  const [tierFilter, setTierFilter] = useState<'all' | PerformanceTier>('all')
  const [textFilter, setTextFilter] = useState<string>('')

  return {
    achievementFilter,
    statusFilter,
    tierFilter,
    textFilter,
    setAchievementFilter,
    setStatusFilter,
    setTierFilter,
    setTextFilter,
  }
}

