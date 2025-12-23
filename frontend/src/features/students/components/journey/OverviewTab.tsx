import { useState, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Trophy, RotateCcw } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import { PillButton } from '../../../../components/ui'
import type { Achievement } from '../../data/achievements'
import type { UserProgressData } from '../../utils/progressMapping'
import { logError } from '../../../../utils/logger'

type OverviewTabProps = {
  allAchievements: Achievement[]
  onViewAllAchievements: () => void
  userData?: UserProgressData
  onRefresh?: () => void
}

export const OverviewTab = ({ allAchievements, onViewAllAchievements, userData, onRefresh }: OverviewTabProps) => {
  const [searchParams] = useSearchParams()
  const [isResetting, setIsResetting] = useState(false)

  // Check if dev mode is enabled via environment variable
  const isDevMode = useMemo(() => {
    return import.meta.env.VITE_DEV_MODE === 'true'
  }, [])

  // Get recent achievements
  const recentAchievements = allAchievements
    .filter((a) => a.status === 'unlocked' && !a.isHidden)
    .sort((a, b) => (b.lastEarnedAt?.getTime() || b.unlockedAt?.getTime() || 0) - (a.lastEarnedAt?.getTime() || a.unlockedAt?.getTime() || 0))
    .slice(0, 6)

  const handleResetUser = async () => {
    if (!userData || !isDevMode) return
    
    const confirmed = window.confirm(
      `⚠️ DEV MODE: This will permanently delete ALL data for ${userData.name}:\n\n` +
      `- All achievements\n` +
      `- All practice sessions\n` +
      `- All answered questions\n` +
      `- All daily stats\n` +
      `- Reset level to 1\n\n` +
      `This cannot be undone. Continue?`
    )
    
    if (!confirmed) return

    setIsResetting(true)
    try {
      const response = await fetch(`/api/users/${userData.id}/reset`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to reset user data')
      }

      // Refresh data if callback provided, otherwise reload page
      if (onRefresh) {
        await onRefresh()
      } else {
        window.location.reload()
      }
      
      // Show success message
      alert(`✅ User data reset successfully! ${userData.name} has been reset to level 1.`)
    } catch (error) {
      logError('Error resetting user:', error)
      alert(`❌ Failed to reset user data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsResetting(false)
    }
  }

  return (
    <motion.div
      key="overview"
      data-testid="testid-overview-tab"
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      exit={{
        opacity: 0,
        y: -20,
      }}
      className="space-y-8"
    >
      {/* Recent Achievements */}
      <div data-testid="testid-recent-achievements">
        <h2 className="mb-6 flex items-center gap-3 text-2xl font-bold text-gray-900">
          <Trophy className="h-7 w-7 text-purple-600" />
          Recent Achievements
        </h2>
        {recentAchievements.length > 0 ? (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {recentAchievements.map((achievement, index) => (
              <AchievementCard key={achievement.id} achievement={achievement} index={index} />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border-2 border-gray-200 bg-gray-50 p-8 text-center text-gray-500">
            No achievements unlocked yet. Keep practicing to earn achievements!
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
        {isDevMode && userData && (
          <PillButton
            onClick={handleResetUser}
            tone="rose"
            disabled={isResetting}
            leftIcon={<RotateCcw className="h-4 w-4" />}
          >
            {isResetting ? 'Resetting...' : 'Reset User (Dev)'}
          </PillButton>
        )}
        <button
          data-testid="testid-view-all-achievements-button"
          onClick={onViewAllAchievements}
          className="rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 px-8 py-4 font-semibold text-white shadow-lg transition-all hover:scale-105 hover:shadow-xl"
        >
          View All Achievements
        </button>
      </div>
    </motion.div>
  )
}

