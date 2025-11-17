import { motion } from 'framer-motion'
import { Target, Clock, Zap, Flag } from 'lucide-react'
import type { SummaryMetrics } from '../../hooks/useSummaryData'

type SummaryStatsCardsProps = {
  metrics: SummaryMetrics
}

export const SummaryStatsCards = ({ metrics }: SummaryStatsCardsProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Accuracy Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-2xl p-6 shadow-lg relative overflow-hidden"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <Target className="w-6 h-6 text-green-600" />
          </div>
          {metrics.isNewBestAccuracy && (
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              className="bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full"
            >
              NEW BEST!
            </motion.div>
          )}
        </div>
        <div className="text-sm font-medium text-gray-600 mb-1">Accuracy</div>
        <div className="text-4xl font-bold text-gray-900 mb-2">{metrics.accuracy}%</div>
        <div className="text-sm text-gray-500">
          {metrics.correctProblems} of {metrics.totalProblems} correct
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-2 bg-gray-100">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${metrics.accuracy}%` }}
            transition={{ delay: 0.5, duration: 1 }}
            className="h-full bg-gradient-to-r from-green-400 to-green-600"
          />
        </div>
      </motion.div>

      {/* Speed Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-2xl p-6 shadow-lg relative overflow-hidden"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <Clock className="w-6 h-6 text-blue-600" />
          </div>
          {metrics.isNewBestSpeed && (
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              className="bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full"
            >
              NEW BEST!
            </motion.div>
          )}
        </div>
        <div className="text-sm font-medium text-gray-600 mb-1">Avg Speed</div>
        <div className="text-4xl font-bold text-gray-900 mb-2">{metrics.averageSpeed}s</div>
        <div className="text-sm text-gray-500">Per question</div>
      </motion.div>

      {/* Streak Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-2xl p-6 shadow-lg"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-orange-600" />
          </div>
        </div>
        <div className="text-sm font-medium text-gray-600 mb-1">Current Streak</div>
        <div className="text-4xl font-bold text-gray-900 mb-2">{metrics.currentStreak}</div>
        <div className="text-sm text-gray-500">Days in a row</div>
      </motion.div>

      {/* Review Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white rounded-2xl p-6 shadow-lg"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center">
            <Flag className="w-6 h-6 text-yellow-600" />
          </div>
        </div>
        <div className="text-sm font-medium text-gray-600 mb-1">Flagged for Review</div>
        <div className="text-4xl font-bold text-gray-900 mb-2">{metrics.flaggedProblems}</div>
        <div className="text-sm text-gray-500">Problems marked</div>
      </motion.div>
    </div>
  )
}

