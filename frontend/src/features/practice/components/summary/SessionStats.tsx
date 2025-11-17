import { motion } from 'framer-motion'
import { Award, CheckCircle, XCircle, Flag, Clock } from 'lucide-react'
import type { SummaryMetrics } from '../../hooks/useSummaryData'

type SessionStatsProps = {
  metrics: SummaryMetrics
}

export const SessionStats = ({ metrics }: SessionStatsProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.9 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
        <Award className="w-5 h-5 text-blue-600" />
        Session Stats
      </h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-green-50 rounded-xl">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700">Correct</span>
          </div>
          <span className="text-lg font-bold text-green-700">{metrics.correctProblems}</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-red-50 rounded-xl">
          <div className="flex items-center gap-3">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-sm font-medium text-gray-700">Incorrect</span>
          </div>
          <span className="text-lg font-bold text-red-700">{metrics.incorrectProblems}</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-xl">
          <div className="flex items-center gap-3">
            <Flag className="w-5 h-5 text-yellow-600" />
            <span className="text-sm font-medium text-gray-700">Flagged</span>
          </div>
          <span className="text-lg font-bold text-yellow-700">{metrics.flaggedProblems}</span>
        </div>
        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-xl">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700">Total Time</span>
          </div>
          <span className="text-lg font-bold text-blue-700">{Math.round(metrics.totalTime)}s</span>
        </div>
      </div>
    </motion.div>
  )
}

