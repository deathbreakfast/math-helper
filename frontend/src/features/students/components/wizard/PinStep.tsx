import PinPad from '../PinPad'

type PinStepProps = {
  pin: string
  name: string
  avatar: string
  isSubmitting: boolean
  errorMessage?: string | null
  onChange: (pin: string) => void
  onComplete: (pin: string) => Promise<void>
}

export const PinStep = ({ pin, name, avatar, isSubmitting, errorMessage, onChange, onComplete }: PinStepProps) => {
  return (
    <div>
      <PinPad
        value={pin}
        onChange={onChange}
        onComplete={onComplete}
        studentName={name.trim() || undefined}
        studentAvatar={avatar || '👧'}
        title="Create PIN"
        subtitle="Enter a 4-digit PIN to secure this profile"
        showBackButton={false}
        layout="inline"
        disabled={isSubmitting}
        errorMessage={errorMessage ?? undefined}
      />
    </div>
  )
}

