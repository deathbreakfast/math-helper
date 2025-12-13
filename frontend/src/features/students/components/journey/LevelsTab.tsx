import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, Crown, Loader2 } from 'lucide-react'
import { LevelRequirementCard } from '../LevelRequirementCard'
import type { UserProgressData } from '../../utils/progressMapping'
import { useLevelRequirements, useAchievementDefinitions } from '../../../../lib/levels/hooks'
import { mapUserToProgressData } from '../../utils/progressMapping'
import { useDevMode } from '../../../../utils/devMode'
import type { User } from '../../hooks/useLearners'

type LevelsTabProps = {
  userData: UserProgressData
  isActive: boolean
  user?: User | null
}

export const LevelsTab = ({ userData, isActive, user }: LevelsTabProps) => {
  const devMode = useDevMode()
  
  // Only fetch level requirements when tab is active (lazy loading)
  // In dev mode, fetch all 45 levels. Otherwise, fetch levels up to user's level + 3
  // Pass userId to get completion status from server
  const maxLevel = devMode ? 45 : Math.min((userData.level || 1) + 3, 45)
  const userId = user?.id ? String(user.id) : undefined
  const { requirements: levelRequirementsCache, isLoading, error } = useLevelRequirements(maxLevel, isActive, userId)
  const { definitions: achievementDefinitions } = useAchievementDefinitions()
  
  // Re-map user data with fetched level requirements if user is available
  const updatedUserData = useMemo(() => {
    if (!user || !levelRequirementsCache || Object.keys(levelRequirementsCache).length === 0) {
      return userData
    }
    return mapUserToProgressData(user, levelRequirementsCache, achievementDefinitions, devMode)
  }, [user, levelRequirementsCache, achievementDefinitions, userData, devMode])

  return (
    <motion.div
      data-testid="testid-levels-tab"
      key="levels"
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
      className="space-y-6"
    >
      <div data-testid="testid-level-progression-header" className="mb-8 rounded-2xl border-2 border-blue-300 bg-gradient-to-r from-blue-100 to-purple-100 p-6">
        <div className="mb-3 flex items-center gap-3">
          <Crown className="h-8 w-8 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Level Progression Path</h2>
        </div>
        <p className="text-gray-700">Complete achievements to unlock higher levels. Each level brings new challenges and rewards!</p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading level requirements...</span>
        </div>
      )}

      {error && (
        <div className="rounded-lg border-2 border-red-300 bg-red-50 p-4 text-red-800">
          <p>Failed to load level requirements: {error}</p>
        </div>
      )}

      {!isLoading && !error && updatedUserData.levelRequirements
        .filter((req) => devMode || !req.isLocked || req.level <= updatedUserData.level + 1)
        .map((requirement, index) => (
          <LevelRequirementCard key={requirement.id} requirement={requirement} index={index} userId={userData.id} />
        ))}

      {/* Locked Future Levels Preview - Only show when not in dev mode */}
      {!isLoading && !error && !devMode && (
        <div className="rounded-2xl border-2 border-gray-300 bg-gray-100 p-8 text-center">
          <Lock className="mx-auto mb-4 h-16 w-16 text-gray-400" />
          <h3 className="mb-2 text-xl font-bold text-gray-600">More Levels Await</h3>
          <p className="text-gray-500">Keep progressing to unlock requirements for Levels {updatedUserData.level + 2} and beyond!</p>
        </div>
      )}
    </motion.div>
  )
}

