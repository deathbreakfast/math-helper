import { motion } from 'framer-motion'
import type { PracticeQuestion } from '../../features/practice/types'

type VerticalProblemCardProps = {
  question: PracticeQuestion
  showSeparator?: boolean
  className?: string
}

const getOperationSymbol = (operation: PracticeQuestion['operation']) => {
  switch (operation) {
    case 'addition':
      return '+'
    case 'subtraction':
      return '−'
    case 'multiplication':
      return '×'
    case 'division':
      return '÷'
  }
}

export const VerticalProblemCard = ({
  question,
  showSeparator = true,
  className = '',
}: VerticalProblemCardProps) => {
  return (
    <div className={`text-center ${className}`}>
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-2"
      >
        <div className="text-7xl font-bold leading-tight">{question.operand1}</div>
        <div className="text-5xl font-bold text-slate-500">{getOperationSymbol(question.operation)}</div>
        <div className="text-7xl font-bold leading-tight">{question.operand2}</div>
        {showSeparator && <div className="h-1 w-40 mx-auto rounded-full bg-slate-200 mt-4" />}
      </motion.div>
    </div>
  )
}

