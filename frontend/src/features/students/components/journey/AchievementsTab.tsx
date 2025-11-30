import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Search } from 'lucide-react'
import { AchievementCard } from '../AchievementCard'
import type { Achievement, AchievementType, AchievementStatus } from '../../data/achievements'

type AchievementsTabProps = {
  filteredAchievements: Achievement[]
  achievementFilter: 'all' | AchievementType | string
  statusFilter: 'all' | AchievementStatus
  textFilter: string
  onAchievementFilterChange: (filter: 'all' | AchievementType | string) => void
  onStatusFilterChange: (filter: 'all' | AchievementStatus) => void
  onTextFilterChange: (filter: string) => void
}

export const AchievementsTab = ({
  filteredAchievements,
  achievementFilter,
  statusFilter,
  textFilter,
  onAchievementFilterChange,
  onStatusFilterChange,
  onTextFilterChange,
}: AchievementsTabProps) => {
  // DEBUG: Log achievements being rendered in the tab
  // [STACK: AchievementsTab - Component render, before rendering cards]
  useEffect(() => {
    console.log(`[ACH-008] [ACHIEVEMENTS TAB] Filtered achievements count: ${filteredAchievements.length}`)
    console.log(`[ACH-008] [ACHIEVEMENTS TAB] Active filters: category=${achievementFilter}, status=${statusFilter}, text="${textFilter}"`)
    
    if (filteredAchievements.length > 0) {
      const achievementCodes = filteredAchievements.map(a => a.code || a.id || a.title).filter(Boolean)
      const achievementStatuses = filteredAchievements.map(a => a.status).filter(Boolean)
      console.log(`[ACH-008] [ACHIEVEMENTS TAB] Achievement codes to render:`, achievementCodes)
      console.log(`[ACH-008] [ACHIEVEMENTS TAB] Achievement statuses:`, achievementStatuses)
      
      // Check for our specific test achievements
      const hasFirstVictory = achievementCodes.some(code => code === 'first-victory' || String(code).includes('first-victory'))
      const hasAdditionBasics = achievementCodes.some(code => code === 'addition-basics' || String(code).includes('addition-basics'))
      console.log(`[ACH-008] [ACHIEVEMENTS TAB] Has first-victory: ${hasFirstVictory}, Has addition-basics: ${hasAdditionBasics}`)
    } else {
      console.warn(`[ACH-008] [ACHIEVEMENTS TAB] WARNING: No filtered achievements to render!`)
    }
  }, [filteredAchievements, achievementFilter, statusFilter, textFilter])
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
              <option value="test">Test</option>
              <option value="test-mastery">Test Mastery</option>
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

