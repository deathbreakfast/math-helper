import { useState } from 'react'
import type { AchievementType, AchievementStatus, PerformanceTier } from '../data/achievements'

export const useJourneyFilters = () => {
  const [achievementFilter, setAchievementFilter] = useState<'all' | AchievementType>('all')
  const [statusFilter, setStatusFilter] = useState<'all' | AchievementStatus>('all')
  const [testFilter, setTestFilter] = useState<'all' | 'addition' | 'subtraction' | 'multiplication' | 'division'>('all')
  const [tierFilter, setTierFilter] = useState<'all' | PerformanceTier>('all')

  return {
    achievementFilter,
    statusFilter,
    testFilter,
    tierFilter,
    setAchievementFilter,
    setStatusFilter,
    setTestFilter,
    setTierFilter,
  }
}

