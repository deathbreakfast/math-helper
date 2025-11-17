import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, Flag } from 'lucide-react'
import type { ProblemResult } from '../../hooks/useSummaryData'
import { getOperationSymbol, getOperationColor } from '../../utils/summaryUtils'

type ProblemDetailModalProps = {
  problem: ProblemResult | null
  onClose: () => void
}

export const ProblemDetailModal = ({ problem, onClose }: ProblemDetailModalProps) => {
  if (!problem) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Problem Details</h2>
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center ${
                problem.isCorrect ? 'bg-green-100' : 'bg-red-100'
              }`}
            >
              {problem.isCorrect ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-red-600" />
              )}
            </div>
          </div>
          <div className="space-y-4">
            <div className={`p-4 rounded-xl ${getOperationColor(problem.operation)}`}>
              <div className="text-center text-4xl font-bold mb-2">
                {problem.operand1} {getOperationSymbol(problem.operation)} {problem.operand2}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 rounded-xl">
                <div className="text-sm text-gray-600 mb-1">Correct Answer</div>
                <div className="text-2xl font-bold text-green-700">{problem.correctAnswer}</div>
              </div>
              <div className={`p-4 rounded-xl ${problem.isCorrect ? 'bg-green-50' : 'bg-red-50'}`}>
                <div className="text-sm text-gray-600 mb-1">Your Answer</div>
                <div className={`text-2xl font-bold ${problem.isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                  {problem.userAnswer ?? '—'}
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <span className="text-sm font-medium text-gray-600">Time Spent</span>
              <span className="text-lg font-bold text-gray-900">{problem.timeSpent.toFixed(1)}s</span>
            </div>
            {problem.isMarkedForReview && (
              <div className="flex items-center gap-2 p-4 bg-yellow-50 rounded-xl border-2 border-yellow-200">
                <Flag className="w-5 h-5 text-yellow-600 fill-yellow-600" />
                <span className="text-sm font-medium text-yellow-700">Flagged for review</span>
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="mt-6 w-full px-6 py-3 bg-gray-200 text-gray-800 rounded-xl hover:bg-gray-300 transition-colors font-medium"
          >
            Close
          </button>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

