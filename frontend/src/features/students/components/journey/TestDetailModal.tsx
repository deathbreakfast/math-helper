import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Play, Clock, Target } from 'lucide-react'
import type { FrontendTest, FrontendTestAttempt, FrontendTestAttemptDetail } from '../../utils/testMapping'
import { AttemptCard } from './AttemptCard'

type TestDetailModalProps = {
  test: FrontendTest | null
  isOpen: boolean
  onClose: () => void
  onStartTest: (test: FrontendTest) => void
  getTestAttempts: (testType: string) => Promise<FrontendTestAttempt[]>
  getTestAttemptDetail: (attemptId: number) => Promise<FrontendTestAttemptDetail | null>
}

export const TestDetailModal: React.FC<TestDetailModalProps> = ({
  test,
  isOpen,
  onClose,
  onStartTest,
  getTestAttempts,
  getTestAttemptDetail,
}) => {
  const [attempts, setAttempts] = useState<FrontendTestAttempt[]>([])
  const [isLoadingAttempts, setIsLoadingAttempts] = useState(false)

  useEffect(() => {
    if (isOpen && test) {
      loadAttempts()
    } else {
      setAttempts([])
    }
  }, [isOpen, test])

  const loadAttempts = async () => {
    if (!test) return

    setIsLoadingAttempts(true)
    try {
      const testAttempts = await getTestAttempts(test.test_type)
      setAttempts(testAttempts)
    } catch (error) {
      console.error('Error loading test attempts:', error)
    } finally {
      setIsLoadingAttempts(false)
    }
  }

  const handleExpandAttempt = async (attemptId: number): Promise<FrontendTestAttemptDetail | null> => {
    try {
      const detail = await getTestAttemptDetail(attemptId)
      if (detail) {
        // Update the attempt in the list with detailed data
        setAttempts((prev) =>
          prev.map((attempt) => (attempt.attempt_id === attemptId ? detail : attempt))
        )
      }
      return detail
    } catch (error) {
      console.error('Error loading attempt detail:', error)
      return null
    }
  }

  if (!test) return null

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-black/50"
            data-testid="testid-test-detail-modal-backdrop"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-4 z-50 mx-auto max-h-[90vh] max-w-4xl overflow-hidden rounded-2xl bg-white shadow-2xl"
            data-testid="testid-test-detail-modal"
          >
            {/* Header */}
            <div className="border-b border-gray-200 bg-gradient-to-r from-blue-500 to-purple-600 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-white" data-testid="testid-test-detail-title">
                    {test.display_name}
                  </h2>
                  <div className="mt-2 flex items-center gap-4 text-sm text-white/90">
                    <div className="flex items-center gap-1" data-testid="testid-test-detail-question-count">
                      <Target className="h-4 w-4" />
                      {test.question_count} questions
                    </div>
                    <div className="flex items-center gap-1" data-testid="testid-test-detail-level-requirement">
                      Level {test.level_requirement}+ required
                    </div>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="rounded-full bg-white/20 p-2 text-white transition-all hover:bg-white/30"
                  data-testid="testid-test-detail-close-button"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="max-h-[calc(90vh-120px)] overflow-y-auto p-6">
              {/* Test Info */}
              <div className="mb-6 rounded-xl bg-gray-50 p-4">
                <h3 className="mb-2 font-semibold text-gray-900">Test Information</h3>
                <div className="space-y-1 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">Operation:</span> {test.operation}
                  </div>
                  <div>
                    <span className="font-medium">Question Count:</span> {test.question_count}
                  </div>
                  <div>
                    <span className="font-medium">Level Requirement:</span> Level {test.level_requirement}
                  </div>
                  {test.bestResult && (
                    <div>
                      <span className="font-medium">Best Result:</span> {test.bestResult.tier} Rank -{' '}
                      {test.bestResult.accuracy.toFixed(0)}% accuracy
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
                    No attempts yet. Start your first test!
                  </div>
                ) : (
                  <div className="space-y-3">
                    {attempts.map((attempt, index) => (
                      <AttemptCard
                        key={attempt.attempt_id}
                        attempt={attempt}
                        index={index}
                        onExpand={handleExpandAttempt}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Footer Actions */}
            <div className="border-t border-gray-200 bg-gray-50 p-6">
              <div className="flex gap-3">
                <button
                  onClick={() => onStartTest(test)}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-3 font-semibold text-white transition-all hover:from-green-600 hover:to-emerald-700"
                  data-testid="testid-test-detail-start-button"
                >
                  <Play className="h-5 w-5" />
                  Start New Test
                </button>
                <button
                  onClick={onClose}
                  className="rounded-xl border-2 border-gray-300 bg-white px-6 py-3 font-semibold text-gray-700 transition-all hover:bg-gray-50"
                  data-testid="testid-test-detail-close-footer-button"
                >
                  Close
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

