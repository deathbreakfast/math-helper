import { useSearchParams } from 'react-router-dom'
import type { AchievementType, AchievementStatus } from '../data/achievements'

export const useJourneyFilters = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  
  // Derive filter values directly from URL - single source of truth
  const achievementFilter = searchParams.get('filter') || 'all'
  // Cast statusFilter to AchievementStatus type (URL params are strings)
  const statusFilter = (searchParams.get('status') || 'all') as 'all' | AchievementStatus
  const textFilter = searchParams.get('text') || ''
  
  // Update functions that modify URL directly
  const setAchievementFilter = (filter: 'all' | AchievementType | string) => {
    const newParams = new URLSearchParams(searchParams)
    if (filter !== 'all') {
      newParams.set('filter', filter)
    } else {
      newParams.delete('filter')
    }
    setSearchParams(newParams, { replace: true })
  }
  
  const setStatusFilter = (filter: 'all' | AchievementStatus) => {
    const newParams = new URLSearchParams(searchParams)
    if (filter !== 'all') {
      newParams.set('status', filter)
    } else {
      newParams.delete('status')
    }
    setSearchParams(newParams, { replace: true })
  }
  
  const setTextFilter = (filter: string) => {
    const newParams = new URLSearchParams(searchParams)
    if (filter) {
      newParams.set('text', filter)
    } else {
      newParams.delete('text')
    }
    setSearchParams(newParams, { replace: true })
  }

  return {
    achievementFilter,
    statusFilter,
    textFilter,
    setAchievementFilter,
    setStatusFilter,
    setTextFilter,
  }
}

