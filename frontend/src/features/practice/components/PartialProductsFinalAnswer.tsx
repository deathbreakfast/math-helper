import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle, Lightbulb, XCircle } from 'lucide-react'
import type { VerificationResults } from '../hooks/usePartialProducts'

type PartialProductsFinalAnswerProps = {
  finalAnswer: string
  showAnswer: boolean
  verificationResults: VerificationResults | null
  correctAnswer: string
  hint?: string
  onFinalAnswerChange: (value: string) => void
  inputRef: HTMLInputElement | null
}

const DEFAULT_TIP = 'Multiply by each digit separately, line up the place values, then add the partial products together.'

export const PartialProductsFinalAnswer = ({
  finalAnswer,
  showAnswer,
  verificationResults,
  correctAnswer,
  hint,
  onFinalAnswerChange,
  inputRef,
}: PartialProductsFinalAnswerProps) => {
  return (
    <div className="mt-6">
      <h3 className="text-xl font-semibold text-slate-800 mb-4 text-center">Final Answer</h3>
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <input
            ref={(el) => {
              if (inputRef !== el) {
                // Store ref in parent's ref object
              }
            }}
            type="text"
            inputMode="numeric"
            value={finalAnswer}
            onChange={(event) => onFinalAnswerChange(event.target.value.replace(/[^0-9]/g, ''))}
            disabled={showAnswer}
            className={`font-mono text-3xl sm:text-4xl font-bold text-center w-56 px-6 py-3 border-4 rounded-xl outline-none transition ${
              verificationResults?.finalAnswer === true
                ? 'border-green-500 bg-green-50 text-green-700'
                : verificationResults?.finalAnswer === false
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-purple-400 bg-purple-50 text-slate-900 focus:border-purple-600 focus:bg-white'
            }`}
            placeholder="?"
          />
          <AnimatePresence>
            {verificationResults?.finalAnswer === true && (
              <motion.div
                initial={{ scale: 0, rotate: -120 }}
                animate={{ scale: 1, rotate: 0 }}
                exit={{ scale: 0 }}
                className="absolute -right-3 -top-3"
              >
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
              </motion.div>
            )}
            {verificationResults?.finalAnswer === false && (
              <motion.div
                initial={{ scale: 0, rotate: -120 }}
                animate={{ scale: 1, rotate: 0 }}
                exit={{ scale: 0 }}
                className="absolute -right-3 -top-3"
              >
                <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center shadow-lg">
                  <XCircle className="w-6 h-6 text-white" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          {verificationResults?.finalAnswer === false && showAnswer && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-sm font-semibold text-emerald-600"
            >
              Correct answer: {correctAnswer}
            </motion.div>
          )}
        </div>

        <div className="w-full max-w-md rounded-2xl border border-purple-200 bg-gradient-to-r from-purple-50 to-pink-50 p-4 text-sm text-purple-800">
          <p className="font-semibold mb-1 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-purple-500" />
            Tip
          </p>
          <p className="leading-relaxed">{hint || DEFAULT_TIP}</p>
        </div>
      </div>
    </div>
  )
}

