import { useMemo, useRef } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle } from 'lucide-react'

import type { NoticeConfig, PracticeQuestion, TipConfig } from '../types'
import type { AnswerMode } from '../hooks/useLongDivisionVerification'
import { useLongDivisionVerification } from '../hooks/useLongDivisionVerification'
import { getAnswerDisplay } from '../utils/longDivision'
import { GradientSurface } from '../../../components/ui'
import { LongDivisionNotice } from './LongDivisionNotice'
import { AnswerFormatSwitcher } from './AnswerFormatSwitcher'
import { LongDivisionAnswerInputs } from './LongDivisionAnswerInputs'
import { LongDivisionWorkSteps } from './LongDivisionWorkSteps'
import { LongDivisionFeedback } from './LongDivisionFeedback'
import { LongDivisionTip } from './LongDivisionTip'

type LongDivisionWorksheetProps = {
  question: PracticeQuestion
  notice?: NoticeConfig
  tip?: TipConfig
  answerFormats?: AnswerMode[]
}

const defaultNotice: NoticeConfig = {
  tone: 'orange',
  icon: 'lightbulb',
  title: 'Long Division',
  body: 'Use the long division algorithm to break the problem into clear steps.',
}

const defaultTip: TipConfig = {
  icon: 'lightbulb',
  title: 'Long Division Tip',
  body: 'Remember the cycle: Divide, Multiply, Subtract, then Bring Down the next digit.',
}

const LongDivisionWorksheet = ({
  question,
  notice = defaultNotice,
  tip = defaultTip,
  answerFormats: answerFormatOptions,
}: LongDivisionWorksheetProps) => {
  const formats = useMemo<AnswerMode[]>(
    () => (answerFormatOptions && answerFormatOptions.length > 0 ? answerFormatOptions : ['remainder']),
    [answerFormatOptions],
  )
  const answerMode = useMemo<AnswerMode>(() => formats[0], [formats])
  const inputRefs = useRef<Record<string, HTMLInputElement | null>>({})

  const divisor = question.operand2
  const dividend = question.operand1

  const {
    divisionSteps,
    quotientInput,
    remainderInput,
    fractionNumerator,
    fractionDenominator,
    decimalPart,
    feedback,
    showAnswer,
    verificationResults,
    answerFieldsComplete,
    setQuotientInput,
    setRemainderInput,
    setFractionNumerator,
    setFractionDenominator,
    setDecimalPart,
    handleStepChange,
    verify,
    reset,
  } = useLongDivisionVerification({
    dividend,
    divisor,
    answerMode,
  })

  const answerDisplay = getAnswerDisplay(dividend, divisor, answerMode)

  return (
    <div className="space-y-6">
      {notice && <LongDivisionNotice notice={notice} />}

      <AnswerFormatSwitcher answerMode={answerMode} formats={formats} />

      <GradientSurface variant="soft" tone="neutral" className="p-6 sm:p-8">
        <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="space-y-8">
          <div className="space-y-4">
            <LongDivisionAnswerInputs
              answerMode={answerMode}
              quotientInput={quotientInput}
              remainderInput={remainderInput}
              fractionNumerator={fractionNumerator}
              fractionDenominator={fractionDenominator}
              decimalPart={decimalPart}
              showAnswer={showAnswer}
              verificationResults={verificationResults}
              onQuotientChange={(value) => setQuotientInput(value.replace(/[^0-9]/g, ''))}
              onRemainderChange={(value) => setRemainderInput(value.replace(/[^0-9]/g, ''))}
              onFractionNumeratorChange={(value) => setFractionNumerator(value.replace(/[^0-9]/g, ''))}
              onFractionDenominatorChange={(value) => setFractionDenominator(value.replace(/[^0-9]/g, ''))}
              onDecimalPartChange={(value) => setDecimalPart(value.replace(/[^0-9]/g, '').slice(0, 2))}
              inputRefs={inputRefs.current}
            />

            <LongDivisionFeedback
              feedback={feedback}
              verificationResults={verificationResults}
              answerMode={answerMode}
              answerDisplay={answerDisplay}
            />
          </div>

          <div className="flex justify-center">
            <div className="flex items-start gap-0">
              <div className="pt-6 pr-4 text-3xl font-bold text-slate-600 font-mono">{divisor}</div>
              <div className="rounded-tl-3xl border-l-4 border-t-4 border-slate-900 px-6 pb-2 pt-4">
                <div className="text-4xl font-bold tracking-widest text-slate-900 font-mono">{dividend}</div>
              </div>
            </div>
          </div>

          <LongDivisionWorkSteps
            steps={divisionSteps}
            showAnswer={showAnswer}
            onStepChange={(id, value) => handleStepChange(id, value, inputRefs.current)}
            inputRefs={inputRefs.current}
          />

          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            {!showAnswer ? (
              <button
                type="button"
                onClick={verify}
                disabled={!answerFieldsComplete || divisionSteps.some((step) => !step.value)}
                className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition enabled:hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-40"
              >
                <CheckCircle className="h-5 w-5" />
                Check My Work
              </button>
            ) : (
              <button
                type="button"
                onClick={() => reset(inputRefs.current)}
                className="rounded-2xl bg-white px-8 py-4 text-lg font-semibold text-slate-700 shadow-lg transition hover:scale-[1.02]"
              >
                Try Again
              </button>
            )}
          </div>
        </motion.div>
      </GradientSurface>

      {tip && <LongDivisionTip tip={tip} />}
    </div>
  )
}

export default LongDivisionWorksheet
