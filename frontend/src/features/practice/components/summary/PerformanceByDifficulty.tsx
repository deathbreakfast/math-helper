import { motion } from 'framer-motion'
import { TrendingUp } from 'lucide-react'

type PerformanceByDifficultyProps = {
  performanceByDifficulty: Record<number, { correct: number; total: number }>
}

export const PerformanceByDifficulty = ({ performanceByDifficulty }: PerformanceByDifficultyProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.7 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-purple-600" />
        Performance by Level
      </h3>
      <div className="space-y-4">
        {Object.entries(performanceByDifficulty)
          .sort(([a], [b]) => Number(a) - Number(b))
          .map(([difficulty, stats], index) => {
            const percentage = Math.round((stats.correct / stats.total) * 100)
            return (
              <div key={difficulty}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Difficulty {difficulty}</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {stats.correct}/{stats.total} ({percentage}%)
                  </span>
                </div>
                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ delay: 0.8 + index * 0.1, duration: 0.8 }}
                    className={`h-full ${
                      percentage >= 80 ? 'bg-green-500' : percentage >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                    } rounded-full`}
                  />
                </div>
              </div>
            )
          })}
      </div>
    </motion.div>
  )
}

