import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, Award, Info } from 'lucide-react'
import type { Achievement } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import { logError } from '../../../../utils/logger'
import { getTestDisplayName } from '../../utils/progressMapping/testDisplayNames'

type AchievementInstance = {
  id: string
  code: string
  title: string
  description: string
  icon: string
  category: string
  earnedAt: string
  metadata?: Record<string, any>
}

type AchievementDetailModalProps = {
  achievement: Achievement | null
  achievementDefinition: BackendAchievementDefinition | null
  userId: string
  isOpen: boolean
  onClose: () => void
}

export const AchievementDetailModal: React.FC<AchievementDetailModalProps> = ({
  achievement,
  achievementDefinition,
  userId,
  isOpen,
  onClose,
}) => {
  const [instances, setInstances] = useState<AchievementInstance[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (isOpen && achievement) {
      loadInstances()
    } else {
      setInstances([])
    }
  }, [isOpen, achievement, userId])

  const loadInstances = async () => {
    if (!achievement) return

    setIsLoading(true)
    try {
      // achievement.id should be the backend code (set in convertBackendDefinitionToFrontend)
      // But check both id and code fields as fallback
      const achievementCode = (achievement as any).code || achievement.id
      const response = await fetch(`/api/achievements?user_id=${userId}&code=${encodeURIComponent(achievementCode)}`)
      if (!response.ok) {
        throw new Error(`Failed to fetch achievement instances: ${response.status} ${response.statusText}`)
      }
      const data = await response.json()
      setInstances(data.achievements || [])
    } catch (error) {
      logError('Error loading achievement instances:', error)
      setInstances([])
    } finally {
      setIsLoading(false)
    }
  }

  const formatMetadata = (metadata?: Record<string, any>): string => {
    if (!metadata) return ''
    const parts: string[] = []
    if (metadata.level) {
      parts.push(`Level ${metadata.level}`)
    } else if (metadata.test_type) {
      // Show friendly test name for test sessions
      parts.push(getTestDisplayName(metadata.test_type))
    }
    if (metadata.operation) parts.push(metadata.operation)
    return parts.join(' • ')
  }

  if (!achievement) return null

  const definition = achievementDefinition || {
    title: achievement.title,
    description: achievement.description,
    icon: achievement.icon,
    category: achievement.category,
  }

  const reward = (achievementDefinition as any)?.xp_reward ?? (achievement as any)?.xp_reward
  const hasReward = !!reward && ((reward.bonus_xp ?? 0) > 0 || (reward.multiplier ?? 0) > 0)

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
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
            data-testid="testid-achievement-detail-modal"
          >
            <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl bg-white shadow-2xl">
              {/* Header */}
              <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white p-6">
                <div className="flex items-center gap-4">
                  <div className="text-5xl">{definition.icon}</div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{definition.title}</h2>
                    <p className="text-sm text-gray-600 mt-1">{definition.description}</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="rounded-full p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
                  aria-label="Close modal"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                {isLoading ? (
                  <div className="flex items-center justify-center py-12" data-testid="testid-achievement-modal-loading">
                    <div className="mr-3 h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"></div>
                    <div className="text-gray-500">Loading achievement history...</div>
                  </div>
                ) : instances.length === 0 ? (
                  <div className="py-12 text-center" data-testid="testid-achievement-modal-not-earned">
                    <Award className="mx-auto mb-4 h-16 w-16 text-gray-300" />
                    <p className="text-lg font-semibold text-gray-700">Not Yet Earned</p>
                    <p className="text-sm text-gray-500 mt-2">
                      This achievement hasn't been earned yet. Keep practicing to unlock it!
                    </p>
                    {hasReward && (
                      <div className="mt-4 rounded-lg bg-purple-50 p-4 border border-purple-200" data-testid="testid-achievement-modal-xp-reward">
                        <p className="text-sm font-semibold text-gray-700 mb-1">XP reward:</p>
                        <p className="text-sm text-gray-700">
                          Bonus: {(reward.bonus_xp ?? 0).toLocaleString()}xp
                          {(reward.multiplier ?? 0) > 0 ? ` • Multiplier: x${Number(reward.multiplier).toFixed(2)}` : ''}
                        </p>
                      </div>
                    )}
                    {/* Show requirement even when not earned */}
                    {achievement.requirement && (
                      <div className="mt-4 rounded-lg bg-gray-50 p-4">
                        <p className="text-sm font-semibold text-gray-700 mb-1">Requirement:</p>
                        <p className="text-sm text-gray-600">{achievement.requirement}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-4" data-testid="testid-achievement-modal-instances">
                    {/* Requirement section */}
                    {achievement.requirement && (
                      <div className="mb-6 rounded-lg bg-blue-50 p-4 border border-blue-200">
                        <p className="text-sm font-semibold text-gray-700 mb-1">Requirement:</p>
                        <p className="text-sm text-gray-600">{achievement.requirement}</p>
                      </div>
                    )}
                    {hasReward && (
                      <div className="mb-6 rounded-lg bg-purple-50 p-4 border border-purple-200" data-testid="testid-achievement-modal-xp-reward">
                        <p className="text-sm font-semibold text-gray-700 mb-1">XP reward:</p>
                        <p className="text-sm text-gray-700">
                          Bonus: {(reward.bonus_xp ?? 0).toLocaleString()}xp
                          {(reward.multiplier ?? 0) > 0 ? ` • Multiplier: x${Number(reward.multiplier).toFixed(2)}` : ''}
                        </p>
                      </div>
                    )}
                    <div className="mb-6 flex items-center gap-2 text-sm font-semibold text-gray-700">
                      <Info className="h-4 w-4" />
                      <span>Earned {instances.length} time{instances.length !== 1 ? 's' : ''}</span>
                    </div>

                    {instances.map((instance, index) => (
                      <motion.div
                        key={instance.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="rounded-xl border-2 border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50 p-4"
                        data-testid={`testid-achievement-instance-${instance.id}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Calendar className="h-4 w-4 text-gray-500" />
                              <span className="text-sm font-medium text-gray-700">
                                {new Date(instance.earnedAt).toLocaleDateString('en-US', {
                                  year: 'numeric',
                                  month: 'long',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </span>
                            </div>
                            {instance.metadata && (
                              <div className="mt-2 text-xs font-medium text-blue-700">
                                {formatMetadata(instance.metadata)}
                              </div>
                            )}
                          </div>
                          <div className="text-3xl">{instance.icon}</div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}



