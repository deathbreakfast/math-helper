import { motion } from 'framer-motion'
import { getEncouragementMessage } from '../../utils/summaryUtils'
import type { LevelUpResult } from '../../types'

type EncouragementBannerProps = {
  accuracy: number
  totalProblems: number
  totalTime: number
  levelUp: LevelUpResult | null
}

export const EncouragementBanner = ({ accuracy, totalProblems, totalTime, levelUp }: EncouragementBannerProps) => {
  const hasLeveledUp = levelUp?.leveled_up === true

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
      className="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 rounded-3xl shadow-2xl p-8 mb-8 text-center text-white"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
        className="text-6xl mb-4"
      >
        {hasLeveledUp ? '🎉' : accuracy === 100 ? '🏆' : accuracy >= 80 ? '⭐' : '💪'}
      </motion.div>
      {hasLeveledUp ? (
        <>
          <h2 className="text-3xl sm:text-4xl font-bold mb-2">
            🎉 Congratulations! You've Leveled Up! 🎉
          </h2>
          <p className="text-white/90 text-lg mb-2">
            You've reached Level {levelUp.new_level}! Outstanding work!
          </p>
          <p className="text-white/80 text-base">
            You completed {totalProblems} problems in {Math.round(totalTime)} seconds
          </p>
        </>
      ) : (
        <>
          <h2 className="text-3xl sm:text-4xl font-bold mb-2">{getEncouragementMessage(accuracy)}</h2>
          <p className="text-white/90 text-lg">
            You completed {totalProblems} problems in {Math.round(totalTime)} seconds
          </p>
        </>
      )}
    </motion.div>
  )
}

