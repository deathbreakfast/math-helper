import { motion } from 'framer-motion'
import { Trophy, Calculator, Flame, Target } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'

type JourneyStatsOverviewProps = {
  userData: UserProgressData
  unlockedAchievements: number
  totalAchievements: number
  unlockedTestAchievements: number
  sssRankAchievements: number
  inProgressAchievements: number
}

export const JourneyStatsOverview = ({
  userData,
  unlockedAchievements,
  totalAchievements,
  unlockedTestAchievements,
  sssRankAchievements,
  inProgressAchievements,
}: JourneyStatsOverviewProps) => {
  return (
    <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
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
          delay: 0.1,
        }}
        className="rounded-2xl bg-white p-6 shadow-lg"
      >
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-100">
            <Trophy className="h-6 w-6 text-yellow-600" />
          </div>
          <div className="text-sm font-medium text-gray-600">Achievements</div>
        </div>
        <div className="text-4xl font-bold text-gray-900">{unlockedAchievements}</div>
        <div className="mt-1 text-sm text-gray-500">of {totalAchievements} unlocked</div>
      </motion.div>

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
          delay: 0.15,
        }}
        className="rounded-2xl bg-white p-6 shadow-lg"
      >
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-100">
            <Calculator className="h-6 w-6 text-purple-600" />
          </div>
          <div className="text-sm font-medium text-gray-600">Test Achievements</div>
        </div>
        <div className="text-4xl font-bold text-gray-900">{unlockedTestAchievements}</div>
        <div className="mt-1 text-sm text-gray-500">{sssRankAchievements} SSS rank</div>
      </motion.div>

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
          delay: 0.2,
        }}
        className="rounded-2xl bg-white p-6 shadow-lg"
      >
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-orange-100">
            <Flame className="h-6 w-6 text-orange-600" />
          </div>
          <div className="text-sm font-medium text-gray-600">Current Streak</div>
        </div>
        <div className="text-4xl font-bold text-gray-900">{userData.currentStreak}</div>
        <div className="mt-1 text-sm text-gray-500">Best: {userData.bestStreak} days</div>
      </motion.div>

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
          delay: 0.25,
        }}
        className="rounded-2xl bg-white p-6 shadow-lg"
      >
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
            <Target className="h-6 w-6 text-blue-600" />
          </div>
          <div className="text-sm font-medium text-gray-600">In Progress</div>
        </div>
        <div className="text-4xl font-bold text-gray-900">{inProgressAchievements}</div>
        <div className="mt-1 text-sm text-gray-500">achievements active</div>
      </motion.div>
    </div>
  )
}

