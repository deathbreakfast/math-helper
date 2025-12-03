import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

/* eslint-disable react-hooks/set-state-in-effect */
import { useLearners } from '../../lib/learners/hooks'
import PracticeDeck from './components/PracticeDeck'
import PracticeHeader from './components/PracticeHeader'
import LongDivisionWorksheet from './components/LongDivisionWorksheet'
import PartialProductsWorksheet from './components/PartialProductsWorksheet'
import { MathTypeDisplay } from './components/MathTypeDisplay'
import { PracticeFooterControls } from './components/PracticeFooterControls'
import { usePracticeRouting } from './hooks/usePracticeRouting'
import { usePracticeSession } from './hooks/usePracticeSession'

const PracticeSessionPage = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { learners, isLoading: isLoadingLearners, error: learnersError } = useLearners()
  const practiceSectionRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLInputElement | null>(null)
  const nextButtonRef = useRef<HTMLButtonElement | null>(null)

  const { selectedUser, practiceMode } = usePracticeRouting(learners)
  
  // Detect test mode from URL params
  const testType = searchParams.get('testType')
  const isTestParam = searchParams.get('isTest')
  const isTest = isTestParam === 'true' && testType !== null

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
    sessionMode,
    sessionError,
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
    navigate,
  })

  const loadError = learnersError
  const isLoadingUsers = isLoadingLearners

  // Focus input when question changes (prioritize this over Next button focus)
  useEffect(() => {
    // When question changes, blur any focused buttons immediately
    if (nextButtonRef.current && nextButtonRef.current === document.activeElement) {
      nextButtonRef.current.blur()
    }
    
    // Only focus if we have a current question and answer is not shown
    if (!currentQuestion || showAnswer) return
    
    // Try to focus with increasing delays to handle async state updates
    const timers: ReturnType<typeof setTimeout>[] = []
    
    for (let i = 0; i < 3; i++) {
      const timer = setTimeout(() => {
        if (inputRef.current && !inputRef.current.disabled) {
          inputRef.current.focus()
        }
      }, 200 + i * 100) // 200ms, 300ms, 400ms
      timers.push(timer)
    }
    
    return () => {
      timers.forEach(timer => clearTimeout(timer))
    }
  }, [currentQuestionIndex, currentQuestion?.id, showAnswer])

  useEffect(() => {
    if (!selectedUser || !practiceSectionRef.current) return
    practiceSectionRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [selectedUser])

  // Focus Next button when answer is checked (but only if we're not changing questions)
  useEffect(() => {
    // Only focus Next button if showAnswer becomes true
    // Use a longer delay to ensure question change focus doesn't interfere
    if (showAnswer && nextButtonRef.current && !canSubmit && currentQuestion) {
      const timer = setTimeout(() => {
        // Double-check that showAnswer is still true, input is disabled, and we haven't changed questions
        if (showAnswer && inputRef.current?.disabled && nextButtonRef.current) {
          nextButtonRef.current.focus()
        }
      }, 250)
      return () => clearTimeout(timer)
    }
  }, [showAnswer, canSubmit, currentQuestion])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <PracticeHeader
          selectedUser={selectedUser}
          cardCounterDisplay={cardCounterDisplay}
          currentQuestion={currentQuestion}
          progressPercent={progressPercent}
          isTest={isTest}
        />

        {currentQuestion && (
          <MathTypeDisplay mode={sessionMode} operation={currentQuestion.operation} />
        )}

        {loadError && (
          <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{loadError}</div>
        )}

        {sessionError && (
          <div className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
            <strong>Unable to start session:</strong> {sessionError}
          </div>
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
                    onMoveNext={() => handleMove('next')}
                    canMoveNext={currentQuestionIndex < problems.length - 1}
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
                  showAnswer={showAnswer}
                  nextButtonRef={nextButtonRef}
                />
              </>
            )
          })()}
      </div>
    </div>
  )
}

export default PracticeSessionPage


