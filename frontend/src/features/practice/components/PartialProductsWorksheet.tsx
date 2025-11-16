import { useRef } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle } from 'lucide-react'

import type { PracticeQuestion, PartialProductsMode } from '../types'
import { usePartialProducts } from '../hooks/usePartialProducts'
import { GradientSurface } from '../../../components/ui'
import { renderProblemLayout } from '../layouts/ProblemLayouts'
import { PartialProductsIntro } from './PartialProductsIntro'
import { PartialProductsRows } from './PartialProductsRows'
import { PartialProductsFinalAnswer } from './PartialProductsFinalAnswer'
import { PartialProductsFeedback } from './PartialProductsFeedback'

type PartialProductsWorksheetProps = {
  question: PracticeQuestion
  mode?: PartialProductsMode
  onComplete?: (isCorrect: boolean) => void
}

const PartialProductsWorksheet = ({
  question,
  mode = 'easy',
  onComplete,
}: PartialProductsWorksheetProps) => {
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({})
  const operandsLabel = `${question.operand1} × ${question.operand2}`

  const {
    partialProducts,
    finalAnswer,
    feedback,
    showAnswer,
    verificationResults,
    allowRowManagement,
    setFinalAnswer,
    handlePartialProductChange,
    handleAddPartialProduct,
    handleRemovePartialProduct,
    verify,
    reset,
  } = usePartialProducts({
    question,
    mode,
    onComplete,
  })

  return (
    <div className="space-y-6">
      <PartialProductsIntro operandsLabel={operandsLabel} />

      <GradientSurface variant="soft" tone="neutral" className="p-6 sm:p-8">
        <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="w-full">
          <div className="mb-10 flex justify-center">
            <div className="max-w-md text-center">{renderProblemLayout('vertical', { question })}</div>
          </div>

          <PartialProductsRows
            rows={partialProducts}
            mode={mode}
            showAnswer={showAnswer}
            allowRowManagement={allowRowManagement}
            onRowChange={(id, value) => handlePartialProductChange(id, value, inputRefs.current)}
            onAddRow={() => handleAddPartialProduct(inputRefs.current)}
            onRemoveRow={handleRemovePartialProduct}
            inputRefs={inputRefs.current}
          />

          <div className="max-w-md mx-auto mb-6">
            <div className="flex items-center justify-center gap-3">
              <div className="h-1 flex-1 bg-slate-200 rounded-full" />
              <span className="text-slate-400 text-2xl">+</span>
              <div className="h-1 flex-1 bg-slate-200 rounded-full" />
            </div>
          </div>

          <PartialProductsFinalAnswer
            finalAnswer={finalAnswer}
            showAnswer={showAnswer}
            verificationResults={verificationResults}
            correctAnswer={question.correctAnswer}
            hint={question.hint}
            onFinalAnswerChange={(value) => setFinalAnswer(value.replace(/[^0-9]/g, ''))}
            inputRef={inputRefs.current.final || null}
          />

          <PartialProductsFeedback feedback={feedback} verificationResults={verificationResults} />

          <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
            {!showAnswer ? (
              <button
                type="button"
                onClick={verify}
                disabled={!finalAnswer || partialProducts.every((row) => !row.value)}
                className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-lg font-semibold shadow-lg transition enabled:hover:scale-[1.02] disabled:opacity-40"
              >
                <CheckCircle className="w-5 h-5" />
                Check My Work
              </button>
            ) : (
              <button
                type="button"
                onClick={() => reset(inputRefs.current)}
                className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-white text-slate-700 text-lg font-semibold shadow-lg transition hover:scale-[1.02]"
              >
                Try Again
              </button>
            )}
          </div>
        </motion.div>
      </GradientSurface>
    </div>
  )
}

export default PartialProductsWorksheet
