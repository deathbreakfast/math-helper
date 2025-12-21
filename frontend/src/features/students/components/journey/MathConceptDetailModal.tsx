import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Play } from 'lucide-react'
import { useNavigate, useParams } from 'react-router-dom'
import type { MathConcept } from '../../data/mathConcepts'
import { AttemptCard } from './AttemptCard'
import PINVerificationModal from '../../modals/PINVerificationModal'
import type { User } from '../../hooks/useLearners'
import { logError } from '../../../../utils/logger'
import { getConceptAttempts, getConceptAttemptDetail, type ConceptAttempt, type ConceptAttemptDetail } from '../../hooks/useConceptAttempts'
import { getConceptXpPerCorrect } from '../../data/conceptXp'

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
  const [attempts, setAttempts] = useState<ConceptAttempt[]>([])
  const [isLoadingAttempts, setIsLoadingAttempts] = useState(false)
  const [isPinModalOpen, setIsPinModalOpen] = useState(false)
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

  const handleExpandAttempt = async (attemptId: number): Promise<ConceptAttemptDetail | null> => {
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
      }
      return detail
    } catch (error) {
      logError('Error loading attempt detail:', error)
      return null
    }
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
                          {concept.unlockRequirements.map((req, idx) => (
                            <div
                              key={idx}
                              className={req.completed ? 'text-green-600' : 'text-gray-500'}
                            >
                              {req.completed ? '✓' : '○'} {req.description}
                            </div>
                          ))}
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
                        // Calculate tier based on accuracy ace logic (Bronze, Silver, Gold)
                        const getTier = (accuracy: number): 'bronze' | 'silver' | 'gold' => {
                          if (accuracy >= 100) return 'gold'   // 100% = Gold
                          if (accuracy >= 90) return 'silver'  // 90-99% = Silver
                          if (accuracy >= 80) return 'bronze' // 80-89% = Bronze
                          return 'bronze' // Below 80% still shows bronze (but marked as failed)
                        }

                        return (
                          <AttemptCard
                            key={attempt.attempt_id || `attempt-${index}`}
                            attempt={{
                              attempt_id: attempt.attempt_id,
                              test_type: concept.conceptId,
                              score: attempt.accuracy / 100, // Convert to 0-1 range
                              accuracy: attempt.accuracy,
                              tier: getTier(attempt.accuracy),
                              question_count: attempt.total_questions,
                              correct_count: attempt.correct_count,
                              avg_time_per_question_ms: attempt.total_duration_ms 
                                ? attempt.total_duration_ms / attempt.total_questions 
                                : undefined,
                              total_duration_ms: attempt.total_duration_ms,
                              attempted_at: attempt.attempted_at.toISOString(),
                              passed: attempt.accuracy >= 80, // 80% passing threshold
                            }}
                            index={index}
                            onExpand={handleExpandAttempt}
                          />
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
