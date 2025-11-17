import { PillButton } from '../../../components/ui'

type PracticeModeToggleProps = {
  practiceMode: 'standard' | 'multiplication' | 'division'
  onChange: (mode: 'standard' | 'multiplication' | 'division') => void
}

export const PracticeModeToggle = ({ practiceMode, onChange }: PracticeModeToggleProps) => {
  return (
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
}

