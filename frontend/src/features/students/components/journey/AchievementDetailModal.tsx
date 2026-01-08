import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, Award, Info, Play } from 'lucide-react'
import type { Achievement } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import type { UserProgressData } from '../../utils/progressMapping'
import { logError } from '../../../../utils/logger'
import { getConceptDisplayNameByConceptId } from '../../data/mathConcepts'
import { useRouter } from '../../../../utils/routing'
import { useMathConcepts } from '../../hooks/useMathConcepts'

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
  conceptId?: string
  userData?: UserProgressData
}

export const AchievementDetailModal: React.FC<AchievementDetailModalProps> = ({
  achievement,
  achievementDefinition,
  userId,
  isOpen,
  onClose,
  conceptId,
  userData,
}) => {
  const router = useRouter()
  const [instances, setInstances] = useState<AchievementInstance[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  // Get math concepts to check if concept is locked
  const { concepts: mathConcepts } = useMathConcepts({
    userData,
    isActive: true,
    userId,
  })
  
  // Find the concept and check if it's locked
  const concept = useMemo(() => {
    if (!conceptId) return null
    return mathConcepts.find(c => c.conceptId === conceptId) || null
  }, [conceptId, mathConcepts])
  
  const isConceptLocked = concept ? concept.isLocked : false
  const conceptDisplayName = conceptId ? getConceptDisplayNameByConceptId(conceptId) : null
  
  // Handle start practice
  const handleStartPractice = useCallback(() => {
    if (!userData || !conceptId || isConceptLocked) return
    
    router.navigate('/practice', {
      user: userData.name,
      userId: userData.id,
      avatar: userData.avatar,
      conceptId: conceptId,
      isConcept: 'true',
    })
  }, [userData, conceptId, isConceptLocked, router])

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
    if (metadata.concept_id) {
      const conceptName = getConceptDisplayNameByConceptId(metadata.concept_id)
      if (conceptName) {
        parts.push(conceptName)
      } else {
        // Fallback to concept_id if display name not found
        parts.push(metadata.concept_id)
      }
    }
    if (metadata.level) {
      parts.push(`Level ${metadata.level}`)
    }
    if (metadata.operation) parts.push(metadata.operation)
    return parts.join(' • ')
  }

  // Group instances by concept_id to show a summary for level master achievements
  const conceptSummary = useMemo(() => {
    if (!achievement || !instances.length) return null
    
    // Check if this is a level master achievement
    const isLevelMaster = achievement.id?.startsWith('math-master-') || 
                         (achievement as any).code?.startsWith('math-master-')
    
    if (!isLevelMaster) return null
    
    // Group instances by concept_id
    const conceptMap = new Map<string, number>()
    instances.forEach(instance => {
      if (instance.metadata?.concept_id) {
        const conceptId = instance.metadata.concept_id
        conceptMap.set(conceptId, (conceptMap.get(conceptId) || 0) + 1)
      }
    })
    
    if (conceptMap.size === 0) return null
    
    // Convert to array of { conceptId, displayName, count }
    const concepts = Array.from(conceptMap.entries()).map(([conceptId, count]) => ({
      conceptId,
      displayName: getConceptDisplayNameByConceptId(conceptId) || conceptId,
      count,
    }))
    
    return concepts
  }, [instances, achievement])

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
                {/* Start Practice Button (if conceptId is provided) */}
                {conceptId && conceptDisplayName && (
                  <div className="mb-6 rounded-lg border-2 border-blue-200 bg-blue-50 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-gray-700 mb-1">Practice Session</p>
                        <p className="text-sm text-gray-600">
                          Start practicing: <span className="font-medium">{conceptDisplayName}</span>
                        </p>
                      </div>
                      <button
                        onClick={handleStartPractice}
                        disabled={isConceptLocked}
                        className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors ${
                          isConceptLocked
                            ? 'cursor-not-allowed bg-gray-400'
                            : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                        }`}
                        title={isConceptLocked ? 'This concept is locked. Complete requirements to unlock it.' : `Start practicing ${conceptDisplayName}`}
                      >
                        <Play className="h-4 w-4" />
                        Start Practice
                      </button>
                    </div>
                    {isConceptLocked && (
                      <p className="mt-2 text-xs text-gray-500">
                        This concept is locked. Complete the requirements to unlock it.
                      </p>
                    )}
                  </div>
                )}
                
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
                    {conceptSummary && conceptSummary.length > 0 && (
                      <div className="mb-6 rounded-lg bg-green-50 p-4 border border-green-200" data-testid="testid-achievement-modal-concept-summary">
                        <p className="text-sm font-semibold text-gray-700 mb-2">Math Concepts:</p>
                        <div className="space-y-1">
                          {conceptSummary.map((concept, idx) => (
                            <div key={idx} className="text-sm text-gray-700">
                              <span className="font-medium">{concept.displayName}</span>
                              {concept.count > 1 && (
                                <span className="text-gray-500 ml-2">({concept.count}x)</span>
                              )}
                            </div>
                          ))}
                        </div>
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



