import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle, XCircle } from 'lucide-react'
import type { AnswerMode, VerificationResults } from '../hooks/useLongDivisionVerification'

type LongDivisionAnswerInputsProps = {
  answerMode: AnswerMode
  quotientInput: string
  remainderInput: string
  fractionNumerator: string
  fractionDenominator: string
  decimalPart: string
  showAnswer: boolean
  verificationResults: VerificationResults | null
  onQuotientChange: (value: string) => void
  onRemainderChange: (value: string) => void
  onFractionNumeratorChange: (value: string) => void
  onFractionDenominatorChange: (value: string) => void
  onDecimalPartChange: (value: string) => void
  inputRefs: Record<string, HTMLInputElement | null>
}

export const LongDivisionAnswerInputs = ({
  answerMode,
  quotientInput,
  remainderInput,
  fractionNumerator,
  fractionDenominator,
  decimalPart,
  showAnswer,
  verificationResults,
  onQuotientChange,
  onRemainderChange,
  onFractionNumeratorChange,
  onFractionDenominatorChange,
  onDecimalPartChange,
  inputRefs,
}: LongDivisionAnswerInputsProps) => {
  return (
    <div className="space-y-4">
      {answerMode === 'remainder' && (
        <div className="flex flex-wrap items-center justify-center gap-3">
          <span className="text-base font-semibold text-slate-700">Quotient</span>
          <div className="relative">
            <input
              ref={(el) => {
                inputRefs.quotient = el
              }}
              type="text"
              inputMode="numeric"
              value={quotientInput}
              onChange={(event) => onQuotientChange(event.target.value.replace(/[^0-9]/g, ''))}
              disabled={showAnswer}
              className={`w-28 rounded-2xl border-2 px-4 py-2 text-center text-2xl font-bold font-mono outline-none transition ${
                verificationResults?.quotientCorrect === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : verificationResults?.quotientCorrect === false
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-orange-300 bg-slate-50 text-slate-900 focus:border-orange-500 focus:bg-white'
              }`}
              placeholder="?"
            />
            <AnimatePresence>
              {verificationResults?.quotientCorrect === true && (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 shadow-lg">
                    <CheckCircle className="h-5 w-5 text-white" />
                  </div>
                </motion.div>
              )}
              {verificationResults?.quotientCorrect === false && (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500 shadow-lg">
                    <XCircle className="h-5 w-5 text-white" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          <span className="text-lg font-bold text-slate-500">r</span>
          <div className="relative">
            <input
              ref={(el) => {
                inputRefs.remainder = el
              }}
              type="text"
              inputMode="numeric"
              value={remainderInput}
              onChange={(event) => onRemainderChange(event.target.value.replace(/[^0-9]/g, ''))}
              disabled={showAnswer}
              className={`w-24 rounded-2xl border-2 px-4 py-2 text-center text-2xl font-bold font-mono outline-none transition ${
                verificationResults?.remainderCorrect === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : verificationResults?.remainderCorrect === false
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-orange-200 bg-slate-50 text-slate-900 focus:border-orange-400 focus:bg-white'
              }`}
              placeholder="?"
            />
          </div>
        </div>
      )}

      {answerMode === 'fraction' && (
        <div className="flex flex-wrap items-center justify-center gap-3">
          <span className="text-base font-semibold text-slate-700">Quotient</span>
          <div className="relative">
            <input
              ref={(el) => {
                inputRefs.quotient = el
              }}
              type="text"
              inputMode="numeric"
              value={quotientInput}
              onChange={(event) => onQuotientChange(event.target.value.replace(/[^0-9]/g, ''))}
              disabled={showAnswer}
              className={`w-28 rounded-2xl border-2 px-4 py-2 text-center text-2xl font-bold font-mono outline-none transition ${
                verificationResults?.quotientCorrect === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : verificationResults?.quotientCorrect === false
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-orange-300 bg-slate-50 text-slate-900 focus:border-orange-500 focus:bg-white'
              }`}
              placeholder="?"
            />
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <input
                ref={(el) => {
                  inputRefs.fractionNumerator = el
                }}
                type="text"
                inputMode="numeric"
                value={fractionNumerator}
                onChange={(event) => onFractionNumeratorChange(event.target.value.replace(/[^0-9]/g, ''))}
                disabled={showAnswer}
                className={`w-20 rounded-2xl border-2 px-3 py-2 text-center text-xl font-bold font-mono outline-none transition ${
                  verificationResults?.fractionNumeratorCorrect === true
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : verificationResults?.fractionNumeratorCorrect === false
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-orange-200 bg-slate-50 text-slate-900 focus:border-orange-400 focus:bg-white'
                }`}
                placeholder="?"
              />
              <AnimatePresence>
                {verificationResults?.fractionNumeratorCorrect === true && (
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-green-500 shadow-lg">
                      <CheckCircle className="h-4 w-4 text-white" />
                    </div>
                  </motion.div>
                )}
                {verificationResults?.fractionNumeratorCorrect === false && (
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-red-500 shadow-lg">
                      <XCircle className="h-4 w-4 text-white" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <span className="text-2xl font-bold text-slate-500">/</span>
            <div className="relative">
              <input
                ref={(el) => {
                  inputRefs.fractionDenominator = el
                }}
                type="text"
                inputMode="numeric"
                value={fractionDenominator}
                onChange={(event) => onFractionDenominatorChange(event.target.value.replace(/[^0-9]/g, ''))}
                disabled={showAnswer}
                className={`w-20 rounded-2xl border-2 px-3 py-2 text-center text-xl font-bold font-mono outline-none transition ${
                  verificationResults?.fractionDenominatorCorrect === true
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : verificationResults?.fractionDenominatorCorrect === false
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-orange-200 bg-slate-50 text-slate-900 focus:border-orange-400 focus:bg-white'
                }`}
                placeholder="?"
              />
              <AnimatePresence>
                {verificationResults?.fractionDenominatorCorrect === true && (
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-green-500 shadow-lg">
                      <CheckCircle className="h-4 w-4 text-white" />
                    </div>
                  </motion.div>
                )}
                {verificationResults?.fractionDenominatorCorrect === false && (
                  <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-red-500 shadow-lg">
                      <XCircle className="h-4 w-4 text-white" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      )}

      {answerMode === 'decimal' && (
        <div className="flex flex-wrap items-center justify-center gap-3">
          <span className="text-base font-semibold text-slate-700">Quotient</span>
          <div className="relative">
            <input
              ref={(el) => {
                inputRefs.quotient = el
              }}
              type="text"
              inputMode="numeric"
              value={quotientInput}
              onChange={(event) => onQuotientChange(event.target.value.replace(/[^0-9]/g, ''))}
              disabled={showAnswer}
              className={`w-28 rounded-2xl border-2 px-4 py-2 text-center text-2xl font-bold font-mono outline-none transition ${
                verificationResults?.quotientCorrect === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : verificationResults?.quotientCorrect === false
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-orange-300 bg-slate-50 text-slate-900 focus:border-orange-500 focus:bg-white'
              }`}
              placeholder="?"
            />
          </div>
          <span className="text-2xl font-bold text-slate-500">.</span>
          <div className="relative">
            <input
              ref={(el) => {
                inputRefs.decimalPart = el
              }}
              type="text"
              inputMode="numeric"
              value={decimalPart}
              onChange={(event) => onDecimalPartChange(event.target.value.replace(/[^0-9]/g, '').slice(0, 2))}
              disabled={showAnswer}
              className={`w-24 rounded-2xl border-2 px-4 py-2 text-center text-2xl font-bold font-mono outline-none transition ${
                verificationResults?.decimalPartCorrect === true
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : verificationResults?.decimalPartCorrect === false
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-orange-200 bg-slate-50 text-slate-900 focus:border-orange-400 focus:bg-white'
              }`}
              placeholder="?"
            />
            <AnimatePresence>
              {verificationResults?.decimalPartCorrect === true && (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-500 shadow-lg">
                    <CheckCircle className="h-5 w-5 text-white" />
                  </div>
                </motion.div>
              )}
              {verificationResults?.decimalPartCorrect === false && (
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }} className="absolute -right-2 -top-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-red-500 shadow-lg">
                    <XCircle className="h-5 w-5 text-white" />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  )
}

