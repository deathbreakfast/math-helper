import { useMemo } from 'react'
import type { Achievement, AchievementType, AchievementStatus, PerformanceTier } from '../data/achievements'

type UseFilteredAchievementsProps = {
  achievements: Achievement[]
  achievementFilter: 'all' | AchievementType
  statusFilter: 'all' | AchievementStatus
  testFilter: 'all' | 'addition' | 'subtraction' | 'multiplication' | 'division'
  tierFilter: 'all' | PerformanceTier
}

export const useFilteredAchievements = ({
  achievements,
  achievementFilter,
  statusFilter,
  testFilter,
  tierFilter,
}: UseFilteredAchievementsProps) => {
  // Filter achievements
  const filteredAchievements = useMemo(() => {
    return achievements.filter((achievement) => {
      const typeMatch = achievementFilter === 'all' || achievement.type === achievementFilter
      const statusMatch = statusFilter === 'all' || achievement.status === statusFilter
      return typeMatch && statusMatch
    })
  }, [achievements, achievementFilter, statusFilter])

  // Filter test achievements
  const testAchievements = useMemo(() => {
    return achievements.filter((a) => a.type === 'test-completion')
  }, [achievements])

  const filteredTestAchievements = useMemo(() => {
    return testAchievements.filter((achievement) => {
      const testTypeMatch = testFilter === 'all' || achievement.testType?.startsWith(testFilter) || false
      const tierMatch = tierFilter === 'all' || achievement.performanceTier === tierFilter
      const statusMatch = statusFilter === 'all' || achievement.status === statusFilter
      return testTypeMatch && tierMatch && statusMatch
    })
  }, [testAchievements, testFilter, tierFilter, statusFilter])

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

