import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Play, ChevronDown, ChevronUp, Clock, Target, CheckCircle, XCircle } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import type { MathConcept } from '../../data/mathConcepts'
import PINVerificationModal from '../../modals/PINVerificationModal'
import type { User } from '../../hooks/useLearners'
import { logError } from '../../../../utils/logger'
import { getConceptAttempts, getConceptAttemptDetail, type ConceptAttempt, type ConceptAttemptDetail } from '../../hooks/useConceptAttempts'
import { getConceptXpPerCorrect } from '../../data/conceptXp'
import { extractTierFromCode } from '../../utils/achievementUtils'
import { QuestionResponseCard } from './QuestionResponseCard'

type MathConceptDetailModalProps = {
  concept: MathConcept | null
  isOpen: boolean
  onClose: () => void
  onStartPractice: (concept: MathConcept) => void
  selectedUser: User | null
}

export const MathConceptDetailModal: React.FC<MathConceptDetailModalProps> = ({
  concept,
  isOpen,
  onClose,
  onStartPractice,
  selectedUser,
}) => {
  const [attempts, setAttempts] = useState<(ConceptAttempt | ConceptAttemptDetail)[]>([])
  const [isLoadingAttempts, setIsLoadingAttempts] = useState(false)
  const [isPinModalOpen, setIsPinModalOpen] = useState(false)
  const [expandedAttemptIds, setExpandedAttemptIds] = useState<Set<number>>(new Set())
  const navigate = useNavigate()
  const params = useParams<{ userId?: string }>()
  const xpPerCorrect = concept ? getConceptXpPerCorrect(concept.conceptId) : null
  
  const handleAchievementClick = (achievementCode: string) => {
    if (params.userId) {
      navigate(`/journey/${params.userId}/achievements?achievement=${encodeURIComponent(achievementCode)}`)
    }
  }

  useEffect(() => {
    if (isOpen && concept && selectedUser) {
      loadAttempts()
    } else {
      setAttempts([])
    }
  }, [isOpen, concept, selectedUser])

  const loadAttempts = async () => {
    if (!concept || !selectedUser) return

    setIsLoadingAttempts(true)
    try {
      const conceptAttempts = await getConceptAttempts(concept.conceptId, selectedUser.id)
      setAttempts(conceptAttempts)
    } catch (error) {
      logError('Error loading concept attempts:', error)
    } finally {
      setIsLoadingAttempts(false)
    }
  }

  const handleExpandAttempt = async (attemptId: number) => {
    if (expandedAttemptIds.has(attemptId)) {
      setExpandedAttemptIds((prev) => {
        const next = new Set(prev)
        next.delete(attemptId)
        return next
      })
      return
    }

    try {
      const detail = await getConceptAttemptDetail(attemptId)
      if (detail) {
        // Update the attempt in the list with detailed data, preserving original attempt data
        setAttempts((prev) =>
          prev.map((attempt) => {
            if (attempt.attempt_id === attemptId) {
              // Merge detail with original attempt to preserve all fields
              return {
                ...attempt,
                ...detail,
                // Ensure we preserve the original attempt's data if detail is missing fields
                accuracy: detail.accuracy ?? attempt.accuracy,
                total_questions: detail.total_questions ?? attempt.total_questions,
                correct_count: detail.correct_count ?? attempt.correct_count,
                attempted_at: detail.attempted_at ?? attempt.attempted_at,
                total_duration_ms: detail.total_duration_ms ?? attempt.total_duration_ms,
              }
            }
            return attempt
          })
        )
        setExpandedAttemptIds((prev) => new Set(prev).add(attemptId))
      }
    } catch (error) {
      logError('Error loading attempt detail:', error)
    }
  }

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatTime = (ms: number | null | undefined): string => {
    if (!ms) return 'N/A'
    const seconds = ms / 1000
    return `${seconds.toFixed(1)}s`
  }

  const handleStartPracticeClick = () => {
    if (!concept) return
    setIsPinModalOpen(true)
  }

  const handlePinVerified = (pin: string) => {
    setIsPinModalOpen(false)
    if (concept) {
      onStartPractice(concept)
    }
  }

  if (!concept) return null

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <React.Fragment key="concept-detail-modal">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="fixed inset-0 z-40 bg-black/50"
              data-testid="testid-concept-detail-modal-backdrop"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-4 z-50 mx-auto max-h-[90vh] max-w-4xl overflow-hidden rounded-2xl bg-white shadow-2xl"
              data-testid="testid-concept-detail-modal"
            >
              {/* Header */}
              <div className="border-b border-gray-200 bg-gradient-to-r from-green-500 to-emerald-600 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-white" data-testid="testid-concept-detail-title">
                      {concept.displayName}
                    </h2>
                    <div className="mt-2 flex items-center gap-4 text-sm text-white/90">
                      <div className="flex items-center gap-1 capitalize" data-testid="testid-concept-detail-operation">
                        {concept.operation}
                      </div>
                      {concept.unlockRequirements.length > 0 && (
                        <div className="flex items-center gap-1" data-testid="testid-concept-detail-unlock-requirement">
                          {concept.unlockRequirements.filter(r => r.completed).length} / {concept.unlockRequirements.length} requirements met
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={onClose}
                    className="rounded-full bg-white/20 p-2 text-white transition-all hover:bg-white/30"
                    data-testid="testid-concept-detail-close-button"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="max-h-[calc(90vh-120px)] overflow-y-auto p-6">
                {/* Concept Info */}
                <div className="mb-6 rounded-xl bg-gray-50 p-4">
                  <h3 className="mb-2 font-semibold text-gray-900">Concept Information</h3>
                  <div className="space-y-1 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Operation:</span> {concept.operation}
                    </div>
                    {concept.layoutType && (
                      <div data-testid="testid-concept-detail-layout">
                        <span className="font-medium">Layout:</span> {concept.layoutType}
                      </div>
                    )}
                    {concept.answerFormat && (
                      <div data-testid="testid-concept-detail-answer-format">
                        <span className="font-medium">Answer Format:</span> {concept.answerFormat}
                      </div>
                    )}
                    {xpPerCorrect !== null && (
                      <div data-testid="testid-concept-detail-xp">
                        <span className="font-medium">XP:</span> {xpPerCorrect} per correct answer
                      </div>
                    )}
                    {concept.unlockRequirements.length > 0 && (
                      <div className="mt-3 rounded-lg border border-gray-200 bg-white p-3">
                        <div className="mb-2 font-semibold text-gray-900">Unlock Requirements</div>
                        <div className="mb-2">
                          <div className="mb-1 flex items-center justify-between text-xs">
                            <span>Progress:</span>
                            <span className="font-semibold">
                              {concept.unlockRequirements.filter(r => r.completed).length} / {concept.unlockRequirements.length}
                            </span>
                          </div>
                          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                            <div
                              className="h-full bg-green-500 transition-all"
                              style={{
                                width: `${(concept.unlockRequirements.filter(r => r.completed).length / concept.unlockRequirements.length) * 100}%`,
                              }}
                            />
                          </div>
                        </div>
                        <div className="text-xs text-gray-600 space-y-1">
                          {concept.unlockRequirements.map((req, idx) => {
                            // Extract tier and quantity from achievement code if available
                            let tier: string | null = null
                            let quantity: number | undefined = undefined
                            
                            if (req.achievementCode) {
                              // Extract tier from achievement code
                              const { tier: extractedTier } = extractTierFromCode(req.achievementCode)
                              tier = extractedTier
                              
                              // Get quantity from maxProgress
                              quantity = req.maxProgress && req.maxProgress > 1 ? req.maxProgress : undefined
                            }
                            
                            return (
                              <div
                                key={idx}
                                className={req.completed ? 'text-green-600' : 'text-gray-500'}
                              >
                                {req.completed ? '✓' : '○'} {req.description}
                                {tier && (
                                  <span className="ml-1 font-semibold">({tier}{quantity ? ` • Qty: ${quantity}` : ''})</span>
                                )}
                                {!tier && quantity && (
                                  <span className="ml-1 font-semibold">(Qty: {quantity})</span>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                    {concept.bestAccuracy && (
                      <div>
                        <span className="font-medium">Best Accuracy:</span> {concept.bestAccuracy.toFixed(0)}%
                      </div>
                    )}
                  </div>
                </div>

                {/* Past Attempts */}
                <div className="mb-6">
                  <h3 className="mb-4 text-lg font-semibold text-gray-900">Past Attempts</h3>
                  {isLoadingAttempts ? (
                    <div className="text-center text-gray-500">Loading attempts...</div>
                  ) : attempts.length === 0 ? (
                    <div className="rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 p-8 text-center text-gray-500">
                      No attempts yet. Start your first practice session!
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {attempts.map((attempt, index) => {
                        const isExpanded = expandedAttemptIds.has(attempt.attempt_id)
                        const hasQuestions = 'questions' in attempt && attempt.questions && attempt.questions.length > 0
                        const avgTimePerQuestion = attempt.total_duration_ms && attempt.total_questions
                          ? attempt.total_duration_ms / attempt.total_questions
                          : null
                        const passed = attempt.accuracy >= 80

                        return (
                          <motion.div
                            key={attempt.attempt_id || `attempt-${index}`}
                            data-testid={`testid-practice-attempt-${attempt.attempt_id}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className={`rounded-xl border-2 p-4 ${
                              passed
                                ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50'
                                : 'border-red-300 bg-gradient-to-br from-red-50 to-pink-50'
                            }`}
                          >
                            {/* Header */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                {passed ? (
                                  <CheckCircle className="h-5 w-5 text-green-500" data-testid="testid-attempt-passed" />
                                ) : (
                                  <XCircle className="h-5 w-5 text-red-500" data-testid="testid-attempt-failed" />
                                )}
                                <div>
                                  <div className="text-sm font-medium text-gray-600">{formatDate(attempt.attempted_at)}</div>
                                  <div className="text-xs text-gray-500">
                                    {passed ? 'Passed' : 'Failed'} - {attempt.accuracy.toFixed(1)}% accuracy
                                  </div>
                                </div>
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
                                {formatTime(avgTimePerQuestion)} avg
                              </div>
                              <div className="text-gray-600" data-testid="testid-attempt-question-count">
                                {attempt.total_questions} questions
                              </div>
                            </div>

                            {/* Expand Button */}
                            {!hasQuestions && (
                              <button
                                data-testid="testid-attempt-expand-button"
                                onClick={() => handleExpandAttempt(attempt.attempt_id)}
                                className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 transition-all hover:bg-gray-200"
                              >
                                {isExpanded ? (
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
                              {isExpanded && hasQuestions && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: 'auto', opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  transition={{ duration: 0.3 }}
                                  className="mt-4 space-y-2 overflow-hidden"
                                  data-testid="testid-attempt-questions-list"
                                >
                                  {attempt.questions?.map((question, qIndex) => (
                                    <QuestionResponseCard
                                      key={question.question_id || qIndex}
                                      question={{
                                        question_id: question.question_id,
                                        prompt: question.prompt,
                                        correct_answer: question.correct_answer,
                                        user_answer: question.submitted_answer,
                                        is_correct: question.is_correct,
                                        time_taken_ms: question.duration_ms || 0,
                                        answered_at: null,
                                      }}
                                      index={qIndex}
                                    />
                                  ))}
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </motion.div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>

              {/* Footer Actions */}
              <div className="border-t border-gray-200 bg-gray-50 p-6">
                <div className="flex gap-3">
                  <button
                    onClick={handleStartPracticeClick}
                    className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-3 font-semibold text-white transition-all hover:from-green-600 hover:to-emerald-700"
                    data-testid="testid-concept-detail-start-button"
                  >
                    <Play className="h-5 w-5" />
                    Start Practice
                  </button>
                  <button
                    onClick={onClose}
                    className="rounded-xl border-2 border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 transition-all hover:bg-gray-50"
                    data-testid="testid-concept-detail-close-footer-button"
                  >
                    Close
                  </button>
                </div>
              </div>
            </motion.div>
          </React.Fragment>
        )}
      </AnimatePresence>
      {/* PIN Verification Modal - outside AnimatePresence to avoid nesting */}
      <PINVerificationModal
        isOpen={isPinModalOpen}
        onClose={() => setIsPinModalOpen(false)}
        onVerified={handlePinVerified}
        selectedUser={selectedUser}
      />
    </>
  )
}
