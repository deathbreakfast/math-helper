import { useEffect, useMemo, useState } from 'react'

const STEP_SEQUENCE = ['name', 'avatar', 'pin'] as const
export type Step = (typeof STEP_SEQUENCE)[number]

const NAME_MAX_LENGTH = 30

type NewUser = {
  name: string
  avatar: string
  pin: string
}

type UseAddLearnerWizardProps = {
  initialUser?: NewUser
  onComplete?: (user: NewUser) => Promise<void>
}

export const useAddLearnerWizard = ({ initialUser, onComplete }: UseAddLearnerWizardProps = {}) => {
  const [step, setStep] = useState<Step>('name')
  const [newUser, setNewUser] = useState<NewUser>(
    initialUser ?? {
      name: '',
      avatar: '',
      pin: '',
    },
  )
  const [nameError, setNameError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const currentStepIndex = useMemo(() => STEP_SEQUENCE.indexOf(step), [step])

  const isNameValid = newUser.name.trim().length >= 2
  const isAvatarValid = Boolean(newUser.avatar)
  const isPinValid = newUser.pin.length === 4

  const reset = () => {
    setStep('name')
    setNewUser({
      name: '',
      avatar: '',
      pin: '',
    })
    setNameError('')
    setError(null)
    setIsSubmitting(false)
  }

  const handleNameChange = (name: string) => {
    const nextValue = name.slice(0, NAME_MAX_LENGTH)
    setNameError('')
    setNewUser({ ...newUser, name: nextValue })
  }

  const handleNameNext = () => {
    if (!isNameValid) {
      setNameError('Please enter at least 2 characters')
      return false
    }
    setNameError('')
    setStep('avatar')
    return true
  }

  const handleAvatarSelect = (avatar: string) => {
    setNewUser({ ...newUser, avatar })
  }

  const handleAvatarNext = () => {
    if (!isAvatarValid) return false
    setStep('pin')
    return true
  }

  const handlePinChange = (pin: string) => {
    setNewUser({ ...newUser, pin })
  }

  const handlePinComplete = async (pin: string) => {
    if (isSubmitting || pin.length !== 4) return false
    
    // Update state synchronously before calling onComplete
    const updatedUser = { ...newUser, pin }
    setNewUser(updatedUser)
    
    if (onComplete) {
      setIsSubmitting(true)
      setError(null)
      try {
        // Use the updated user object directly instead of relying on state
        await onComplete(updatedUser)
        return true
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to create learner.'
        setError(message)
        return false
      } finally {
        setIsSubmitting(false)
      }
    }
    return false
  }

  const handleBack = () => {
    if (isSubmitting) return
    if (step === 'name') {
      return 'close'
    }
    if (step === 'avatar') {
      setStep('name')
      return 'back'
    }
    setStep('avatar')
    return 'back'
  }

  return {
    step,
    currentStepIndex,
    newUser,
    nameError,
    isSubmitting,
    error,
    isNameValid,
    isAvatarValid,
    isPinValid,
    reset,
    handleNameChange,
    handleNameNext,
    handleAvatarSelect,
    handleAvatarNext,
    handlePinChange,
    handlePinComplete,
    handleBack,
    setError,
    NAME_MAX_LENGTH,
    STEP_SEQUENCE,
  }
}

