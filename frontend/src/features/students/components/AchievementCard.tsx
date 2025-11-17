import React from 'react'
import { motion } from 'framer-motion'
import { Lock, Unlock, Trophy, Check, Star, Sparkles } from 'lucide-react'
import type { Achievement } from '../data/achievements'
import { getTierColor } from '../utils/achievementUtils'

type AchievementCardProps = {
  achievement: Achievement
  index: number
}

export const AchievementCard: React.FC<AchievementCardProps> = ({ achievement, index }) => {
  const isLocked = achievement.status === 'locked'
  const isInProgress = achievement.status === 'in-progress'
  const progressPercent = achievement.progress && achievement.maxProgress ? (achievement.progress / achievement.maxProgress) * 100 : 0
  const hasMultipleEarns = (achievement.count ?? 0) > 1

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        delay: index * 0.05,
      }}
      className={`relative rounded-2xl border-2 p-6 transition-all ${
        isLocked
          ? 'border-gray-300 bg-gray-100'
          : isInProgress
            ? 'border-blue-300 bg-gradient-to-br from-blue-50 to-purple-50 shadow-lg'
            : 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-amber-50 shadow-lg'
      }`}
    >
      {/* Lock/Unlock Icon */}
      <div className="absolute right-4 top-4">
        {isLocked ? <Lock className="h-5 w-5 text-gray-400" /> : <Unlock className="h-5 w-5 text-green-500" />}
      </div>

      {/* Count Badge */}
      {hasMultipleEarns && (
        <motion.div
          initial={{
            scale: 0,
          }}
          animate={{
            scale: 1,
          }}
          className="absolute left-4 top-4 flex items-center gap-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 px-3 py-1 text-xs font-bold text-white shadow-lg"
        >
          <Trophy className="h-3 w-3" />
          ×{achievement.count}
        </motion.div>
      )}

      {/* Achievement Icon */}
      <div className={`mb-3 text-5xl ${isLocked ? 'opacity-30' : ''}`}>{achievement.icon}</div>

      {/* Tier Badge */}
      <div className={`mb-3 inline-block rounded-full bg-gradient-to-r px-3 py-1 text-xs font-bold text-white ${getTierColor(achievement.tier)}`}>
        {achievement.tier}
      </div>

      {/* Title and Description */}
      <h3 className={`mb-2 text-lg font-bold ${isLocked ? 'text-gray-500' : 'text-gray-900'}`}>{achievement.title}</h3>
      <p className={`mb-3 text-sm ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>{achievement.description}</p>

      {/* Requirement */}
      <div className={`text-xs font-medium ${isLocked ? 'text-gray-400' : 'text-gray-500'}`}>
        Requirement: {achievement.requirement}
      </div>

      {/* Progress Bar */}
      {isInProgress && achievement.progress && achievement.maxProgress && (
        <div className="mt-4">
          <div className="mb-2 flex justify-between text-xs font-medium text-gray-700">
            <span>Progress</span>
            <span>
              {achievement.progress}/{achievement.maxProgress}
            </span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-gray-200">
            <motion.div
              initial={{
                width: 0,
              }}
              animate={{
                width: `${Math.min(progressPercent, 100)}%`,
              }}
              transition={{
                duration: 1,
                ease: 'easeOut',
              }}
              className="h-2.5 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
            />
          </div>
        </div>
      )}

      {/* Unlocked Date & Count Info */}
      {achievement.unlockedAt && (
        <div className="mt-3 space-y-1">
          <div className="flex items-center gap-1 text-xs font-medium text-green-600">
            <Check className="h-3 w-3" />
            First unlocked {achievement.unlockedAt.toLocaleDateString()}
          </div>
          {achievement.lastEarnedAt && achievement.lastEarnedAt.getTime() !== achievement.unlockedAt.getTime() && (
            <div className="flex items-center gap-1 text-xs font-medium text-blue-600">
              <Star className="h-3 w-3" />
              Last earned {achievement.lastEarnedAt.toLocaleDateString()}
            </div>
          )}
          {hasMultipleEarns && (
            <div className="flex items-center gap-1 text-xs font-bold text-purple-600">
              <Sparkles className="h-3 w-3" />
              Earned {achievement.count} times!
            </div>
          )}
        </div>
      )}
    </motion.div>
  )
}

