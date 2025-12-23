import { useMemo } from 'react'
import { useDevMode } from '../../../utils/devMode'
import type { Achievement, AchievementType, AchievementStatus } from '../data/achievements'
import { shouldShowAchievement } from '../utils/achievementUtils'

type UseFilteredAchievementsProps = {
  achievements: Achievement[]
  achievementFilter: 'all' | AchievementType | string
  statusFilter: 'all' | AchievementStatus
  textFilter: string
}

export const useFilteredAchievements = ({
  achievements,
  achievementFilter,
  statusFilter,
  textFilter,
}: UseFilteredAchievementsProps) => {
  const devMode = useDevMode()
  
  // Filter achievements
  const filteredAchievements = useMemo(() => {
    // Normalize text filter: replace hyphens with spaces for flexible matching
    const normalizedTextFilter = textFilter.toLowerCase().replace(/-/g, ' ')
    return achievements.filter((achievement) => {
      // In dev mode, show all achievements including hidden/locked ones
      // In normal mode, filter out hidden achievements unless they're unlocked
      if (!devMode && achievement.isHidden && achievement.status !== 'unlocked') {
        return false
      }
      
      // Apply tier visibility filter (shows unlocked + next tier only)
      if (!shouldShowAchievement(achievement, achievements, devMode)) {
        return false
      }
      
      // Support both type and category filtering
      const typeMatch = achievementFilter === 'all' || 
        achievement.type === achievementFilter || 
        achievement.category === achievementFilter
      const statusMatch = statusFilter === 'all' || achievement.status === statusFilter
      
      // Normalize achievement text for comparison (replace hyphens with spaces)
      const normalizedTitle = achievement.title.toLowerCase().replace(/-/g, ' ')
      const normalizedDescription = achievement.description.toLowerCase().replace(/-/g, ' ')
      const normalizedId = achievement.id.toLowerCase().replace(/-/g, ' ')
      const textMatch = !textFilter || 
        normalizedTitle.includes(normalizedTextFilter) ||
        normalizedDescription.includes(normalizedTextFilter) ||
        normalizedId.includes(normalizedTextFilter)
      return typeMatch && statusMatch && textMatch
    })
  }, [achievements, achievementFilter, statusFilter, textFilter, devMode])

  // Calculate stats
  // In dev mode, include all achievements in stats. Otherwise, only include non-hidden or unlocked achievements
  const totalAchievements = devMode 
    ? achievements.length 
    : achievements.filter((a) => !a.isHidden || a.status === 'unlocked').length
  const unlockedAchievements = achievements.filter((a) => a.status === 'unlocked').length
  const inProgressAchievements = achievements.filter((a) => a.status === 'in-progress').length

  return {
    filteredAchievements,
    totalAchievements,
    unlockedAchievements,
    inProgressAchievements,
  }
}

