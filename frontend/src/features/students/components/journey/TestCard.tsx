import React from 'react'
import { motion } from 'framer-motion'
import { Lock, Play, Eye } from 'lucide-react'
import type { FrontendTest } from '../../utils/testMapping'

type TestCardProps = {
  test: FrontendTest
  index: number
  onClick: (test: FrontendTest) => void
  onStartTest?: (test: FrontendTest) => void
}

const getTierColor = (tier: 'B' | 'A' | 'S' | 'SS' | 'SSS'): string => {
  switch (tier) {
    case 'SSS':
      return 'from-purple-600 to-pink-600'
    case 'SS':
      return 'from-blue-600 to-purple-600'
    case 'S':
      return 'from-green-500 to-emerald-600'
    case 'A':
      return 'from-yellow-500 to-orange-500'
    case 'B':
      return 'from-gray-500 to-gray-600'
    default:
      return 'from-gray-500 to-gray-600'
  }
}

export const TestCard: React.FC<TestCardProps> = ({ test, index, onClick, onStartTest }) => {
  const isLocked = test.isLocked
  const hasAttempts = test.attemptCount > 0

  return (
    <motion.div
      data-testid={`testid-test-card-${test.test_type}`}
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        delay: index * 0.05,
      }}
      className={`relative cursor-pointer rounded-2xl border-2 p-6 transition-all hover:shadow-lg ${
        isLocked
          ? 'border-gray-300 bg-gray-100'
          : hasAttempts
            ? 'border-blue-300 bg-gradient-to-br from-blue-50 to-purple-50 shadow-lg'
            : 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-lg'
      }`}
      onClick={() => !isLocked && onClick(test)}
    >
      {/* Lock Icon */}
      {isLocked && (
        <div className="absolute right-4 top-4">
          <Lock className="h-5 w-5 text-gray-400" data-testid="testid-test-lock-icon" />
        </div>
      )}

      {/* Test Name */}
      <h3 className={`mb-2 text-lg font-bold ${isLocked ? 'text-gray-500' : 'text-gray-900'}`}>
        {test.display_name}
      </h3>

      {/* Question Count Badge */}
      <div className="mb-3 inline-block rounded-full bg-gray-200 px-3 py-1 text-xs font-medium text-gray-700">
        {test.question_count} questions
      </div>

      {/* Level Requirement */}
      <div className={`mb-3 text-xs font-medium ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>
        {isLocked ? `Unlocks at Level ${test.level_requirement}` : `Level ${test.level_requirement}+`}
      </div>

      {/* Best Result Badge */}
      {test.bestResult && !isLocked && (
        <div
          className={`mb-3 inline-block rounded-full bg-gradient-to-r px-3 py-1 text-xs font-bold text-white ${getTierColor(test.bestResult.tier)}`}
          data-testid="testid-test-best-result-badge"
        >
          {test.bestResult.tier} Rank - {test.bestResult.accuracy.toFixed(0)}%
        </div>
      )}

      {/* Action Button */}
      {!isLocked && (
        <div className="mt-4 flex gap-2">
          {hasAttempts ? (
            <button
              data-testid="testid-test-view-results-button"
              onClick={(e) => {
                e.stopPropagation()
                onClick(test)
              }}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-500 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-blue-600"
            >
              <Eye className="h-4 w-4" />
              View Results
            </button>
          ) : (
            <button
              data-testid="testid-test-start-button"
              onClick={(e) => {
                e.stopPropagation()
                onStartTest?.(test)
              }}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-green-500 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-green-600"
            >
              <Play className="h-4 w-4" />
              Start Test
            </button>
          )}
        </div>
      )}
    </motion.div>
  )
}

