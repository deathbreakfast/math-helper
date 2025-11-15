import { AnimatePresence, motion } from 'framer-motion'
import type { PracticeQuestion } from '../types'
import { RefObject } from 'react'

type PracticeDeckProps = {
  practiceSectionRef: RefObject<HTMLDivElement>
  question: PracticeQuestion
  userAnswer: string
  onAnswerChange: (value: string) => void
  onSubmit: () => void
  feedback: 'correct' | 'incorrect' | null
  showAnswer: boolean
  inputRef: RefObject<HTMLInputElement>
}

const PracticeDeck = ({
  practiceSectionRef,
  question,
  userAnswer,
  onAnswerChange,
  onSubmit,
  feedback,
  showAnswer,
  inputRef,
}: PracticeDeckProps) => {
  return (
    <div
      ref={practiceSectionRef}
      className="mt-8 rounded-3xl border border-slate-100 bg-gradient-to-r from-white to-slate-50 p-8 text-center shadow-inner"
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={question.id}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -16 }}
          transition={{ duration: 0.2 }}
        >
          <div className="text-center text-slate-900">
            <div className="text-7xl font-bold leading-tight">{question.operand1}</div>
            <div className="text-5xl font-bold text-slate-500">{question.operation === 'addition'
              ? '+'
              : question.operation === 'subtraction'
                ? '−'
                : question.operation === 'multiplication'
                  ? '×'
                  : '÷'}</div>
            <div className="text-7xl font-bold leading-tight">{question.operand2}</div>
          </div>
          <form
            onSubmit={(event) => {
              event.preventDefault()
              onSubmit()
            }}
            className="mt-8 flex flex-col items-center gap-4"
          >
            <div className="h-1 w-40 rounded-full bg-slate-200" />
            <input
              ref={inputRef}
              type="text"
              inputMode="numeric"
              value={userAnswer}
              onChange={(event) => onAnswerChange(event.target.value)}
              placeholder="?"
              className={`w-full max-w-sm rounded-2xl border-4 px-6 py-4 text-center text-4xl font-bold outline-none transition ${
                feedback === 'correct'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : feedback === 'incorrect'
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-blue-200 bg-white text-slate-900 focus:border-blue-500'
              }`}
            />
            {showAnswer && feedback === 'incorrect' && (
              <div className="text-sm font-semibold text-slate-600">
                Correct answer:{' '}
                <span className="text-base text-green-600">{question.correctAnswer}</span>
              </div>
            )}
            <button
              type="submit"
              disabled={!userAnswer.trim()}
              className="rounded-2xl bg-gradient-to-r from-blue-500 to-purple-600 px-10 py-3 text-lg font-semibold text-white shadow-lg transition hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-40"
            >
              Check Answer
            </button>
            <p className="text-sm text-slate-400">Press Enter to submit</p>
          </form>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default PracticeDeck

