import { motion } from 'framer-motion'
import type { AnswerMode } from '../hooks/useLongDivisionVerification'

type AnswerFormatSwitcherProps = {
  answerMode: AnswerMode
  formats: AnswerMode[]
}

export const AnswerFormatSwitcher = ({ answerMode, formats }: AnswerFormatSwitcherProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-center"
    >
      <div className="inline-flex items-center rounded-2xl bg-white p-2 shadow-lg ring-1 ring-slate-100">
        <span className="px-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Answer Format</span>
        {formats.map((format) => (
          <div
            key={format}
            className={`px-4 py-2 text-sm font-semibold rounded-xl ${
              answerMode === format
                ? 'bg-gradient-to-r from-orange-500 to-amber-600 text-white shadow-md'
                : 'text-slate-400'
            }`}
          >
            {format === 'remainder' ? 'Remainder' : format === 'fraction' ? 'Fraction' : 'Decimal'}
          </div>
        ))}
      </div>
    </motion.div>
  )
}

