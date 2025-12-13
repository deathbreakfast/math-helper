import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useRef, type RefObject } from 'react'
import type { PracticeQuestion } from '../types'
import { GradientSurface, PillButton } from '../../../components/ui'
import { renderProblemLayout } from '../layouts/ProblemLayouts'

type PracticeDeckProps = {
  practiceSectionRef: RefObject<HTMLDivElement | null>
  question: PracticeQuestion
  userAnswer: string
  onAnswerChange: (value: string) => void
  onSubmit: () => void
  feedback: 'correct' | 'incorrect' | null
  showAnswer: boolean
  inputRef: RefObject<HTMLInputElement | null>
  onMoveNext?: () => void
  canMoveNext?: boolean
  canSubmit?: boolean
  onSessionSubmit?: () => void
  isLastQuestion?: boolean
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
  onMoveNext,
  canMoveNext = false,
  canSubmit = false,
  onSessionSubmit,
  isLastQuestion = false,
}: PracticeDeckProps) => {
  const layoutType = question.layout?.type ?? 'vertical'
  const formRef = useRef<HTMLFormElement>(null)

  // Auto-focus input when question changes (only if answer is not shown)
  useEffect(() => {
    // Only focus if answer is not shown
    if (!showAnswer) {
      // Small delay to ensure the input is rendered and enabled
      const timer = setTimeout(() => {
        if (inputRef.current && !inputRef.current.disabled) {
          inputRef.current.focus()
        }
      }, 300)
      return () => clearTimeout(timer)
    }
  }, [question.id, showAnswer, inputRef])

  // Handle keyboard events for Enter key when answer is checked
  useEffect(() => {
    if (!showAnswer) return

    const handleKeyDown = (event: KeyboardEvent) => {
      // Handle Enter key when answer is checked
      // Only trigger if the active element is within the form or the form area
      if (event.key === 'Enter') {
        const activeElement = document.activeElement
        const form = formRef.current
        
        // Check if active element is within the form, or if form is in view
        if (form && (form.contains(activeElement) || activeElement === document.body)) {
          // Prevent default only if we're in the practice context
          event.preventDefault()
          event.stopPropagation()
          
          // If can submit and this is last question, submit session
          if (canSubmit && isLastQuestion && onSessionSubmit) {
            onSessionSubmit()
          } else if (onMoveNext && canMoveNext) {
            // Otherwise, move to next question
            onMoveNext()
          }
        }
      }
    }

    // Use document listener to catch Enter even when input is disabled
    document.addEventListener('keydown', handleKeyDown, true)
    return () => {
      document.removeEventListener('keydown', handleKeyDown, true)
    }
  }, [showAnswer, onMoveNext, canMoveNext, canSubmit, isLastQuestion, onSessionSubmit])

  const handleFormSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (showAnswer && onMoveNext && canMoveNext) {
      // If answer is already checked, go to next question
      onMoveNext()
    } else if (!showAnswer) {
      // If answer not checked yet, check it
      onSubmit()
    }
  }

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
          <div data-testid="testid-question-display">
            {renderProblemLayout(layoutType, {
              question,
              answerFormat: question.answerFormat,
              showWork: question.layout?.showWork,
              workSteps: question.layout?.workSteps,
            })}
          </div>
          <form
            ref={formRef}
            onSubmit={handleFormSubmit}
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
              disabled={showAnswer}
              data-testid="testid-answer-input"
              className={`w-full max-w-sm rounded-2xl border-4 px-6 py-4 text-center text-4xl font-bold outline-none transition ${
                feedback === 'correct'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : feedback === 'incorrect'
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-blue-200 bg-white text-slate-900 focus:border-blue-500'
              } ${showAnswer ? 'cursor-not-allowed opacity-75' : ''}`}
            />
            {showAnswer && feedback === 'incorrect' && (
              <div className="text-sm font-semibold text-slate-600">
                Correct answer:{' '}
                <span className="text-base text-green-600">{question.correctAnswer}</span>
              </div>
            )}
            <PillButton 
              type="submit" 
              tone="indigo" 
              disabled={!userAnswer.trim() || (showAnswer && !canMoveNext)} 
              className="px-10 py-4 text-lg"
              data-testid="testid-check-answer-button"
            >
              {showAnswer ? 'Answer Locked' : 'Check Answer'}
            </PillButton>
            <p className="text-sm text-slate-400">
              {showAnswer 
                ? (canSubmit && isLastQuestion ? 'Press Enter to submit session' : 'Press Enter to go to next question')
                : 'Press Enter to submit'}
            </p>
          </form>
        </motion.div>
      </AnimatePresence>
    </GradientSurface>
  )
}

export default PracticeDeck

