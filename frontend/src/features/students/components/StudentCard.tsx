import { motion } from 'framer-motion'
import { Star } from 'lucide-react'
import type { User } from '../hooks/useStudents'

type StudentCardProps = {
  user: User
  isSelected: boolean
  index: number
  onClick: () => void
}

const StudentCard = ({ user, isSelected, index, onClick }: StudentCardProps) => {
  return (
    <motion.button
      key={user.id}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: index * 0.08 }}
      onClick={onClick}
      className={`relative rounded-2xl p-6 text-left transition-all ${
        isSelected
          ? 'bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-2xl ring-2 ring-blue-100'
          : 'bg-white text-slate-800 shadow-card hover:-translate-y-1 hover:shadow-xl'
      }`}
    >
      <div className="mb-3 text-5xl">{user.avatar}</div>
      <div className="text-lg font-semibold">{user.name}</div>
      <div className={isSelected ? 'text-white/80' : 'text-slate-500'}>Level {user.level}</div>
      {isSelected && (
        <motion.div
          layoutId="selected-indicator"
          className="absolute -top-2 -right-2 flex h-9 w-9 items-center justify-center rounded-full bg-yellow-400 shadow-lg"
        >
          <Star className="h-4 w-4 text-yellow-900" />
        </motion.div>
      )}
    </motion.button>
  )
}

export default StudentCard

