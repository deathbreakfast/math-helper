import React from 'react'
import { motion } from 'framer-motion'
import { Lock, Play, Eye } from 'lucide-react'
import type { MathConcept } from '../../data/mathConcepts'
import { getConceptXpPerCorrect } from '../../data/conceptXp'
import { getConceptDisplayNameByConceptId } from '../../data/mathConcepts'

type MathConceptCardProps = {
  concept: MathConcept
  index: number
  onClick: (concept: MathConcept) => void
  onStartPractice?: (concept: MathConcept) => void
  matchesFilter?: boolean
  debugDependencies?: Array<{
    achievementName: string
    tier: string | null
    conceptRequirement: string | null
  }> // For debugging: show required achievements with metadata
}

export const MathConceptCard: React.FC<MathConceptCardProps> = ({ 
  concept, 
  index, 
  onClick, 
  onStartPractice,
  matchesFilter = true,
  debugDependencies = []
}) => {
  const isLocked = concept.isLocked
  const hasAttempts = concept.attemptCount > 0
  const xpPerCorrect = getConceptXpPerCorrect(concept.conceptId)

  return (
    <motion.div
      data-testid={`testid-concept-card-${concept.conceptId}`}
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
      className={`relative rounded-2xl border-2 p-4 transition-all flex flex-col ${
        isLocked
          ? 'cursor-pointer border-gray-300 bg-gray-100 hover:bg-gray-200'
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
      style={{ width: '203px', height: '203px' }}
      onClick={() => onClick(concept)}
    >
      {/* Lock Icon */}
      {isLocked && (
        <div className="absolute right-4 top-4">
          <Lock className="h-5 w-5 text-gray-400" data-testid="testid-concept-lock-icon" />
        </div>
      )}

      {/* Concept Name */}
      <h3 className={`mb-2 text-sm font-bold line-clamp-2 ${isLocked ? 'text-gray-500' : 'text-gray-900'}`}>
        {concept.displayName}
      </h3>

      {/* Operation Badge - TEMPORARILY HIDDEN */}
      {/* <div className="mb-2 inline-block rounded-full bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-700 capitalize">
        {concept.operation}
      </div> */}

      {/* XP per correct */}
      {xpPerCorrect !== null && (
        <div
          className={`mb-2 text-xs font-semibold ${isLocked ? 'text-gray-400' : 'text-gray-600'}`}
          data-testid="testid-concept-xp-per-correct"
        >
          XP: {xpPerCorrect} per correct
        </div>
      )}

      {/* DEBUG: Required Ancestors */}
      {debugDependencies && debugDependencies.length > 0 && (
        <div className="mb-2 space-y-1 text-xs text-gray-500">
          {debugDependencies.map((dep, idx) => (
            <div key={idx} className="text-xs">
              <div>
                - {dep.achievementName}{dep.tier ? ` (${dep.tier})` : ''}
              </div>
              {dep.conceptRequirement && (
                <div className="ml-4 text-gray-400">
                  {dep.conceptRequirement}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Best Result Badge */}
      {concept.bestAccuracy && !isLocked && (
        <div
          className="mb-2 inline-block rounded-full bg-gradient-to-r from-blue-500 to-purple-600 px-2 py-1 text-xs font-bold text-white"
          data-testid="testid-concept-best-accuracy-badge"
        >
          Best: {concept.bestAccuracy.toFixed(0)}%
        </div>
      )}

      {/* Action Button - TEMPORARILY HIDDEN */}
      {/* <div className="flex-1" />
      
      {!isLocked ? (
        <div className="mt-auto flex gap-2">
          {hasAttempts ? (
            <button
              data-testid="testid-concept-view-results-button"
              onClick={(e) => {
                e.stopPropagation()
                onClick(concept)
              }}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-blue-500 px-3 py-2 text-xs font-semibold text-white transition-all hover:bg-blue-600"
            >
              <Eye className="h-3 w-3" />
              View
            </button>
          ) : (
            <button
              data-testid="testid-concept-start-button"
              onClick={(e) => {
                e.stopPropagation()
                onStartPractice?.(concept)
              }}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-green-500 px-3 py-2 text-xs font-semibold text-white transition-all hover:bg-green-600"
            >
              <Play className="h-3 w-3" />
              Start
            </button>
          )}
        </div>
      ) : (
        <div className="mt-auto flex gap-2">
          <button
            disabled
            className="flex flex-1 cursor-not-allowed items-center justify-center gap-2 rounded-xl bg-gray-300 px-3 py-2 text-xs font-semibold text-gray-500"
          >
            <Lock className="h-3 w-3" />
            Locked
          </button>
        </div>
      )} */}
    </motion.div>
  )
}
