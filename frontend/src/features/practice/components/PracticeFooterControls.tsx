import { ChevronLeft, ChevronRight, Flag } from 'lucide-react'
import { PillButton } from '../../../components/ui'

type PracticeFooterControlsProps = {
  currentQuestionIndex: number
  problemsLength: number
  isFlagged: boolean
  canSubmit: boolean
  onMove: (direction: 'next' | 'prev') => void
  onToggleFlag: () => void
  onSubmit: () => void
}

export const PracticeFooterControls = ({
  currentQuestionIndex,
  problemsLength,
  isFlagged,
  canSubmit,
  onMove,
  onToggleFlag,
  onSubmit,
}: PracticeFooterControlsProps) => {
  return (
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
      {canSubmit ? (
        <PillButton tone="emerald" onClick={onSubmit} className="px-8">
          Submit Session
        </PillButton>
      ) : (
        <PillButton
          tone="emerald"
          onClick={() => onMove('next')}
          disabled={currentQuestionIndex >= problemsLength - 1}
          rightIcon={<ChevronRight className="h-4 w-4" />}
        >
          {currentQuestionIndex >= problemsLength - 1 ? 'Complete' : 'Next'}
        </PillButton>
      )}
    </div>
  )
}

