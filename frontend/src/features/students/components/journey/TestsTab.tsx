import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import type { Achievement, AchievementStatus, PerformanceTier } from '../../data/achievements'

type TestsTabProps = {
  filteredTestAchievements: Achievement[]
  testFilter: 'all' | 'addition' | 'subtraction' | 'multiplication' | 'division'
  tierFilter: 'all' | PerformanceTier
  statusFilter: 'all' | AchievementStatus
  onTestFilterChange: (filter: 'all' | 'addition' | 'subtraction' | 'multiplication' | 'division') => void
  onTierFilterChange: (filter: 'all' | PerformanceTier) => void
  onStatusFilterChange: (filter: 'all' | AchievementStatus) => void
}

export const TestsTab = ({
  filteredTestAchievements,
  testFilter,
  tierFilter,
  statusFilter,
  onTestFilterChange,
  onTierFilterChange,
  onStatusFilterChange,
}: TestsTabProps) => {
  return (
    <motion.div
      key="tests"
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
            <label className="mb-2 block text-sm font-medium text-gray-700">Test Type</label>
            <select
              value={testFilter}
              onChange={(e) => onTestFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Tests</option>
              <option value="addition">Addition</option>
              <option value="subtraction">Subtraction</option>
              <option value="multiplication">Multiplication</option>
              <option value="division">Division</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Rank/Tier</label>
            <select
              value={tierFilter}
              onChange={(e) => onTierFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 px-4 py-2 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Ranks</option>
              <option value="B">B Rank</option>
              <option value="A">A Rank</option>
              <option value="S">S Rank</option>
              <option value="SS">SS Rank</option>
              <option value="SSS">SSS Rank</option>
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

      {/* Test Achievement Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredTestAchievements.map((achievement, index) => (
          <AchievementCard key={achievement.id} achievement={achievement} index={index} />
        ))}
      </div>

      {filteredTestAchievements.length === 0 && (
        <div className="py-16 text-center">
          <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
          <p className="text-lg text-gray-500">No test achievements match your filters</p>
        </div>
      )}
    </motion.div>
  )
}

