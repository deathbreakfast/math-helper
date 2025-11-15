import { AnimatePresence, motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import { AlertTriangle, Check, X } from 'lucide-react'
import ModalShell from '../../../components/ModalShell'
import PinPad from '../components/PinPad'
import type { User } from '../hooks/useStudents'

type PINVerificationModalProps = {
  isOpen: boolean
  onClose: () => void
  onVerified: (pin: string) => void
  selectedUser: User | null
}

const PINVerificationModal = ({ isOpen, onClose, onVerified, selectedUser }: PINVerificationModalProps) => {
  const [pin, setPin] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isVerifying, setIsVerifying] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const titleId = 'pin-verification-title'

  useEffect(() => {
    if (!isOpen) {
      const resetHandle = window.setTimeout(() => {
        setPin('')
        setError(null)
        setIsVerifying(false)
        setShowSuccess(false)
      }, 0)
      return () => window.clearTimeout(resetHandle)
    }
    return undefined
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return
    const resetHandle = window.setTimeout(() => {
      setPin('')
      setError(null)
      setIsVerifying(false)
    }, 0)
    return () => window.clearTimeout(resetHandle)
  }, [selectedUser, isOpen])

  const handleModalClose = () => {
    if (isVerifying) return
    onClose()
  }

  const handlePinChange = (next: string) => {
    if (isVerifying) return
    setPin(next)
    setError(null)
  }

  const handleVerify = () => {
    if (!selectedUser || isVerifying) return
    if (pin.length !== 4) {
      setError('Enter all four digits to continue.')
      return
    }

    setIsVerifying(true)
    setError(null)

    window.setTimeout(() => {
      const isMatch = pin === selectedUser.pin
      setIsVerifying(false)

      if (isMatch) {
        setShowSuccess(true)
        const verifiedPin = pin
        window.setTimeout(() => {
          setShowSuccess(false)
          setPin('')
          onVerified(verifiedPin)
        }, 700)
        return
      }

      setError('Incorrect PIN. Please try again.')
      setPin('')
    }, 500)
  }

  return (
    <ModalShell isOpen={isOpen} onClose={handleModalClose} maxWidth="sm" showCloseButton={false} ariaLabelledBy={titleId}>
      <div className="relative overflow-hidden">
        <AnimatePresence>
          {showSuccess && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-20 flex items-center justify-center bg-gradient-to-br from-emerald-500 to-green-600"
            >
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', duration: 0.5 }}>
                <div className="flex h-24 w-24 items-center justify-center rounded-full bg-white shadow-2xl">
                  <Check className="h-14 w-14 text-emerald-500" strokeWidth={3} />
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

      <div className="relative z-10 space-y-8">
        <div className="flex items-center justify-between">
          <h2 id={titleId} className="text-2xl font-bold text-slate-900">
            Enter PIN
          </h2>
            <button
              type="button"
              onClick={handleModalClose}
              className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
              aria-label="Close verification modal"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {selectedUser ? (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center text-center"
          >
            <div className="mb-4 flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 text-5xl text-white shadow-xl">
              {selectedUser.avatar}
            </div>
            <h3 className="text-xl font-semibold text-slate-900">{selectedUser.name}</h3>
            <p className="mt-1 text-sm text-slate-500">Enter your PIN to continue</p>
          </motion.div>
          ) : (
            <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              <span className="font-semibold">Select a learner</span> to enter a PIN.
            </div>
          )}

          <PinPad
            value={pin}
            onChange={handlePinChange}
            layout="inline"
            showHeader={false}
            showContinueButton={false}
            disabled={!selectedUser || isVerifying}
          />

          {error && (
            <div className="flex items-center gap-2 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">
              <AlertTriangle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={handleModalClose}
              disabled={isVerifying}
              className="rounded-xl bg-slate-200 px-6 py-3 font-medium text-slate-800 transition hover:bg-slate-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleVerify}
              disabled={!selectedUser || pin.length !== 4 || isVerifying}
              className="flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-semibold text-white shadow-lg transition hover:from-blue-700 hover:to-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isVerifying ? 'Verifying…' : 'Start Practice'}
            </button>
          </div>
        </div>
      </div>
    </ModalShell>
  )
}

export default PINVerificationModal


