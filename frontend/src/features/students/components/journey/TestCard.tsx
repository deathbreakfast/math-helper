import React from 'react'
import { motion } from 'framer-motion'
import { Lock, Play, Eye, Info } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import type { FrontendTest, NewTier } from '../../utils/testMapping'

type TestCardProps = {
  test: FrontendTest
  index: number
  onClick: (test: FrontendTest) => void
  onStartTest?: (test: FrontendTest) => void
  matchesFilter?: boolean
}

const getTierColor = (tier: NewTier): string => {
  switch (tier) {
    case 'Champion':
      return 'from-yellow-400 via-orange-500 to-red-600'
    case 'Divine':
      return 'from-purple-600 to-pink-600'
    case 'Mythic':
      return 'from-indigo-600 to-purple-600'
    case 'Legendary':
      return 'from-blue-600 to-indigo-600'
    case 'Grandmaster':
      return 'from-cyan-500 to-blue-600'
    case 'Master':
      return 'from-teal-500 to-cyan-600'
    case 'Diamond':
      return 'from-blue-400 to-cyan-500'
    case 'Platinum':
      return 'from-gray-300 to-gray-400'
    case 'Gold':
      return 'from-yellow-400 to-yellow-600'
    case 'Silver':
      return 'from-gray-200 to-gray-400'
    case 'Bronze':
      return 'from-orange-600 to-orange-800'
    default:
      return 'from-gray-500 to-gray-600'
  }
}

export const TestCard: React.FC<TestCardProps> = ({ test, index, onClick, onStartTest, matchesFilter = true }) => {
  const isLocked = test.isLocked
  const hasAttempts = test.attemptCount > 0
  const navigate = useNavigate()
  const params = useParams<{ userId?: string }>()
  
  const handleAchievementClick = (e: React.MouseEvent, achievementCode: string) => {
    e.stopPropagation()
    if (params.userId) {
      navigate(`/journey/${params.userId}/achievements?achievement=${encodeURIComponent(achievementCode)}`)
    }
  }
  
  // Get list of achievement codes to display
  const achievementCodes = test.unlockRequirements?.achievementCodes || 
    (test.unlockRequirements?.achievementCode ? [test.unlockRequirements.achievementCode] : [])
  
  // Helper to format achievement code with metadata
  const formatAchievementCode = (code: string): string => {
    const metadataFilter = test.unlockRequirements?.metadataFilters?.[code]
    if (metadataFilter) {
      const parts: string[] = []
      if (metadataFilter.level) parts.push(`Level ${metadataFilter.level}`)
      if (metadataFilter.operation) parts.push(metadataFilter.operation)
      if (parts.length > 0) {
        return `${code.replace(/-/g, ' ')} (${parts.join(', ')})`
      }
    }
    return code.replace(/-/g, ' ')
  }

  return (
    <motion.div
      data-testid={`testid-test-card-${test.test_type}`}
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: isLocked ? 0.5 : matchesFilter ? 1 : 0.6,
        y: 0,
      }}
      transition={{
        delay: index * 0.05,
      }}
      className={`relative rounded-2xl border-2 p-6 transition-all ${
        isLocked
          ? 'cursor-not-allowed border-gray-300 bg-gray-100'
          : matchesFilter
            ? 'cursor-pointer hover:shadow-lg'
            : 'cursor-pointer opacity-60 hover:shadow-md'
      } ${
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

      {/* Unlock Requirements or Level Requirement */}
      {test.unlockRequirements ? (
        <div className={`mb-3 space-y-1 text-xs ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>
          <div className="font-medium flex items-center gap-2">
            {isLocked ? 'Unlock Requirements:' : 'Unlocked'}
            <Info 
              className="h-3 w-3 text-gray-400 hover:text-gray-600 cursor-help" 
              title="Higher tier achievements can substitute for lower tier requirements (e.g., 4 Bronze = 2 Silver = 1 Gold)"
            />
          </div>
          {test.unlockProgress && (
            <div className="text-xs font-semibold mb-1">
              {test.unlockProgress.met}/{test.unlockProgress.total} achievements
            </div>
          )}
          {achievementCodes.length > 0 && (
            <div className="space-y-1">
              {achievementCodes.map((code, idx) => (
                <div
                  key={idx}
                  onClick={(e) => handleAchievementClick(e, code)}
                  className="text-xs cursor-pointer hover:underline hover:text-blue-600 transition-colors"
                  title={`Click to view ${code.replace(/-/g, ' ')} achievement`}
                >
                  • {formatAchievementCode(code)}
                </div>
              ))}
            </div>
          )}
          {test.unlockRequirements.level && (
            <div className="text-xs mt-1">
              at level {test.unlockRequirements.level}
            </div>
          )}
          {test.unlockRequirements.minAccuracy && (
            <div className="text-xs mt-1">
              ({(test.unlockRequirements.minAccuracy * 100).toFixed(0)}%+ accuracy)
            </div>
          )}
        </div>
      ) : (
        <div className={`mb-3 text-xs font-medium ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}>
          {isLocked ? `Unlocks at Level ${test.level_requirement}` : `Level ${test.level_requirement}+`}
        </div>
      )}

      {/* Best Result Badge */}
      {test.bestResult && !isLocked && (
        <div
          className={`mb-3 inline-block rounded-full bg-gradient-to-r px-3 py-1 text-xs font-bold text-white ${getTierColor(test.bestResult.tier)}`}
          data-testid="testid-test-best-result-badge"
        >
          {test.bestResult.tier} Tier - {test.bestResult.accuracy.toFixed(0)}%
        </div>
      )}

      {/* Action Button */}
      {!isLocked ? (
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
      ) : (
        <div className="mt-4 flex gap-2">
          <button
            disabled
            className="flex flex-1 cursor-not-allowed items-center justify-center gap-2 rounded-xl bg-gray-300 px-4 py-2 text-sm font-semibold text-gray-500"
          >
            <Lock className="h-4 w-4" />
            Locked
          </button>
        </div>
      )}
    </motion.div>
  )
}

