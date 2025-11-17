import { motion } from 'framer-motion'
import { Filter, Eye, CheckCircle, XCircle, Flag } from 'lucide-react'
import type { ProblemResult, FilterType } from '../../hooks/useSummaryData'
import { getOperationSymbol } from '../../utils/summaryUtils'

type ProblemGridProps = {
  problems: ProblemResult[]
  filter: FilterType
  onFilterChange: (filter: FilterType) => void
  onProblemClick: (problem: ProblemResult) => void
}

export const ProblemGrid = ({ problems, filter, onFilterChange, onProblemClick }: ProblemGridProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.0 }}
      className="bg-white rounded-2xl shadow-lg p-6 mb-8"
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4">
        <h3 className="text-xl font-semibold text-gray-800">Problem Review</h3>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <div className="flex gap-2">
            {(['all', 'correct', 'incorrect', 'flagged'] as FilterType[]).map((filterType) => (
              <button
                key={filterType}
                onClick={() => onFilterChange(filterType)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  filter === filterType
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {problems.map((problem, index) => (
          <motion.button
            key={problem.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.1 + index * 0.05 }}
            onClick={() => onProblemClick(problem)}
            className={`relative p-4 rounded-xl font-semibold transition-all hover:scale-105 ${
              problem.isCorrect
                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                : 'bg-red-100 text-red-700 hover:bg-red-200'
            } ${problem.isMarkedForReview ? 'ring-2 ring-yellow-400' : ''}`}
          >
            <div className="text-xs mb-1 opacity-70">#{index + 1}</div>
            <div className="text-lg mb-1">
              {problem.operand1} {getOperationSymbol(problem.operation)} {problem.operand2}
            </div>
            <div className="absolute top-2 right-2">
              {problem.isCorrect ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
            </div>
            {problem.isMarkedForReview && (
              <div className="absolute bottom-2 right-2">
                <Flag className="w-3 h-3 fill-yellow-500 text-yellow-600" />
              </div>
            )}
          </motion.button>
        ))}
      </div>
      {problems.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <Eye className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No problems match this filter</p>
        </div>
      )}
    </motion.div>
  )
}

