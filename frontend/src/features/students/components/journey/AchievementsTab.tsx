import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Search } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import { AchievementDetailModal } from './AchievementDetailModal'
import type { Achievement, AchievementType, AchievementStatus } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'

type AchievementsTabProps = {
  filteredAchievements: Achievement[]
  achievementFilter: 'all' | AchievementType | string
  statusFilter: 'all' | AchievementStatus
  textFilter: string
  onAchievementFilterChange: (filter: 'all' | AchievementType | string) => void
  onStatusFilterChange: (filter: 'all' | AchievementStatus) => void
  onTextFilterChange: (filter: string) => void
  userId: string
  achievementDefinitions?: Record<string, BackendAchievementDefinition>
}

export const AchievementsTab = ({
  filteredAchievements,
  achievementFilter,
  statusFilter,
  textFilter,
  onAchievementFilterChange,
  onStatusFilterChange,
  onTextFilterChange,
  userId,
  achievementDefinitions,
}: AchievementsTabProps) => {
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Handle deep linking - check URL params for achievement code
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const achievementCode = params.get('achievement')
    if (achievementCode && filteredAchievements.length > 0) {
      const achievement = filteredAchievements.find(a => a.id === achievementCode)
      if (achievement) {
        setSelectedAchievement(achievement)
        setIsModalOpen(true)
        // Clean up URL
        params.delete('achievement')
        const newUrl = window.location.pathname + (params.toString() ? `?${params.toString()}` : '')
        window.history.replaceState({}, '', newUrl)
      }
    }
  }, [filteredAchievements])

  const handleAchievementClick = (achievement: Achievement) => {
    setSelectedAchievement(achievement)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedAchievement(null)
  }

  const selectedDefinition = selectedAchievement && achievementDefinitions
    ? achievementDefinitions[selectedAchievement.id]
    : null

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
              data-testid="testid-achievement-filter-category"
              value={achievementFilter}
              onChange={(e) => onAchievementFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-900 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              <option value="milestone">Milestones</option>
              <option value="accuracy">Accuracy</option>
              <option value="progression">Progression</option>
              <option value="consistency">Consistency</option>
              <option value="speed">Speed</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Status</label>
            <select
              data-testid="testid-achievement-filter-status"
              value={statusFilter}
              onChange={(e) => onStatusFilterChange(e.target.value as any)}
              className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 text-gray-900 outline-none focus:border-transparent focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="unlocked">Unlocked</option>
              <option value="in-progress">In Progress</option>
              <option value="locked">Locked</option>
            </select>
          </div>
          <div className="min-w-[200px] flex-1">
            <label className="mb-2 block text-sm font-medium text-gray-700">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <input
                data-testid="testid-achievement-search-input"
                type="text"
                value={textFilter}
                onChange={(e) => onTextFilterChange(e.target.value)}
                placeholder="Search achievements..."
                className="w-full rounded-xl border border-gray-300 bg-white px-4 py-2 pl-10 text-gray-900 outline-none placeholder:text-gray-400 focus:border-transparent focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Achievement Grid */}
      <div data-testid="testid-achievements-grid" className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredAchievements.map((achievement, index) => (
          <div
            key={achievement.id}
            onClick={() => handleAchievementClick(achievement)}
            className="cursor-pointer"
          >
            <AchievementCard achievement={achievement} index={index} />
          </div>
        ))}
      </div>

      {filteredAchievements.length === 0 && (
        <div className="py-16 text-center">
          <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
          <p className="text-lg text-gray-500">No achievements match your filters</p>
        </div>
      )}

      {/* Achievement Detail Modal */}
      <AchievementDetailModal
        achievement={selectedAchievement}
        achievementDefinition={selectedDefinition}
        userId={userId}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </motion.div>
  )
}

