import { motion } from 'framer-motion'
import { Home } from 'lucide-react'

type SummaryHeaderProps = {
  studentName: string
  level: number
  onBackToDashboard: () => void
}

export const SummaryHeader = ({ studentName, level, onBackToDashboard }: SummaryHeaderProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between mb-8"
    >
      <div>
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2">Practice Summary</h1>
        <p className="text-gray-600">
          {studentName} • Level {level}
        </p>
      </div>
      <button
        onClick={onBackToDashboard}
        className="flex items-center gap-2 px-6 py-3 bg-white text-gray-700 rounded-xl hover:bg-gray-50 transition-colors shadow-md hover:shadow-lg"
      >
        <Home className="w-5 h-5" />
        <span className="hidden sm:inline">Dashboard</span>
      </button>
    </motion.div>
  )
}

