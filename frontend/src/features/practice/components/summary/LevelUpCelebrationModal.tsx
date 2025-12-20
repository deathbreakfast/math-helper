import { AnimatePresence, motion } from 'framer-motion'
import { Sparkles, X } from 'lucide-react'
import type { LevelUpResult } from '../../types'

type LevelUpCelebrationModalProps = {
  levelUp: LevelUpResult | null
  isOpen: boolean
  onClose: () => void
}

function getProgressPercent(levelUp: LevelUpResult | null): number {
  const progress = levelUp?.xp_progress
  if (!progress) return 0
  const denom = (progress.next_level_total_xp ?? progress.current_level_total_xp) - progress.current_level_total_xp
  if (!denom || denom <= 0) return 0
  return Math.max(0, Math.min(100, (progress.xp_into_level / denom) * 100))
}

export const LevelUpCelebrationModal = ({ levelUp, isOpen, onClose }: LevelUpCelebrationModalProps) => {
  const hasLeveledUp = levelUp?.leveled_up === true
  if (!hasLeveledUp) return null

  const newLevel = levelUp?.new_level
  const progress = levelUp?.xp_progress
  const earnedXp = levelUp?.earned_xp
  const progressPercent = getProgressPercent(levelUp)

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
            data-testid="testid-level-up-backdrop"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 16 }}
            transition={{ type: 'spring', stiffness: 240, damping: 22 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
            data-testid="testid-level-up-modal"
          >
            <div className="relative w-full max-w-xl overflow-hidden rounded-3xl bg-white shadow-2xl">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-pink-500 to-amber-400 opacity-90" />
              <div className="relative p-6 sm:p-8 text-white">
                <button
                  onClick={onClose}
                  className="absolute right-4 top-4 rounded-full bg-white/15 p-2 text-white hover:bg-white/25"
                  aria-label="Close level-up modal"
                >
                  <X className="h-5 w-5" />
                </button>

                <div className="flex items-center gap-3">
                  <div className="rounded-2xl bg-white/15 p-3">
                    <Sparkles className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white/90">Level Up!</div>
                    <div className="text-3xl sm:text-4xl font-extrabold tracking-tight">
                      Level {newLevel ?? '—'}
                    </div>
                  </div>
                </div>

                <div className="mt-6 rounded-2xl bg-white/15 p-4">
                  <div className="flex items-baseline justify-between gap-4">
                    <div className="text-sm font-semibold">XP progress</div>
                    {progress && (
                      <div className="text-xs text-white/90">
                        {progress.xp_into_level.toLocaleString()} /{' '}
                        {(
                          (progress.next_level_total_xp ?? progress.current_level_total_xp) -
                          progress.current_level_total_xp
                        ).toLocaleString()}{' '}
                        xp
                      </div>
                    )}
                  </div>
                  <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-white/20">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progressPercent}%` }}
                      transition={{ delay: 0.15, duration: 0.8, ease: 'easeOut' }}
                      className="h-full rounded-full bg-white"
                    />
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-3 text-xs text-white/90">
                  {typeof earnedXp === 'number' && (
                    <div className="rounded-full bg-white/15 px-3 py-1.5">
                      Earned this session: <span className="font-bold">{earnedXp.toLocaleString()}xp</span>
                    </div>
                  )}
                  {progress?.total_xp !== undefined && (
                    <div className="rounded-full bg-white/15 px-3 py-1.5">
                      Total XP: <span className="font-bold">{progress.total_xp.toLocaleString()}xp</span>
                    </div>
                  )}
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    onClick={onClose}
                    className="rounded-xl bg-white px-5 py-2.5 font-semibold text-purple-700 shadow hover:bg-white/95"
                    data-testid="testid-level-up-close"
                  >
                    Awesome!
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

