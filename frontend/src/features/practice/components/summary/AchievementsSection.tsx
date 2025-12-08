import { motion, AnimatePresence } from 'framer-motion'
import { Trophy, Award, Star } from 'lucide-react'
import type { AchievementBadge } from '../../hooks/useSummaryData'

type AchievementsSectionProps = {
  achievements: AchievementBadge[]
  showAchievements: boolean
}

export const AchievementsSection = ({ achievements, showAchievements }: AchievementsSectionProps) => {
  return (
    <motion.div
      data-testid="testid-achievements-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
        <Trophy className="w-5 h-5 text-yellow-600" />
        Achievements Earned
      </h3>
      <div className="space-y-3">
        <AnimatePresence>
          {showAchievements && achievements.length > 0 ? (
            achievements.map((achievement, index) => (
              <motion.div
                key={achievement.id}
                data-testid={`testid-newly-earned-achievement-${achievement.id}`}
                initial={{ opacity: 0, x: 20, scale: 0.8 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                transition={{ delay: index * 0.2, type: 'spring' }}
                className="flex items-start gap-3 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border-2 border-yellow-200"
              >
                <div className="text-3xl">{achievement.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-gray-900">{achievement.title}</div>
                  <div className="text-sm text-gray-600 mt-1">{achievement.description}</div>
                  {achievement.metadata && (
                    <div className="text-xs text-gray-500 mt-1">
                      {achievement.metadata.level && `Level ${achievement.metadata.level}`}
                      {achievement.metadata.operation && ` • ${achievement.metadata.operation}`}
                    </div>
                  )}
                </div>
                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500 flex-shrink-0" />
              </motion.div>
            ))
          ) : (
            <div data-testid="testid-no-achievements-empty-state" className="text-center py-8 text-gray-500">
              <Award className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">Complete challenges to earn achievements!</p>
            </div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

