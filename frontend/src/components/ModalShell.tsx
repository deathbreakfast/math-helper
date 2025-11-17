import { AnimatePresence, motion } from 'framer-motion'
import { X } from 'lucide-react'
import type { ReactNode } from 'react'

type ModalShellProps = {
  isOpen: boolean
  onClose: () => void
  children: ReactNode
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl'
  paddingClassName?: string
  showCloseButton?: boolean
  closeButtonAriaLabel?: string
  overlayClassName?: string
  cardClassName?: string
  ariaLabelledBy?: string
  ariaDescribedBy?: string
}

const WIDTH_MAP: Record<NonNullable<ModalShellProps['maxWidth']>, string> = {
  sm: 'max-w-md',
  md: 'max-w-2xl',
  lg: 'max-w-3xl',
  xl: 'max-w-7xl',
}

const ModalShell = ({
  isOpen,
  onClose,
  children,
  maxWidth = 'md',
  paddingClassName = 'p-6 sm:p-8',
  showCloseButton = true,
  closeButtonAriaLabel = 'Close dialog',
  overlayClassName = 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50',
  cardClassName = '',
  ariaLabelledBy,
  ariaDescribedBy,
}: ModalShellProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${overlayClassName}`}
          role="dialog"
          aria-modal="true"
          aria-labelledby={ariaLabelledBy}
          aria-describedby={ariaDescribedBy}
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            onClick={(event) => event.stopPropagation()}
            className={`w-full ${WIDTH_MAP[maxWidth]} rounded-[32px] bg-white/90 shadow-2xl backdrop-blur ${paddingClassName} ${cardClassName}`}
          >
            {showCloseButton && (
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={onClose}
                  aria-label={closeButtonAriaLabel}
                  className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            )}
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default ModalShell

