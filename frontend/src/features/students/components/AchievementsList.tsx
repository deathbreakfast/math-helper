import { motion } from 'framer-motion'
import { Trophy } from 'lucide-react'
import SectionHeader from '../../../components/common/SectionHeader'
import FilterChips from '../../../components/common/FilterChips'
import type { Achievement } from '../hooks/useLearners'

type AchievementWithUser = Achievement & { userName?: string }

type Props = {
  title: string
  achievements: AchievementWithUser[]
  filterCategory?: string
  onFilterChange?: (category: string) => void
  filterOptions?: string[]
  emptyMessage?: string
  layout?: 'grid' | 'list'
  isLoading?: boolean
  skeletonCount?: number
}

const AchievementsList = ({
  title,
  achievements,
  filterCategory,
  onFilterChange,
  filterOptions = [],
  emptyMessage = 'No achievements yet. Keep practicing!',
  layout = 'list',
  isLoading = false,
  skeletonCount = layout === 'grid' ? 6 : 3,
}: Props) => {
  const listClass =
    layout === 'grid' ? 'grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3' : 'space-y-3'
  const cardClass =
    layout === 'grid'
      ? 'border-purple-100 bg-gradient-to-r from-purple-50 to-pink-50 p-4'
      : 'border-amber-100 bg-gradient-to-r from-yellow-50 to-amber-50 p-4'

  const renderSkeletons = () => (
    <div className={listClass}>
      {Array.from({ length: skeletonCount }).map((_, index) => (
        <div
          key={`achievement-skeleton-${index}`}
          className={`flex items-start gap-4 rounded-2xl border ${cardClass} animate-pulse`}
        >
          <div className="h-10 w-10 rounded-full bg-white/60" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-20 rounded-full bg-white/60" />
            <div className="h-4 w-32 rounded-full bg-white/80" />
            <div className="h-3 w-40 rounded-full bg-white/70" />
            <div className="h-3 w-24 rounded-full bg-white/60" />
          </div>
        </div>
      ))}
    </div>
  )

  const renderAchievements = () => (
    <div className={listClass}>
      {achievements.map((achievement, index) => (
        <motion.div
          key={achievement.id}
          initial={{ opacity: 0, x: layout === 'grid' ? 0 : 20, scale: layout === 'grid' ? 0.9 : 1 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ delay: 0.1 * index }}
          className={`flex items-start gap-4 rounded-2xl border ${cardClass}`}
        >
          <div className="text-3xl">{achievement.icon}</div>
          <div className="flex-1">
            {achievement.userName && <div className="text-sm font-semibold text-purple-900">{achievement.userName}</div>}
            <div className="font-semibold text-slate-900">{achievement.title}</div>
            <div className="text-sm text-slate-600">{achievement.description}</div>
            <div className="text-xs text-slate-500">{achievement.earnedAt.toLocaleDateString()}</div>
          </div>
        </motion.div>
      ))}
    </div>
  )

  return (
    <motion.div
      data-testid="testid-achievements-list"
      initial={{ opacity: 0, y: layout === 'grid' ? 12 : 0 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl bg-white p-6 shadow-card ${layout === 'grid' ? 'mt-10' : ''}`}
    >
      <SectionHeader title={title}>
        {filterCategory && onFilterChange && (
          <FilterChips options={filterOptions} value={filterCategory} onChange={onFilterChange} />
        )}
      </SectionHeader>

      {isLoading ? (
        renderSkeletons()
      ) : achievements.length > 0 ? (
        renderAchievements()
      ) : (
        <div className="py-8 text-center text-slate-500">
          <Trophy className="mx-auto mb-3 h-12 w-12 text-slate-300" />
          <p>{emptyMessage}</p>
        </div>
      )}
    </motion.div>
  )
}

export default AchievementsList

