import { useMemo } from 'react'
import type { Achievement, AchievementType, AchievementStatus, PerformanceTier } from '../data/achievements'

type UseFilteredAchievementsProps = {
  achievements: Achievement[]
  achievementFilter: 'all' | AchievementType | string
  statusFilter: 'all' | AchievementStatus
  tierFilter: 'all' | PerformanceTier
  textFilter: string
}

export const useFilteredAchievements = ({
  achievements,
  achievementFilter,
  statusFilter,
  tierFilter,
  textFilter,
}: UseFilteredAchievementsProps) => {
  // Filter achievements
  const filteredAchievements = useMemo(() => {
    const lowerTextFilter = textFilter.toLowerCase()
    return achievements.filter((achievement) => {
      // Support both type and category filtering
      const typeMatch = achievementFilter === 'all' || 
        achievement.type === achievementFilter || 
        achievement.category === achievementFilter
      const statusMatch = statusFilter === 'all' || achievement.status === statusFilter
      const textMatch = !textFilter || 
        achievement.title.toLowerCase().includes(lowerTextFilter) ||
        achievement.description.toLowerCase().includes(lowerTextFilter)
      return typeMatch && statusMatch && textMatch
    })
  }, [achievements, achievementFilter, statusFilter, textFilter])

  // Filter test achievements
  const testAchievements = useMemo(() => {
    return achievements.filter((a) => a.type === 'test-completion')
  }, [achievements])

  const filteredTestAchievements = useMemo(() => {
    const lowerTextFilter = textFilter.toLowerCase()
    return testAchievements.filter((achievement) => {
      const tierMatch = tierFilter === 'all' || achievement.performanceTier === tierFilter
      const statusMatch = statusFilter === 'all' || achievement.status === statusFilter
      const textMatch = !textFilter || 
        achievement.title.toLowerCase().includes(lowerTextFilter) ||
        achievement.description.toLowerCase().includes(lowerTextFilter)
      return tierMatch && statusMatch && textMatch
    })
  }, [testAchievements, tierFilter, statusFilter, textFilter])

  // Calculate stats
  const totalAchievements = achievements.filter((a) => !a.isHidden || a.status === 'unlocked').length
  const unlockedAchievements = achievements.filter((a) => a.status === 'unlocked').length
  const inProgressAchievements = achievements.filter((a) => a.status === 'in-progress').length
  const unlockedTestAchievements = testAchievements.filter((a) => a.status === 'unlocked').length
  const sssRankAchievements = testAchievements.filter((a) => a.performanceTier === 'SSS' && a.status === 'unlocked').length

  return {
    filteredAchievements,
    testAchievements,
    filteredTestAchievements,
    totalAchievements,
    unlockedAchievements,
    inProgressAchievements,
    unlockedTestAchievements,
    sssRankAchievements,
  }
}

