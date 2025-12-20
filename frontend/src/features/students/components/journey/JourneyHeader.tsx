import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { getTierColor } from '../../utils/achievementUtils'
import type { UserProgressData } from '../../utils/progressMapping'

type JourneyHeaderProps = {
  userData: UserProgressData
  onBack?: () => void
}

export const JourneyHeader = ({ userData, onBack }: JourneyHeaderProps) => {
  const progress = userData.xp_progress
  const hasNext = progress?.next_level_total_xp !== null && progress?.next_level_total_xp !== undefined
  const current = progress?.total_xp ?? userData.experience ?? 0
  const currentLevelBase = progress?.current_level_total_xp ?? 0
  const nextLevelTotal = progress?.next_level_total_xp ?? null
  const denom = hasNext ? Math.max(1, (nextLevelTotal as number) - currentLevelBase) : 1
  const numer = hasNext ? Math.max(0, current - currentLevelBase) : 1
  const pct = hasNext ? Math.min(100, Math.round((numer / denom) * 100)) : 100

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: -20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="mb-8 flex items-center justify-between"
    >
      <div className="flex items-center gap-4">
        {onBack && (
          <button onClick={onBack} className="rounded-xl p-2 transition-colors hover:bg-white/50">
            <ChevronRight className="h-6 w-6 rotate-180 text-gray-700" />
          </button>
        )}
        <div>
          <h1 className="mb-2 flex items-center gap-3 text-4xl font-bold text-gray-900">
            <span className="text-5xl">{userData.avatar}</span>
            {userData.name}'s Journey
          </h1>
          <p className="text-gray-600">Track your achievements and level progression</p>
        </div>
      </div>
      <div
        data-testid="testid-current-level-display"
        className={`w-[320px] max-w-full rounded-2xl bg-gradient-to-r px-6 py-4 text-white shadow-lg ${getTierColor('Gold')}`}
      >
        <div className="flex items-end justify-between">
          <div>
            <div className="text-sm font-medium opacity-90">Level</div>
            <div className="text-3xl font-bold">{userData.level}</div>
          </div>
          <div className="text-right">
            <div className="text-xs font-medium opacity-90">XP</div>
            <div className="text-sm font-semibold">{current.toLocaleString()}</div>
          </div>
        </div>

        <div className="mt-3">
          <div className="mb-1 flex items-center justify-between text-xs opacity-90">
            {hasNext ? (
              <>
                <span>
                  {numer.toLocaleString()} / {denom.toLocaleString()}
                </span>
                <span>{pct}%</span>
              </>
            ) : (
              <>
                <span>Max level</span>
                <span>100%</span>
              </>
            )}
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-white/25">
            <div className="h-full rounded-full bg-white" style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

