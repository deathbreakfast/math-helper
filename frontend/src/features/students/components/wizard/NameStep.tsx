import { AnimatePresence, motion } from 'framer-motion'
import { PillButton } from '../../../../components/ui'

type NameStepProps = {
  name: string
  nameError: string
  maxLength: number
  isSubmitting: boolean
  onChange: (name: string) => void
  onNext: () => void
}

export const NameStep = ({ name, nameError, maxLength, isSubmitting, onChange, onNext }: NameStepProps) => {
  return (
    <div className="text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mx-auto mb-6 flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 text-5xl"
      >
        ✍️
      </motion.div>
      <h3 className="text-2xl font-bold text-slate-900">What&apos;s your name?</h3>
      <p className="mt-1 text-sm text-slate-500">Enter a first name or nickname for this learner.</p>
      <div className="mt-8 text-left">
        <label className="text-sm font-semibold text-slate-600">Name</label>
        <input
          type="text"
          value={name}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault()
              onNext()
            }
          }}
          maxLength={maxLength}
          data-testid="testid-learner-name-input"
          className={`mt-2 w-full rounded-2xl border-2 px-5 py-4 text-lg font-medium text-slate-900 shadow-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            nameError ? 'border-red-300 bg-red-50' : 'border-slate-200 bg-white'
          }`}
          placeholder="Enter learner name"
        />
        <div className="mt-2 text-right text-xs text-slate-500">
          {name.trim().length}/{maxLength} characters
        </div>
        <AnimatePresence>
          {nameError && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700"
            >
              {nameError}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <PillButton 
        type="button" 
        onClick={onNext} 
        disabled={!name.trim() || isSubmitting} 
        fullWidth 
        className="mt-6 text-base"
        data-testid="testid-name-step-next-button"
      >
        Next: Choose Avatar
      </PillButton>
    </div>
  )
}

