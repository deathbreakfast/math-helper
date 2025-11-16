import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle, XCircle } from 'lucide-react'
import type { DivisionStep } from '../utils/longDivision'

type LongDivisionWorkStepsProps = {
  steps: DivisionStep[]
  showAnswer: boolean
  onStepChange: (id: string, value: string) => void
  inputRefs: Record<string, HTMLInputElement | null>
}

export const LongDivisionWorkSteps = ({ steps, showAnswer, onStepChange, inputRefs }: LongDivisionWorkStepsProps) => {
  return (
    <div>
      <h3 className="mb-4 text-center text-xl font-semibold text-slate-800">Show Your Work</h3>
      <div className="space-y-4">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.04 * index }}
            className="flex items-center justify-between gap-4"
          >
            <div className="flex items-center gap-3 min-w-[150px]">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-orange-50 text-orange-600">
                {step.stepType === 'divide'
                  ? '÷'
                  : step.stepType === 'multiply'
                    ? '×'
                    : step.stepType === 'subtract'
                      ? '−'
                      : '↓'}
              </div>
              <span className="text-base font-semibold text-slate-700 capitalize">
                {step.stepType === 'bringDown' ? 'Bring Down' : step.stepType}
              </span>
            </div>
            <div className="relative flex-1 max-w-xs">
              <input
                ref={(el) => {
                  inputRefs[step.id] = el
                }}
                type="text"
                inputMode="numeric"
                value={step.value}
                onChange={(event) => onStepChange(step.id, event.target.value)}
                disabled={showAnswer}
                className={`w-full rounded-2xl border-2 px-4 py-2 text-right text-2xl font-bold font-mono outline-none transition ${
                  step.isCorrect === true
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : step.isCorrect === false
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-orange-200 bg-slate-50 text-slate-900 focus:border-orange-400 focus:bg-white'
                }`}
                placeholder="?"
              />
              <AnimatePresence>
                {step.isCorrect === true && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-2 -top-2"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 shadow-lg">
                      <CheckCircle className="h-5 w-5 text-white" />
                    </div>
                  </motion.div>
                )}
                {step.isCorrect === false && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-2 -top-2"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500 shadow-lg">
                      <XCircle className="h-5 w-5 text-white" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              {step.isCorrect === false && showAnswer && step.expectedValue !== null && (
                <motion.span
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute -bottom-5 right-0 text-xs font-semibold text-emerald-600"
                >
                  {step.expectedValue}
                </motion.span>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

