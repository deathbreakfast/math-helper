import React from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, ChevronRight, Check } from 'lucide-react'
import type { LevelRequirement } from '../data/levelRequirements'

type LevelRequirementCardProps = {
  requirement: LevelRequirement
  index: number
  userId?: string
}

export const LevelRequirementCard: React.FC<LevelRequirementCardProps> = ({ requirement, index, userId }) => {
  const navigate = useNavigate()
  const params = useParams<{ userId?: string }>()
  const effectiveUserId = userId || params.userId
  
  const allCompleted = requirement.requirements.every((req) => req.completed)
  const completedCount = requirement.requirements.filter((req) => req.completed).length
  const totalCount = requirement.requirements.length
  
  const handleAchievementClick = (achievementCode: string) => {
    if (effectiveUserId) {
      navigate(`/journey/${effectiveUserId}/achievements?text=${encodeURIComponent(achievementCode)}`)
    }
  }

  return (
    <motion.div
      data-testid={`testid-level-requirement-${requirement.level}`}
      initial={{
        opacity: 0,
        x: -20,
      }}
      animate={{
        opacity: 1,
        x: 0,
      }}
      transition={{
        delay: index * 0.1,
      }}
      className={`rounded-2xl border-2 p-6 ${
        requirement.isLocked
          ? 'border-gray-300 bg-gray-100'
          : allCompleted
            ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-lg'
            : 'border-blue-300 bg-white shadow-lg'
      }`}
    >
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-xl text-xl font-bold ${
              requirement.isLocked
                ? 'bg-gray-200 text-gray-500'
                : allCompleted
                  ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
            }`}
          >
            {requirement.level}
          </div>
          <ChevronRight className="h-6 w-6 text-gray-400" />
          <div
            className={`flex h-12 w-12 items-center justify-center rounded-xl text-xl font-bold ${
              requirement.isLocked
                ? 'bg-gray-200 text-gray-500'
                : allCompleted
                  ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                  : 'bg-gradient-to-r from-purple-500 to-pink-600 text-white'
            }`}
          >
            {requirement.nextLevel}
          </div>
        </div>
        {requirement.isLocked && <Lock className="h-6 w-6 text-gray-400" data-testid="testid-level-lock-icon" />}
      </div>

      {/* Title */}
      <h3 className={`mb-4 text-xl font-bold ${requirement.isLocked ? 'text-gray-500' : 'text-gray-900'}`}>{requirement.title}</h3>

      {/* Requirements List */}
      <div className="space-y-3">
        {requirement.requirements.map((req, idx) => (
          <div key={idx} className="space-y-2" data-testid={`testid-requirement-${idx}`}>
            <div className="flex items-start gap-3">
              <div
                data-testid={req.completed ? 'testid-requirement-completed' : 'testid-requirement-incomplete'}
                className={`mt-1 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full ${
                  req.completed ? 'bg-green-500' : requirement.isLocked ? 'bg-gray-300' : 'bg-gray-200'
                }`}
              >
                {req.completed ? <Check className="h-3 w-3 text-white" /> : <div className={`h-2 w-2 rounded-full ${requirement.isLocked ? 'bg-gray-400' : 'bg-gray-400'}`} />}
              </div>
              <div className="flex-1">
                {req.achievementCode && effectiveUserId ? (
                  <button
                    onClick={() => handleAchievementClick(req.achievementCode!)}
                    className={`text-left text-sm font-medium transition-colors hover:text-blue-600 ${
                      requirement.isLocked ? 'text-gray-400 hover:text-gray-500' : req.completed ? 'text-gray-700 hover:text-blue-600' : 'text-gray-900 hover:text-blue-600'
                    }`}
                  >
                    {req.description}
                  </button>
                ) : (
                  <p className={`text-sm font-medium ${requirement.isLocked ? 'text-gray-400' : req.completed ? 'text-gray-700' : 'text-gray-900'}`}>
                    {req.description}
                  </p>
                )}
                {req.progress !== undefined && req.maxProgress !== undefined && (
                  <div className="mt-2">
                    <div className="mb-1 flex justify-between text-xs text-gray-600">
                      <span>Progress</span>
                      <span>
                        {req.progress}/{req.maxProgress}
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-gray-200">
                      <motion.div
                        initial={{
                          width: 0,
                        }}
                        animate={{
                          width: `${Math.min((req.progress / req.maxProgress) * 100, 100)}%`,
                        }}
                        transition={{
                          duration: 1,
                          ease: 'easeOut',
                        }}
                        className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Progress Summary */}
      <div className="mt-4 border-t border-gray-200 pt-4">
        <div className="flex items-center justify-between text-sm">
          <span className={`font-medium ${requirement.isLocked ? 'text-gray-400' : 'text-gray-700'}`}>Overall Progress</span>
          <span className={`font-bold ${allCompleted ? 'text-green-600' : requirement.isLocked ? 'text-gray-400' : 'text-blue-600'}`}>
            {completedCount}/{totalCount} Complete
          </span>
        </div>
      </div>
    </motion.div>
  )
}

