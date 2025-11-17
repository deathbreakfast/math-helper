import { motion } from 'framer-motion'
import { ChevronRight } from 'lucide-react'
import { getTierColor } from '../../utils/achievementUtils'
import type { UserProgressData } from '../../utils/progressMapping'

type JourneyHeaderProps = {
  userData: UserProgressData
  onBack?: () => void
}

export const JourneyHeader = ({ userData, onBack }: JourneyHeaderProps) => {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: -20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="mb-8 flex items-center justify-between"
    >
      <div className="flex items-center gap-4">
        {onBack && (
          <button onClick={onBack} className="rounded-xl p-2 transition-colors hover:bg-white/50">
            <ChevronRight className="h-6 w-6 rotate-180 text-gray-700" />
          </button>
        )}
        <div>
          <h1 className="mb-2 flex items-center gap-3 text-4xl font-bold text-gray-900">
            <span className="text-5xl">{userData.avatar}</span>
            {userData.name}'s Journey
          </h1>
          <p className="text-gray-600">Track your achievements and level progression</p>
        </div>
      </div>
      <div className={`rounded-2xl bg-gradient-to-r px-6 py-3 text-white shadow-lg ${getTierColor('Gold')}`}>
        <div className="text-sm font-medium opacity-90">Current Level</div>
        <div className="text-3xl font-bold">{userData.level}</div>
      </div>
    </motion.div>
  )
}

