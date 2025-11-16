import { useEffect, useRef } from 'react'

/* eslint-disable react-hooks/set-state-in-effect */
import { ChevronLeft, ChevronRight, Flag } from 'lucide-react'
import { PillButton } from '../../components/ui'
import { useLearners } from '../../lib/learners/hooks'
import PracticeDeck from './components/PracticeDeck'
import PracticeHeader from './components/PracticeHeader'
import LongDivisionWorksheet from './components/LongDivisionWorksheet'
import PartialProductsWorksheet from './components/PartialProductsWorksheet'
import { usePracticeRouting } from './hooks/usePracticeRouting'
import { usePracticeSession } from './hooks/usePracticeSession'

const PracticeModeToggle = ({
  practiceMode,
  onChange,
}: {
  practiceMode: 'standard' | 'multiplication' | 'division'
  onChange: (mode: 'standard' | 'multiplication' | 'division') => void
}) => (
  <div className="mb-8 flex flex-wrap items-center justify-center gap-3">
    <PillButton
      variant={practiceMode === 'standard' ? 'solid' : 'surface'}
      tone="indigo"
      onClick={() => onChange('standard')}
    >
      Standard Practice
    </PillButton>
    <PillButton
      variant={practiceMode === 'multiplication' ? 'solid' : 'surface'}
      tone="rose"
      onClick={() => onChange('multiplication')}
    >
      Multiplication Demo
    </PillButton>
    <PillButton
      variant={practiceMode === 'division' ? 'solid' : 'surface'}
      tone="amber"
      onClick={() => onChange('division')}
    >
      Division Demo
    </PillButton>
  </div>
)

const PracticeFooterControls = ({
  currentQuestionIndex,
  problemsLength,
  isFlagged,
  onMove,
  onToggleFlag,
}: {
  currentQuestionIndex: number
  problemsLength: number
  isFlagged: boolean
  onMove: (direction: 'next' | 'prev') => void
  onToggleFlag: () => void
}) => (
  <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
    <PillButton
      variant="surface"
      onClick={() => onMove('prev')}
      disabled={currentQuestionIndex === 0}
      leftIcon={<ChevronLeft className="h-4 w-4" />}
    >
      Previous
    </PillButton>
    <PillButton
      variant={isFlagged ? 'solid' : 'surface'}
      tone="amber"
      onClick={onToggleFlag}
      leftIcon={<Flag className="h-4 w-4" />}
    >
      {isFlagged ? 'Flagged' : 'Flag for Review'}
    </PillButton>
    <PillButton
      tone="emerald"
      onClick={() => onMove('next')}
      disabled={currentQuestionIndex >= problemsLength - 1}
      rightIcon={<ChevronRight className="h-4 w-4" />}
    >
      {currentQuestionIndex >= problemsLength - 1 ? 'Complete' : 'Next'}
    </PillButton>
  </div>
)

const PracticeSessionPage = () => {
  const { learners, isLoading: isLoadingLearners, error: learnersError } = useLearners()
  const practiceSectionRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)

  const { selectedUser, practiceMode, setPracticeMode } = usePracticeRouting(learners)

  const {
    problems,
    currentQuestionIndex,
    currentQuestion,
    userAnswer,
    feedback,
    showAnswer,
    flaggedQuestions,
    isPartialProducts,
    isLongDivision,
    progressPercent,
    cardCounterDisplay,
    handleAnswerChange,
    handleCheckAnswer,
    handleMove,
    toggleFlag,
  } = usePracticeSession({
    selectedUser,
    practiceMode,
  })

  const loadError = learnersError
  const isLoadingUsers = isLoadingLearners

  useEffect(() => {
    inputRef.current?.focus()
  }, [currentQuestionIndex])

  useEffect(() => {
    if (!selectedUser || !practiceSectionRef.current) return
    practiceSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [selectedUser])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <PracticeHeader
          selectedUser={selectedUser}
          cardCounterDisplay={cardCounterDisplay}
          currentQuestion={currentQuestion}
          progressPercent={progressPercent}
        />

        <PracticeModeToggle practiceMode={practiceMode} onChange={setPracticeMode} />

        {loadError && (
          <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{loadError}</div>
        )}

        {!loadError && !isLoadingUsers && !selectedUser && (
          <div className="mb-8 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
            No learner selected. Use a dashboard share link to launch practice for a specific student.
          </div>
        )}

        {selectedUser &&
          currentQuestion &&
          problems.length > 0 &&
          (() => {
            const isFlagged = Boolean(flaggedQuestions[currentQuestion.id])
            return (
              <>
                {isPartialProducts ? (
                  <PartialProductsWorksheet
                    question={currentQuestion}
                    mode={currentQuestion.layout?.partialProductsMode ?? 'easy'}
                  />
                ) : isLongDivision ? (
                  <LongDivisionWorksheet
                    question={currentQuestion}
                    notice={currentQuestion.layout?.notice}
                    tip={currentQuestion.layout?.tip}
                    answerFormats={currentQuestion.layout?.answerFormats}
                  />
                ) : (
                  <PracticeDeck
                    practiceSectionRef={practiceSectionRef}
                    question={currentQuestion}
                    userAnswer={userAnswer}
                    onAnswerChange={handleAnswerChange}
                    onSubmit={handleCheckAnswer}
                    feedback={feedback}
                    showAnswer={showAnswer}
                    inputRef={inputRef}
                  />
                )}

                <PracticeFooterControls
                  currentQuestionIndex={currentQuestionIndex}
                  problemsLength={problems.length}
                  isFlagged={isFlagged}
                  onMove={handleMove}
                  onToggleFlag={toggleFlag}
                />
              </>
            )
          })()}
      </div>
    </div>
  )
}

export default PracticeSessionPage


