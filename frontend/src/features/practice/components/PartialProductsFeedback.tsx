import { AnimatePresence, motion } from 'framer-motion'
import type { VerificationResults } from '../hooks/usePartialProducts'

type PartialProductsFeedbackProps = {
  feedback: 'correct' | 'incorrect' | 'partial' | null
  verificationResults: VerificationResults | null
}

export const PartialProductsFeedback = ({ feedback, verificationResults }: PartialProductsFeedbackProps) => {
  if (!verificationResults) return null

  return (
    <AnimatePresence>
      {verificationResults && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className={`mt-8 p-6 rounded-2xl text-center ${
            feedback === 'correct'
              ? 'bg-green-50 border-2 border-green-500 text-green-700'
              : feedback === 'partial'
                ? 'bg-yellow-50 border-2 border-yellow-500 text-yellow-700'
                : 'bg-red-50 border-2 border-red-500 text-red-700'
          }`}
        >
          <p className="text-lg font-semibold">{verificationResults.message}</p>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

