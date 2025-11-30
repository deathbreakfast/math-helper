import { ChevronLeft, ChevronRight, Flag } from 'lucide-react'
import { useRef, type RefObject } from 'react'
import { PillButton } from '../../../components/ui'

type PracticeFooterControlsProps = {
  currentQuestionIndex: number
  problemsLength: number
  isFlagged: boolean
  canSubmit: boolean
  onMove: (direction: 'next' | 'prev') => void
  onToggleFlag: () => void
  onSubmit: () => void
  showAnswer?: boolean
  nextButtonRef?: RefObject<HTMLButtonElement | null>
}

export const PracticeFooterControls = ({
  currentQuestionIndex,
  problemsLength,
  isFlagged,
  canSubmit,
  onMove,
  onToggleFlag,
  onSubmit,
  showAnswer,
  nextButtonRef,
}: PracticeFooterControlsProps) => {
  const internalNextButtonRef = useRef<HTMLButtonElement | null>(null)
  const actualNextButtonRef = nextButtonRef || internalNextButtonRef

  return (
    <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
      <PillButton
        variant="surface"
        onClick={() => onMove('prev')}
        disabled={currentQuestionIndex === 0}
        leftIcon={<ChevronLeft className="h-4 w-4" />}
        data-testid="testid-previous-button"
      >
        Previous
      </PillButton>
      <PillButton
        variant={isFlagged ? 'solid' : 'surface'}
        tone="amber"
        onClick={onToggleFlag}
        leftIcon={<Flag className="h-4 w-4" />}
        data-testid="testid-flag-button"
      >
        {isFlagged ? 'Flagged' : 'Flag for Review'}
      </PillButton>
      {canSubmit ? (
        <PillButton 
          tone="emerald" 
          onClick={onSubmit} 
          className="px-8"
          data-testid="testid-submit-session-button"
        >
          Submit Session
        </PillButton>
      ) : (
        <PillButton
          ref={actualNextButtonRef}
          tone="emerald"
          onClick={() => onMove('next')}
          disabled={currentQuestionIndex >= problemsLength - 1}
          rightIcon={<ChevronRight className="h-4 w-4" />}
          data-testid="testid-next-button"
        >
          {currentQuestionIndex >= problemsLength - 1 ? 'Complete' : 'Next'}
        </PillButton>
      )}
    </div>
  )
}

