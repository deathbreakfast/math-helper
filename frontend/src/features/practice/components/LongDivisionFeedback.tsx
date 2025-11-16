import { AnimatePresence, motion } from 'framer-motion'
import type { VerificationResults } from '../hooks/useLongDivisionVerification'

type LongDivisionFeedbackProps = {
  feedback: 'correct' | 'incorrect' | 'partial' | null
  verificationResults: VerificationResults | null
  answerMode: 'remainder' | 'fraction' | 'decimal'
  answerDisplay: string
}

export const LongDivisionFeedback = ({
  feedback,
  verificationResults,
  answerMode,
  answerDisplay,
}: LongDivisionFeedbackProps) => {
  if (!verificationResults) return null

  return (
    <>
      {verificationResults && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Final Answer ({answerMode})</p>
          <p className="text-3xl font-bold text-orange-600">{answerDisplay}</p>
        </motion.div>
      )}

      <AnimatePresence>
        {verificationResults && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`rounded-2xl p-5 text-center ${
              feedback === 'correct'
                ? 'border-2 border-green-500 bg-green-50 text-green-700'
                : feedback === 'partial'
                  ? 'border-2 border-yellow-500 bg-yellow-50 text-yellow-700'
                  : 'border-2 border-red-500 bg-red-50 text-red-700'
            }`}
          >
            <p className="text-lg font-semibold">{verificationResults.message}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

