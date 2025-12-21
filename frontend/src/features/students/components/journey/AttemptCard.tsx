import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, ChevronUp, Clock, Target, CheckCircle, XCircle } from 'lucide-react'
import type { FrontendTestAttempt, FrontendTestAttemptDetail } from '../../utils/testMapping'
import { QuestionResponseCard } from './QuestionResponseCard'
import { logError } from '../../../../utils/logger'

type AttemptCardProps = {
  attempt: FrontendTestAttempt | FrontendTestAttemptDetail | {
    attempt_id: number
    accuracy: number
    avg_time_per_question_ms?: number | null
    tier: 'B' | 'A' | 'S' | 'SS' | 'SSS' | 'bronze' | 'silver' | 'gold'
    passed: boolean
    attempted_at: string | null
    question_count?: number
    correct_count?: number
    total_questions?: number
    total_duration_ms?: number
    questions?: Array<any>
  }
  index: number
  onExpand?: (attemptId: number) => Promise<any>
}

const getTierColor = (tier: 'B' | 'A' | 'S' | 'SS' | 'SSS' | 'bronze' | 'silver' | 'gold'): string => {
  switch (tier) {
    case 'SSS':
    case 'gold':
      return 'from-purple-600 to-pink-600'
    case 'SS':
    case 'silver':
      return 'from-blue-600 to-purple-600'
    case 'S':
      return 'from-green-500 to-emerald-600'
    case 'A':
      return 'from-yellow-500 to-orange-500'
    case 'B':
    case 'bronze':
      return 'from-gray-500 to-gray-600'
    default:
      return 'from-gray-500 to-gray-600'
  }
}

const formatTierLabel = (tier: 'B' | 'A' | 'S' | 'SS' | 'SSS' | 'bronze' | 'silver' | 'gold'): string => {
  // Capitalize first letter for display
  return tier.charAt(0).toUpperCase() + tier.slice(1)
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Unknown date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTime = (ms: number | null): string => {
  if (!ms) return 'N/A'
  const seconds = ms / 1000
  return `${seconds.toFixed(1)}s`
}

export const AttemptCard: React.FC<AttemptCardProps> = ({ attempt, index, onExpand }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [detailedAttempt, setDetailedAttempt] = useState<FrontendTestAttemptDetail | null>(
    'questions' in attempt ? attempt : null
  )

  const hasQuestions = 'questions' in attempt && attempt.questions.length > 0
  const canExpand = onExpand && !hasQuestions

  const handleExpand = async () => {
    if (!canExpand || !onExpand) return

    if (isExpanded) {
      setIsExpanded(false)
      return
    }

    setIsLoading(true)
    try {
      const detail = await onExpand(attempt.attempt_id)
      if (detail) {
        setDetailedAttempt(detail)
        setIsExpanded(true)
      }
    } catch (error) {
      logError('Error loading attempt details:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const questions = detailedAttempt?.questions || (hasQuestions ? attempt.questions : [])

  return (
    <motion.div
      data-testid={`testid-attempt-card-${attempt.attempt_id}`}
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
      className={`rounded-xl border-2 p-4 ${
        attempt.passed
          ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50'
          : 'border-red-300 bg-gradient-to-br from-red-50 to-pink-50'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {attempt.passed ? (
            <CheckCircle className="h-5 w-5 text-green-500" data-testid="testid-attempt-passed" />
          ) : (
            <XCircle className="h-5 w-5 text-red-500" data-testid="testid-attempt-failed" />
          )}
          <div>
            <div className="text-sm font-medium text-gray-600">{formatDate(attempt.attempted_at)}</div>
            <div className="text-xs text-gray-500">
              {attempt.passed ? 'Passed' : 'Failed'} - {attempt.accuracy.toFixed(1)}% accuracy
            </div>
          </div>
        </div>

        {/* Tier Badge */}
        <div
          className={`rounded-full bg-gradient-to-r px-3 py-1 text-xs font-bold text-white ${getTierColor(attempt.tier)}`}
          data-testid="testid-attempt-tier-badge"
        >
          {formatTierLabel(attempt.tier)} Rank
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 flex gap-4 text-sm">
        <div className="flex items-center gap-1 text-gray-600" data-testid="testid-attempt-accuracy">
          <Target className="h-4 w-4" />
          {attempt.accuracy.toFixed(1)}%
        </div>
        <div className="flex items-center gap-1 text-gray-600" data-testid="testid-attempt-avg-time">
          <Clock className="h-4 w-4" />
          {formatTime(attempt.avg_time_per_question_ms)} avg
        </div>
        {attempt.question_count && (
          <div className="text-gray-600" data-testid="testid-attempt-question-count">
            {attempt.question_count} questions
          </div>
        )}
      </div>

      {/* Expand Button */}
      {canExpand && (
        <button
          data-testid="testid-attempt-expand-button"
          onClick={handleExpand}
          disabled={isLoading}
          className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 transition-all hover:bg-gray-200 disabled:opacity-50"
        >
          {isLoading ? (
            'Loading...'
          ) : isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Hide Questions
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              View Questions
            </>
          )}
        </button>
      )}

      {/* Questions List */}
      <AnimatePresence>
        {isExpanded && questions.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-4 space-y-2 overflow-hidden"
            data-testid="testid-attempt-questions-list"
          >
            {questions.map((question, qIndex) => (
              <QuestionResponseCard key={question.question_id || qIndex} question={question} index={qIndex} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

