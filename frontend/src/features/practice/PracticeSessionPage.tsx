import { useEffect, useRef } from 'react'

/* eslint-disable react-hooks/set-state-in-effect */
import { useLearners } from '../../lib/learners/hooks'
import PracticeDeck from './components/PracticeDeck'
import PracticeHeader from './components/PracticeHeader'
import LongDivisionWorksheet from './components/LongDivisionWorksheet'
import PartialProductsWorksheet from './components/PartialProductsWorksheet'
import { PracticeModeToggle } from './components/PracticeModeToggle'
import { PracticeFooterControls } from './components/PracticeFooterControls'
import { usePracticeRouting } from './hooks/usePracticeRouting'
import { usePracticeSession } from './hooks/usePracticeSession'

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
    handleSetAnswer,
    handleMove,
    toggleFlag,
    canSubmit,
    handleSubmit,
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
                    onComplete={(isCorrect) => {
                      // For partial products, use the final answer or correct answer
                      handleSetAnswer(currentQuestion.id, currentQuestion.correctAnswer, isCorrect)
                    }}
                  />
                ) : isLongDivision ? (
                  <LongDivisionWorksheet
                    question={currentQuestion}
                    notice={currentQuestion.layout?.notice}
                    tip={currentQuestion.layout?.tip}
                    answerFormats={currentQuestion.layout?.answerFormats}
                    onComplete={(isCorrect) => {
                      // For long division, use the correct answer from question
                      handleSetAnswer(currentQuestion.id, currentQuestion.correctAnswer, isCorrect)
                    }}
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
                  canSubmit={canSubmit}
                  onMove={handleMove}
                  onToggleFlag={toggleFlag}
                  onSubmit={handleSubmit}
                />
              </>
            )
          })()}
      </div>
    </div>
  )
}

export default PracticeSessionPage


