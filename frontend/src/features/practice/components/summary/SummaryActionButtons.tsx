import { motion } from 'framer-motion'
import { Home, RotateCcw, ChevronRight, Flag } from 'lucide-react'
import type { PracticeSessionSummary, LevelUpResult } from '../../types'
import type { SummaryMetrics } from '../../hooks/useSummaryData'

type SummaryActionButtonsProps = {
  sessionSummary: PracticeSessionSummary | null
  metrics: SummaryMetrics
  levelUp: LevelUpResult | null
  onBackToDashboard: () => void
  onPracticeAgain: () => void
  onTryNextLevel: () => void
  onReviewFlagged: () => void
}

export const SummaryActionButtons = ({
  sessionSummary,
  metrics,
  levelUp,
  onBackToDashboard,
  onPracticeAgain,
  onTryNextLevel,
  onReviewFlagged,
}: SummaryActionButtonsProps) => {
  const hasLeveledUp = levelUp?.leveled_up === true

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.1 }}
      className="flex flex-col sm:flex-row items-center justify-center gap-4"
    >
      <button
        onClick={onBackToDashboard}
        data-testid="testid-summary-back-to-dashboard-button"
        className="flex items-center gap-2 px-8 py-4 bg-white text-gray-700 rounded-xl hover:bg-gray-50 transition-all shadow-lg hover:shadow-xl font-semibold"
      >
        <Home className="w-5 h-5" />
        Return to Dashboard
      </button>
      <button
        onClick={onPracticeAgain}
        data-testid="testid-practice-again-button"
        className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl font-semibold"
      >
        <RotateCcw className="w-5 h-5" />
        Practice Again
      </button>
      {hasLeveledUp && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1.3, type: 'spring' }}
          onClick={onTryNextLevel}
          data-testid="testid-try-next-level-button"
          className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl hover:from-purple-600 hover:to-pink-700 transition-all shadow-lg hover:shadow-xl font-semibold"
        >
          Try Next Level
          <ChevronRight className="w-5 h-5" />
        </motion.button>
      )}
      {metrics.flaggedProblems > 0 && (
        <button
          onClick={onReviewFlagged}
          data-testid="testid-review-flagged-button"
          className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-yellow-500 to-amber-600 text-white rounded-xl hover:from-yellow-600 hover:to-amber-700 transition-all shadow-lg hover:shadow-xl font-semibold"
        >
          <Flag className="w-5 h-5" />
          Review Flagged ({metrics.flaggedProblems})
        </button>
      )}
    </motion.div>
  )
}

