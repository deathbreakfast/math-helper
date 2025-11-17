import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import type { Achievement, AchievementType, AchievementStatus } from '../../data/achievements'

type AchievementsTabProps = {
  filteredAchievements: Achievement[]
  achievementFilter: 'all' | AchievementType
  statusFilter: 'all' | AchievementStatus
  onAchievementFilterChange: (filter: 'all' | AchievementType) => void
  onStatusFilterChange: (filter: 'all' | AchievementStatus) => void
}

export const AchievementsTab = ({
  filteredAchievements,
  achievementFilter,
  statusFilter,
  onAchievementFilterChange,
  onStatusFilterChange,
}: AchievementsTabProps) => {
  return (
    <motion.div
      key="achievements"
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
    >
      {/* Filters */}
      <div className="mb-8 rounded-2xl bg-white p-6 shadow-lg">
        <div className="flex flex-wrap gap-4">
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Category</label>
            <select
              value={achievementFilter}
              onChange={(e) => onAchievementFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="streak">Streak Achievements</option>
              <option value="milestone">Milestones</option>
              <option value="test-completion">Test Completions</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => onStatusFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="unlocked">Unlocked</option>
              <option value="in-progress">In Progress</option>
              <option value="locked">Locked</option>
            </select>
          </div>
        </div>
      </div>

      {/* Achievement Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredAchievements.map((achievement, index) => (
          <AchievementCard key={achievement.id} achievement={achievement} index={index} />
        ))}
      </div>

      {filteredAchievements.length === 0 && (
        <div className="py-16 text-center">
          <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
          <p className="text-lg text-gray-500">No achievements match your filters</p>
        </div>
      )}
    </motion.div>
  )
}

