import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle, Plus, Trash2, XCircle } from 'lucide-react'
import type { PartialProductRow } from '../hooks/usePartialProducts'

type PartialProductsRowsProps = {
  rows: PartialProductRow[]
  mode: 'easy' | 'normal'
  showAnswer: boolean
  allowRowManagement: boolean
  onRowChange: (id: string, value: string) => void
  onAddRow: () => void
  onRemoveRow: (id: string) => void
  inputRefs: Record<string, HTMLInputElement | null>
}

export const PartialProductsRows = ({
  rows,
  mode,
  showAnswer,
  allowRowManagement,
  onRowChange,
  onAddRow,
  onRemoveRow,
  inputRefs,
}: PartialProductsRowsProps) => {
  return (
    <div className="mt-2 mb-8">
      <h3 className="text-xl font-semibold text-slate-800 mb-4 text-center">Partial Products</h3>
      <div className="space-y-4 max-w-md mx-auto">
        {rows.map((row, index) => (
          <motion.div
            key={row.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.05 * index }}
            className="flex items-center justify-end gap-3"
          >
            {mode === 'easy' && row.promptLabel && (
              <div className="text-sm font-semibold text-slate-500 w-32 text-left">{row.promptLabel}</div>
            )}
            <div className="relative flex-1 max-w-xs">
              <input
                ref={(el) => {
                  inputRefs[row.id] = el
                }}
                type="text"
                inputMode="numeric"
                value={row.value}
                onChange={(event) => onRowChange(row.id, event.target.value)}
                disabled={showAnswer}
                className={`font-mono text-2xl sm:text-3xl font-bold text-right w-full px-4 py-2 border-2 rounded-xl outline-none transition ${
                  row.isCorrect === true
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : row.isCorrect === false
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-indigo-200 bg-indigo-50 text-slate-900 focus:border-indigo-400 focus:bg-white'
                }`}
                placeholder="?"
              />
              <AnimatePresence>
                {row.isCorrect === true && (
                  <motion.div
                    initial={{ scale: 0, rotate: -120 }}
                    animate={{ scale: 1, rotate: 0 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-2 -top-2"
                  >
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
                      <CheckCircle className="w-5 h-5 text-white" />
                    </div>
                  </motion.div>
                )}
                {row.isCorrect === false && (
                  <motion.div
                    initial={{ scale: 0, rotate: -120 }}
                    animate={{ scale: 1, rotate: 0 }}
                    exit={{ scale: 0 }}
                    className="absolute -right-2 -top-2"
                  >
                    <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center shadow-lg">
                      <XCircle className="w-5 h-5 text-white" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            {allowRowManagement && rows.length > 1 && !showAnswer && (
              <button
                type="button"
                onClick={() => onRemoveRow(row.id)}
                className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition"
                aria-label="Remove partial product row"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}
          </motion.div>
        ))}

        {allowRowManagement && !showAnswer && (
          <motion.button
            type="button"
            initial={{ opacity: 0.6 }}
            animate={{ opacity: 1 }}
            onClick={onAddRow}
            className="flex items-center justify-center gap-2 w-full px-4 py-3 bg-white text-indigo-600 rounded-xl hover:bg-indigo-50 transition border-2 border-dashed border-indigo-200"
          >
            <Plus className="w-5 h-5" />
            <span className="font-medium">Add Another Partial Product</span>
          </motion.button>
        )}
      </div>
    </div>
  )
}

