import { motion } from 'framer-motion'
import { AVATAR_OPTIONS } from '../../../../lib/learners/api'
import { PillButton } from '../../../../components/ui'

type AvatarStepProps = {
  name: string
  avatar: string
  isSubmitting: boolean
  onSelect: (avatar: string) => void
  onNext: () => void
}

export const AvatarStep = ({ name, avatar, isSubmitting, onSelect, onNext }: AvatarStepProps) => {
  return (
    <div className="text-center" data-testid="testid-avatar-step">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mx-auto mb-6 flex h-28 w-28 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 text-6xl"
      >
        {avatar || '👧'}
      </motion.div>
      <h3 className="text-2xl font-bold text-slate-900">
        {name ? `Hi ${name.trim()}! Pick your avatar` : 'Pick an avatar'}
      </h3>
      <p className="mt-1 text-sm text-slate-500">Choose an emoji that feels right.</p>
      <div className="mt-8 grid grid-cols-5 gap-3" data-testid="testid-avatar-options">
        {AVATAR_OPTIONS.map((option, index) => {
          const isSelected = option === avatar
          return (
            <motion.button
              key={`avatar-${index}-${option}`}
              type="button"
              whileTap={{ scale: 0.9 }}
              onClick={() => onSelect(option)}
              data-testid={`testid-avatar-option-${option}`}
              className={`rounded-2xl p-3 text-3xl transition ${
                isSelected
                  ? 'bg-gradient-to-br from-blue-100 to-purple-100 ring-2 ring-blue-500 shadow-lg'
                  : 'bg-white shadow hover:bg-slate-50'
              }`}
            >
              {option}
            </motion.button>
          )
        })}
      </div>
      <PillButton 
        type="button" 
        onClick={onNext} 
        disabled={!avatar || isSubmitting} 
        fullWidth 
        className="mt-8 text-base"
        data-testid="testid-avatar-step-next-button"
      >
        Next: Create PIN
      </PillButton>
    </div>
  )
}

