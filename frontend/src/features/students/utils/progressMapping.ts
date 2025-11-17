import type { User } from '../hooks/useStudents'
import { STREAK_ACHIEVEMENTS, MILESTONE_ACHIEVEMENTS, TEST_ACHIEVEMENTS } from '../data/achievements'
import { LEVEL_REQUIREMENTS } from '../data/levelRequirements'
import type { Achievement, AchievementStatus } from '../data/achievements'
import type { LevelRequirement } from '../data/levelRequirements'

export type UserProgressData = {
  id: string
  name: string
  avatar: string
  level: number
  currentStreak: number
  bestStreak: number
  fastestSession: number
  fastestQuestion: number
  totalQuestions: number
  achievements: Achievement[]
  levelRequirements: LevelRequirement[]
}

export const mapUserToProgressData = (user: User): UserProgressData => {
  // Update streak achievements based on user's streak
  const streakAchievements = STREAK_ACHIEVEMENTS.map((achievement) => {
    let status: AchievementStatus = 'locked'
    let unlockedAt: Date | undefined
    let count = 0

    if (achievement.id === 's1' && user.stats.currentStreak >= 2) {
      status = 'unlocked'
      unlockedAt = new Date() // In real app, this would come from achievement data
      count = 1
    } else if (achievement.id === 's2' && user.stats.currentStreak >= 3) {
      status = 'unlocked'
      unlockedAt = new Date()
      count = 1
    } else if (achievement.id === 's3' && user.stats.currentStreak >= 5) {
      status = 'unlocked'
      unlockedAt = new Date()
      count = 1
    } else if (achievement.id === 's4') {
      if (user.stats.currentStreak >= 10) {
        status = 'unlocked'
        unlockedAt = new Date()
        count = 1
      } else if (user.stats.currentStreak >= 7) {
        status = 'in-progress'
      }
    }

    return {
      ...achievement,
      status,
      unlockedAt,
      count,
      progress: status === 'in-progress' ? user.stats.currentStreak : undefined,
      maxProgress: status === 'in-progress' ? 10 : undefined,
    }
  })

  // Update milestone achievements
  const milestoneAchievements = MILESTONE_ACHIEVEMENTS.map((achievement) => {
    let status: AchievementStatus = 'locked'
    let unlockedAt: Date | undefined
    let count = 0

    if (achievement.id === 'm1' && user.questionsAnswered >= 1) {
      status = 'unlocked'
      unlockedAt = new Date()
      count = 1
    } else if (achievement.id === 'm2' && user.questionsAnswered >= 100) {
      status = 'unlocked'
      unlockedAt = new Date()
      count = 1
    }

    return {
      ...achievement,
      status,
      unlockedAt,
      count,
    }
  })

  // Initialize test achievements (all locked for now - would be populated from actual test data)
  const initializedTestAchievements = TEST_ACHIEVEMENTS.map((achievement) => ({
    ...achievement,
    status: 'locked' as AchievementStatus,
  }))

  // Update level requirements based on current level
  const levelRequirements = LEVEL_REQUIREMENTS.map((req) => {
    const isLocked = req.level > user.level
    let requirements = req.requirements.map((r) => {
      // Check if requirement is completed based on achievements
      let completed = false
      let progress = r.progress
      let maxProgress = r.maxProgress

      if (r.achievementIds) {
        const relevantAchievements = [...streakAchievements, ...milestoneAchievements, ...initializedTestAchievements]
        completed = r.achievementIds.every((id) => relevantAchievements.find((a) => a.id === id)?.status === 'unlocked')
      }

      if (r.description.includes('test achievements')) {
        const unlockedTestCount = initializedTestAchievements.filter((a) => a.status === 'unlocked').length
        progress = unlockedTestCount
        maxProgress = r.maxProgress || 5
        completed = unlockedTestCount >= (maxProgress || 5)
      }

      return {
        ...r,
        completed,
        progress,
        maxProgress,
      }
    })

    return {
      ...req,
      isLocked,
      requirements,
    }
  })

  return {
    id: user.id,
    name: user.name,
    avatar: user.avatar,
    level: user.level,
    currentStreak: user.stats.currentStreak,
    bestStreak: user.stats.bestStreak,
    fastestSession: 0, // Would come from actual session data
    fastestQuestion: user.averageSpeed,
    totalQuestions: user.questionsAnswered,
    achievements: [...streakAchievements, ...milestoneAchievements, ...initializedTestAchievements],
    levelRequirements,
  }
}

