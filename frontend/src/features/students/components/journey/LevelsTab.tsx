import { motion } from 'framer-motion'
import { Lock, Crown } from 'lucide-react'
import { LevelRequirementCard } from '../LevelRequirementCard'
import type { UserProgressData } from '../../utils/progressMapping'

type LevelsTabProps = {
  userData: UserProgressData
}

export const LevelsTab = ({ userData }: LevelsTabProps) => {
  return (
    <motion.div
      key="levels"
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      exit={{
        opacity: 0,
        y: -20,
      }}
      className="space-y-6"
    >
      <div className="mb-8 rounded-2xl border-2 border-blue-300 bg-gradient-to-r from-blue-100 to-purple-100 p-6">
        <div className="mb-3 flex items-center gap-3">
          <Crown className="h-8 w-8 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-900">Level Progression Path</h2>
        </div>
        <p className="text-gray-700">Complete achievements to unlock higher levels. Each level brings new challenges and rewards!</p>
      </div>

      {userData.levelRequirements.filter((req) => !req.isLocked || req.level <= userData.level + 1).map((requirement, index) => (
        <LevelRequirementCard key={requirement.id} requirement={requirement} index={index} />
      ))}

      {/* Locked Future Levels Preview */}
      <div className="rounded-2xl border-2 border-gray-300 bg-gray-100 p-8 text-center">
        <Lock className="mx-auto mb-4 h-16 w-16 text-gray-400" />
        <h3 className="mb-2 text-xl font-bold text-gray-600">More Levels Await</h3>
        <p className="text-gray-500">Keep progressing to unlock requirements for Levels {userData.level + 2} and beyond!</p>
      </div>
    </motion.div>
  )
}

