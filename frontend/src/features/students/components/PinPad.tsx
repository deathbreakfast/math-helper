import { useCallback, useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeft, Check, Delete, X } from 'lucide-react'

type PinPadProps = {
  maxDigits?: number
  value?: string
  onChange?: (pin: string) => void
  onComplete?: (pin: string) => void
  onBack?: () => void
  errorMessage?: string
  studentName?: string
  studentAvatar?: string
  title?: string
  subtitle?: string
  showBackButton?: boolean
  showHeader?: boolean
  showContinueButton?: boolean
  continueLabel?: string
  layout?: 'inline' | 'fullscreen'
  disabled?: boolean
}

const NUMBER_GRID = [
  ['1', '2', '3'],
  ['4', '5', '6'],
  ['7', '8', '9'],
  ['clear', '0', 'delete'],
]

const PinPad = ({
  maxDigits = 4,
  value = '',
  onChange,
  onComplete,
  onBack,
  errorMessage,
  studentName,
  studentAvatar,
  title = 'Create PIN',
  subtitle = 'Enter a 4-digit PIN to secure this profile',
  showBackButton = true,
  showHeader = true,
  showContinueButton = true,
  continueLabel = 'Continue',
  layout = 'inline',
  disabled = false,
}: PinPadProps) => {
  const [pin, setPin] = useState(value)
  const [activeButton, setActiveButton] = useState<string | null>(null)
  const [localError, setLocalError] = useState('')

  useEffect(() => {
    setPin(value)
  }, [value])

  useEffect(() => {
    if (errorMessage) {
      setLocalError(errorMessage)
    }
  }, [errorMessage])

  const isComplete = pin.length === maxDigits

  const updatePin = useCallback(
    (next: string) => {
      if (disabled) return
      setPin(next)
      setLocalError('')
      onChange?.(next)
    },
    [disabled, onChange],
  )

  const handleNumberPress = useCallback(
    (digit: string) => {
      if (pin.length >= maxDigits || disabled) return
      updatePin(`${pin}${digit}`)
      setActiveButton(digit)
      window.setTimeout(() => setActiveButton(null), 120)
    },
    [pin, maxDigits, disabled, updatePin],
  )

  const handleDelete = useCallback(() => {
    if (pin.length === 0 || disabled) return
    updatePin(pin.slice(0, -1))
    setActiveButton('delete')
    window.setTimeout(() => setActiveButton(null), 120)
  }, [pin, disabled, updatePin])

  const handleClear = useCallback(() => {
    if (pin.length === 0 || disabled) return
    updatePin('')
    setActiveButton('clear')
    window.setTimeout(() => setActiveButton(null), 120)
  }, [pin, disabled, updatePin])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (disabled) return
      if (event.key >= '0' && event.key <= '9') {
        event.preventDefault()
        handleNumberPress(event.key)
      } else if (event.key === 'Backspace') {
        event.preventDefault()
        handleDelete()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleNumberPress, handleDelete, disabled])

  const containerClasses =
    layout === 'fullscreen'
      ? 'min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center p-4'
      : ''

  const card = (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 16 }}
      className="w-full rounded-2xl border border-slate-100 bg-white p-6 sm:p-8"
    >
      {showBackButton && onBack && (
        <motion.button
          type="button"
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition hover:text-slate-900"
          onClick={onBack}
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </motion.button>
      )}

      {showHeader && (
        <div className="text-center">
          {studentAvatar && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 220, damping: 18 }}
              className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 text-5xl"
            >
              {studentAvatar}
            </motion.div>
          )}
          {(title || studentName) && (
            <h3 className="text-2xl font-bold text-slate-900">
              {studentName ? `${title} for ${studentName}` : title}
            </h3>
          )}
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
      )}

      <div className="mt-8 flex justify-center gap-4">
        {Array.from({ length: maxDigits }).map((_, index) => {
          const isFilled = index < pin.length
          return (
            <motion.div key={index} initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="relative">
              <div
                className={`flex h-14 w-14 items-center justify-center rounded-2xl border-2 transition ${
                  isFilled ? 'border-blue-600 bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg' : 'border-slate-200 bg-slate-50'
                }`}
              >
                {isFilled && <div className="h-3 w-3 rounded-full bg-white shadow-inner" />}
              </div>
              {isFilled && index === maxDigits - 1 && (
                <motion.span
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 text-white"
                >
                  <Check className="h-3 w-3" />
                </motion.span>
              )}
            </motion.div>
          )
        })}
      </div>

      <AnimatePresence>
        {(localError || errorMessage) && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700"
          >
            {localError || errorMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-6 space-y-3">
        {NUMBER_GRID.map((row) => (
          <div key={row.join('-')} className="grid grid-cols-3 gap-3">
            {row.map((value) => {
              const isNumber = /^\d$/.test(value)
              const isDelete = value === 'delete'
              const isClear = value === 'clear'
              const isDisabled =
                disabled ||
                (isNumber && pin.length >= maxDigits) ||
                ((isDelete || isClear) && pin.length === 0)

              const baseClasses =
                'h-14 rounded-xl text-lg font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2'

              let className = baseClasses
              if (isNumber) {
                className += isDisabled
                  ? ' bg-slate-100 text-slate-400'
                  : ` bg-gradient-to-br from-blue-500 to-purple-600 text-white shadow-lg hover:from-blue-600 hover:to-purple-700 ${
                      activeButton === value ? 'scale-95' : ''
                    }`
              } else if (isDelete) {
                className += isDisabled
                  ? ' bg-slate-100 text-slate-400'
                  : ` bg-red-100 text-red-600 hover:bg-red-200 ${activeButton === value ? 'scale-95' : ''}`
              } else {
                className += isDisabled
                  ? ' bg-slate-100 text-slate-400'
                  : ` bg-amber-100 text-amber-700 hover:bg-amber-200 ${activeButton === value ? 'scale-95' : ''}`
              }

              const handleClick = () => {
                if (isDisabled) return
                if (isNumber) {
                  handleNumberPress(value)
                } else if (isDelete) {
                  handleDelete()
                } else {
                  handleClear()
                }
              }

              return (
                <motion.button
                  key={value}
                  type="button"
                  whileTap={!isDisabled ? { scale: 0.96 } : undefined}
                  disabled={isDisabled}
                  className={className}
                  onClick={handleClick}
                >
                  {isNumber ? (
                    value
                  ) : isDelete ? (
                    <Delete className="mx-auto h-5 w-5" />
                  ) : (
                    <X className="mx-auto h-5 w-5" />
                  )}
                </motion.button>
              )
            })}
          </div>
        ))}
      </div>

      <p className="mt-4 text-center text-sm text-slate-500">
        {pin.length} / {maxDigits} digits entered
      </p>

      {showContinueButton && (
        <motion.button
          type="button"
          disabled={!isComplete || disabled}
          whileTap={isComplete && !disabled ? { scale: 0.98 } : undefined}
          className="mt-6 w-full rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-6 py-3 text-base font-semibold text-white shadow-lg transition hover:from-emerald-600 hover:to-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => (isComplete && !disabled ? onComplete?.(pin) : null)}
        >
          {continueLabel}
        </motion.button>
      )}
    </motion.div>
  )

  if (layout === 'fullscreen') {
    return (
      <div className={containerClasses}>
        <div className="w-full max-w-md">{card}</div>
      </div>
    )
  }

  return card
}

export default PinPad

