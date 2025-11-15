import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useMemo, useState } from 'react'
import { ArrowLeft, Check, X } from 'lucide-react'
import ModalShell from '../../../components/ModalShell'
import { AVATAR_OPTIONS } from '../../../lib/learners/api'
import PinPad from '../components/PinPad'
import { PillButton } from '../../../components/ui'

type AddStudentModalProps = {
  isOpen: boolean
  onClose: () => void
  newUser: {
    name: string
    avatar: string
    pin: string
  }
  setNewUser: (user: { name: string; avatar: string; pin: string }) => void
  onAddUser: () => Promise<void>
  isSubmitting: boolean
  errorMessage?: string | null
}

const NAME_MAX_LENGTH = 30
const STEP_SEQUENCE = ['name', 'avatar', 'pin'] as const
type Step = (typeof STEP_SEQUENCE)[number]

const AddStudentModal = ({
  isOpen,
  onClose,
  newUser,
  setNewUser,
  onAddUser,
  isSubmitting,
  errorMessage,
}: AddStudentModalProps) => {
  const [step, setStep] = useState<Step>('name')
  const [nameError, setNameError] = useState('')

  useEffect(() => {
    if (!isOpen) {
      const resetHandle = window.setTimeout(() => {
        setStep('name')
        setNameError('')
      }, 0)
      return () => window.clearTimeout(resetHandle)
    }
    return undefined
  }, [isOpen])

  const titleId = 'add-student-title'

  const isNameValid = newUser.name.trim().length >= 2
  const isAvatarValid = Boolean(newUser.avatar)
  const currentStepIndex = useMemo(() => STEP_SEQUENCE.indexOf(step), [step])

  const handleClose = () => {
    if (isSubmitting) return
    onClose()
  }

  const handleBack = () => {
    if (isSubmitting) return
    if (step === 'name') {
      onClose()
      return
    }
    if (step === 'avatar') {
      setStep('name')
      return
    }
    setStep('avatar')
  }

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextValue = event.target.value.slice(0, NAME_MAX_LENGTH)
    setNameError('')
    setNewUser({ ...newUser, name: nextValue })
  }

  const handleNameNext = () => {
    if (!isNameValid) {
      setNameError('Please enter at least 2 characters')
      return
    }
    setNameError('')
    setStep('avatar')
  }

  const handleAvatarNext = () => {
    if (!isAvatarValid) return
    setStep('pin')
  }

  const handleAvatarSelect = (avatar: string) => {
    setNewUser({ ...newUser, avatar })
  }

  const handlePinChange = (pin: string) => {
    setNewUser({ ...newUser, pin })
  }

  const handlePinComplete = async (pin: string) => {
    if (isSubmitting || pin.length !== 4) return
    if (newUser.pin !== pin) {
      setNewUser({ ...newUser, pin })
    }
    await onAddUser()
  }

  const renderProgress = () => (
    <div className="mb-8 flex flex-wrap items-center justify-center gap-2">
      {STEP_SEQUENCE.map((_, index) => {
        const isActive = index === currentStepIndex
        const isComplete = index < currentStepIndex
        return (
          <div key={index} className="flex items-center gap-2">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold ${
                isActive
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : isComplete
                    ? 'bg-green-100 text-green-600'
                    : 'bg-slate-100 text-slate-400'
              }`}
            >
              {isComplete ? <Check className="h-4 w-4" /> : index + 1}
            </div>
            {index < STEP_SEQUENCE.length - 1 && (
              <span
                className={`h-1 w-10 rounded-full ${
                  index < currentStepIndex ? 'bg-gradient-to-r from-blue-500 to-purple-500' : 'bg-slate-100'
                }`}
              />
            )}
          </div>
        )
      })}
    </div>
  )

  const renderNameStep = () => (
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
          value={newUser.name}
          onChange={handleNameChange}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              event.preventDefault()
              handleNameNext()
            }
          }}
          maxLength={NAME_MAX_LENGTH}
          className={`mt-2 w-full rounded-2xl border-2 px-5 py-4 text-lg font-medium text-slate-900 shadow-sm focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            nameError ? 'border-red-300 bg-red-50' : 'border-slate-200 bg-white'
          }`}
          placeholder="Enter learner name"
        />
        <div className="mt-2 text-right text-xs text-slate-500">
          {newUser.name.trim().length}/{NAME_MAX_LENGTH} characters
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
        onClick={handleNameNext}
        disabled={!newUser.name.trim() || isSubmitting}
        fullWidth
        className="mt-6 text-base"
      >
        Next: Choose Avatar
      </PillButton>
    </div>
  )

  const renderAvatarStep = () => (
    <div className="text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="mx-auto mb-6 flex h-28 w-28 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 text-6xl"
      >
        {newUser.avatar || '👧'}
      </motion.div>
      <h3 className="text-2xl font-bold text-slate-900">
        {newUser.name ? `Hi ${newUser.name.trim()}! Pick your avatar` : 'Pick an avatar'}
      </h3>
      <p className="mt-1 text-sm text-slate-500">Choose an emoji that feels right.</p>
      <div className="mt-8 grid grid-cols-5 gap-3">
        {AVATAR_OPTIONS.map((avatar) => {
          const isSelected = avatar === newUser.avatar
          return (
            <motion.button
              key={avatar}
              type="button"
              whileTap={{ scale: 0.9 }}
              onClick={() => handleAvatarSelect(avatar)}
              className={`rounded-2xl p-3 text-3xl transition ${
                isSelected
                  ? 'bg-gradient-to-br from-blue-100 to-purple-100 ring-2 ring-blue-500 shadow-lg'
                  : 'bg-white shadow hover:bg-slate-50'
              }`}
            >
              {avatar}
            </motion.button>
          )
        })}
      </div>
      <PillButton
        type="button"
        onClick={handleAvatarNext}
        disabled={!isAvatarValid || isSubmitting}
        fullWidth
        className="mt-8 text-base"
      >
        Next: Create PIN
      </PillButton>
    </div>
  )

  const renderPinStep = () => (
    <div>
      <PinPad
        value={newUser.pin}
        onChange={handlePinChange}
        onComplete={handlePinComplete}
        studentName={newUser.name.trim() || undefined}
        studentAvatar={newUser.avatar || '👧'}
        title="Create PIN"
        subtitle="Enter a 4-digit PIN to secure this profile"
        showBackButton={false}
        layout="inline"
        disabled={isSubmitting}
        errorMessage={errorMessage ?? undefined}
      />
    </div>
  )

  const renderStepContent = () => {
    if (step === 'name') return renderNameStep()
    if (step === 'avatar') return renderAvatarStep()
    return renderPinStep()
  }

  return (
    <ModalShell isOpen={isOpen} onClose={handleClose} maxWidth="md" showCloseButton={false} ariaLabelledBy={titleId}>
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={handleBack}
          className="inline-flex items-center gap-2 rounded-full border border-transparent px-4 py-2 text-sm font-semibold text-slate-600 transition hover:border-slate-200 hover:bg-slate-50"
        >
          <ArrowLeft className="h-4 w-4" />
          {step === 'name' ? 'Close' : 'Back'}
        </button>
        <button
          type="button"
          onClick={handleClose}
          className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
          aria-label="Dismiss modal"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="mt-6 text-center">
        <h2 id={titleId} className="text-3xl font-bold text-slate-900">
          Add New Learner
        </h2>
        <p className="mt-1 text-sm text-slate-500">Follow the quick steps to set up a practice profile.</p>
      </div>

      <div className="mt-6">{renderProgress()}</div>

      <AnimatePresence mode="wait">
        <motion.div key={step} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}>
          {renderStepContent()}
        </motion.div>
      </AnimatePresence>

      {errorMessage && step !== 'pin' && (
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
          {errorMessage}
        </div>
      )}
    </ModalShell>
  )
}

export default AddStudentModal

