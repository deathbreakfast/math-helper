import { motion } from 'framer-motion'
import { Calculator } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import type { Achievement } from '../../data/achievements'

type OverviewTabProps = {
  testAchievements: Achievement[]
  onViewAllTests: () => void
}

export const OverviewTab = ({ testAchievements, onViewAllTests }: OverviewTabProps) => {
  return (
    <motion.div
      key="overview"
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
      {/* Recent Test Achievements */}
      <div>
        <h2 className="mb-6 flex items-center gap-3 text-2xl font-bold text-gray-900">
          <Calculator className="h-7 w-7 text-purple-600" />
          Recent Test Achievements
        </h2>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {testAchievements
            .filter((a) => a.status === 'unlocked')
            .sort((a, b) => (b.lastEarnedAt?.getTime() || b.unlockedAt?.getTime() || 0) - (a.lastEarnedAt?.getTime() || a.unlockedAt?.getTime() || 0))
            .slice(0, 6)
            .map((achievement, index) => (
              <AchievementCard key={achievement.id} achievement={achievement} index={index} />
            ))}
        </div>
      </div>

      {/* View All Tests Button */}
      <div className="text-center">
        <button
          onClick={onViewAllTests}
          className="rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 px-8 py-4 font-semibold text-white shadow-lg transition-all hover:scale-105 hover:shadow-xl"
        >
          View All Test Achievements
        </button>
      </div>
    </motion.div>
  )
}

