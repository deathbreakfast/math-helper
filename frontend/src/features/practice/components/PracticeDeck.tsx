import { AnimatePresence, motion } from 'framer-motion'
import type { PracticeQuestion } from '../types'
import { RefObject } from 'react'
import { GradientSurface, PillButton } from '../../../components/ui'
import { renderProblemLayout } from '../layouts/ProblemLayouts'

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
  const layoutType = question.layout?.type ?? 'vertical'

  return (
    <GradientSurface
      ref={practiceSectionRef}
      variant="soft"
      tone="neutral"
      className="mt-8 p-8 text-center"
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={question.id}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -16 }}
          transition={{ duration: 0.2 }}
        >
          {renderProblemLayout(layoutType, {
            question,
            answerFormat: question.answerFormat,
            showWork: question.layout?.showWork,
            workSteps: question.layout?.workSteps,
          })}
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
            <PillButton type="submit" tone="indigo" disabled={!userAnswer.trim()} className="px-10 py-4 text-lg">
              Check Answer
            </PillButton>
            <p className="text-sm text-slate-400">Press Enter to submit</p>
          </form>
        </motion.div>
      </AnimatePresence>
    </GradientSurface>
  )
}

export default PracticeDeck

