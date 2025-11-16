import { AnimatePresence, motion } from 'framer-motion'
import { useEffect } from 'react'
import { ArrowLeft, Check, X } from 'lucide-react'
import ModalShell from '../../../components/ModalShell'
import { useAddLearnerWizard } from '../hooks/useAddLearnerWizard'
import { NameStep } from '../components/wizard/NameStep'
import { AvatarStep } from '../components/wizard/AvatarStep'
import { PinStep } from '../components/wizard/PinStep'

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

const AddStudentModal = ({
  isOpen,
  onClose,
  newUser,
  setNewUser,
  onAddUser,
  isSubmitting,
  errorMessage,
}: AddStudentModalProps) => {
  const wizard = useAddLearnerWizard({
    initialUser: newUser,
    onComplete: async (user) => {
      setNewUser(user)
      await onAddUser()
    },
  })

  useEffect(() => {
    if (!isOpen) {
      const resetHandle = window.setTimeout(() => {
        wizard.reset()
      }, 0)
      return () => window.clearTimeout(resetHandle)
    }
    return undefined
  }, [isOpen, wizard])

  useEffect(() => {
    if (newUser.name !== wizard.newUser.name || newUser.avatar !== wizard.newUser.avatar || newUser.pin !== wizard.newUser.pin) {
      wizard.reset()
    }
  }, [newUser, wizard])

  const titleId = 'add-student-title'

  const handleClose = () => {
    if (isSubmitting || wizard.isSubmitting) return
    onClose()
  }

  const handleBack = () => {
    const result = wizard.handleBack()
    if (result === 'close') {
      onClose()
    }
  }

  const renderProgress = () => (
    <div className="mb-8 flex flex-wrap items-center justify-center gap-2">
      {wizard.STEP_SEQUENCE.map((_, index) => {
        const isActive = index === wizard.currentStepIndex
        const isComplete = index < wizard.currentStepIndex
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
            {index < wizard.STEP_SEQUENCE.length - 1 && (
              <span
                className={`h-1 w-10 rounded-full ${
                  index < wizard.currentStepIndex ? 'bg-gradient-to-r from-blue-500 to-purple-500' : 'bg-slate-100'
                }`}
              />
            )}
          </div>
        )
      })}
    </div>
  )

  const renderStepContent = () => {
    if (wizard.step === 'name') {
      return (
        <NameStep
          name={wizard.newUser.name}
          nameError={wizard.nameError}
          maxLength={wizard.NAME_MAX_LENGTH}
          isSubmitting={isSubmitting || wizard.isSubmitting}
          onChange={wizard.handleNameChange}
          onNext={wizard.handleNameNext}
        />
      )
    }
    if (wizard.step === 'avatar') {
      return (
        <AvatarStep
          name={wizard.newUser.name}
          avatar={wizard.newUser.avatar}
          isSubmitting={isSubmitting || wizard.isSubmitting}
          onSelect={wizard.handleAvatarSelect}
          onNext={wizard.handleAvatarNext}
        />
      )
    }
    return (
      <PinStep
        pin={wizard.newUser.pin}
        name={wizard.newUser.name}
        avatar={wizard.newUser.avatar}
        isSubmitting={isSubmitting || wizard.isSubmitting}
        errorMessage={errorMessage || wizard.error}
        onChange={wizard.handlePinChange}
        onComplete={wizard.handlePinComplete}
      />
    )
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
          {wizard.step === 'name' ? 'Close' : 'Back'}
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
        <motion.div key={wizard.step} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -16 }}>
          {renderStepContent()}
        </motion.div>
      </AnimatePresence>

      {(errorMessage || wizard.error) && wizard.step !== 'pin' && (
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
          {errorMessage || wizard.error}
        </div>
      )}
    </ModalShell>
  )
}

export default AddStudentModal
