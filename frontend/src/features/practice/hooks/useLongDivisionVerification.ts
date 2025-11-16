import { useEffect, useState } from 'react'
import type { DivisionStep } from '../utils/longDivision'
import { buildDivisionSteps, calculateExpectedAnswers } from '../utils/longDivision'

export type AnswerMode = 'remainder' | 'fraction' | 'decimal'

export type VerificationResults = {
  quotientCorrect: boolean
  remainderCorrect?: boolean
  fractionNumeratorCorrect?: boolean
  fractionDenominatorCorrect?: boolean
  decimalPartCorrect?: boolean
  stepsCorrect: boolean[]
  message: string
}

type UseLongDivisionVerificationProps = {
  dividend: number
  divisor: number
  answerMode: AnswerMode
}

export const useLongDivisionVerification = ({ dividend, divisor, answerMode }: UseLongDivisionVerificationProps) => {
  const expectedSteps = buildDivisionSteps(dividend, divisor)
  const { expectedQuotient, expectedRemainder, expectedDecimalPart } = calculateExpectedAnswers(dividend, divisor)

  const [divisionSteps, setDivisionSteps] = useState<DivisionStep[]>(expectedSteps)
  const [quotientInput, setQuotientInput] = useState('')
  const [remainderInput, setRemainderInput] = useState('')
  const [fractionNumerator, setFractionNumerator] = useState('')
  const [fractionDenominator, setFractionDenominator] = useState('')
  const [decimalPart, setDecimalPart] = useState('')
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | 'partial' | null>(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [verificationResults, setVerificationResults] = useState<VerificationResults | null>(null)

  useEffect(() => {
    setDivisionSteps(expectedSteps)
    setQuotientInput('')
    setRemainderInput('')
    setFractionNumerator('')
    setFractionDenominator('')
    setDecimalPart('')
    setFeedback(null)
    setShowAnswer(false)
    setVerificationResults(null)
  }, [expectedSteps])

  useEffect(() => {
    setQuotientInput('')
    setRemainderInput('')
    setFractionNumerator('')
    setFractionDenominator('')
    setDecimalPart('')
    setFeedback(null)
    setShowAnswer(false)
    setVerificationResults(null)
  }, [answerMode])

  const handleStepChange = (id: string, value: string, inputRefs: Record<string, HTMLInputElement | null>) => {
    const numericValue = value.replace(/[^0-9]/g, '')
    setDivisionSteps((prev) =>
      prev.map((step) =>
        step.id === id
          ? {
              ...step,
              value: numericValue,
            }
          : step,
      ),
    )

    if (numericValue) {
      const currentIndex = divisionSteps.findIndex((step) => step.id === id)
      const nextStep = divisionSteps[currentIndex + 1]
      if (nextStep) {
        setTimeout(() => inputRefs[nextStep.id]?.focus(), 80)
      } else {
        const answerTarget =
          answerMode === 'remainder'
            ? 'remainder'
            : answerMode === 'fraction'
              ? 'fractionNumerator'
              : 'decimal'
        setTimeout(() => inputRefs[answerTarget]?.focus(), 80)
      }
    }
  }

  const verify = () => {
    const userQuotient = Number(quotientInput) || 0
    const quotientCorrect = userQuotient === expectedQuotient

    let remainderCorrect: boolean | undefined
    let fractionNumeratorCorrect: boolean | undefined
    let fractionDenominatorCorrect: boolean | undefined
    let decimalPartCorrect: boolean | undefined

    if (answerMode === 'remainder') {
      remainderCorrect = Number(remainderInput) === expectedRemainder
    } else if (answerMode === 'fraction') {
      fractionNumeratorCorrect = Number(fractionNumerator) === expectedRemainder
      fractionDenominatorCorrect = Number(fractionDenominator) === divisor
    } else if (answerMode === 'decimal') {
      const normalizedInput = decimalPart.padEnd(expectedDecimalPart.length, '0')
      decimalPartCorrect = normalizedInput === expectedDecimalPart
    }

    const stepsCorrect = divisionSteps.map((step) => {
      const numericValue = Number(step.value) || 0
      return step.expectedValue !== null && numericValue === step.expectedValue
    })

    setDivisionSteps((prev) =>
      prev.map((step, index) => ({
        ...step,
        isCorrect: stepsCorrect[index],
      })),
    )

    setShowAnswer(true)

    const allStepsCorrect = stepsCorrect.every(Boolean)
    const answerFieldsCorrect =
      answerMode === 'remainder'
        ? Boolean(quotientCorrect && remainderCorrect)
        : answerMode === 'fraction'
          ? Boolean(quotientCorrect && fractionNumeratorCorrect && fractionDenominatorCorrect)
          : Boolean(quotientCorrect && decimalPartCorrect)
    const allCorrect = answerFieldsCorrect && allStepsCorrect

    let message = ''
    if (allCorrect) {
      setFeedback('correct')
      message = '🎉 Perfect! You completed every long division step.'
    } else if (answerFieldsCorrect && !allStepsCorrect) {
      setFeedback('partial')
      message = '👍 Final answer looks good. Double-check the individual steps.'
    } else if (!answerFieldsCorrect && allStepsCorrect) {
      setFeedback('partial')
      message = '👍 Work steps are correct. Revisit your answer inputs.'
    } else {
      setFeedback('incorrect')
      message = "❌ Let's review your work. Check each step and answer field carefully."
    }

    setVerificationResults({
      quotientCorrect,
      remainderCorrect,
      fractionNumeratorCorrect,
      fractionDenominatorCorrect,
      decimalPartCorrect,
      stepsCorrect,
      message,
    })
  }

  const reset = (inputRefs: Record<string, HTMLInputElement | null>) => {
    setDivisionSteps((prev) =>
      prev.map((step) => ({
        ...step,
        value: '',
        isCorrect: undefined,
      })),
    )
    setQuotientInput('')
    setRemainderInput('')
    setFractionNumerator('')
    setFractionDenominator('')
    setDecimalPart('')
    setFeedback(null)
    setShowAnswer(false)
    setVerificationResults(null)

    setTimeout(() => inputRefs.quotient?.focus(), 120)
  }

  const answerFieldsComplete =
    answerMode === 'remainder'
      ? Boolean(quotientInput && remainderInput)
      : answerMode === 'fraction'
        ? Boolean(quotientInput && fractionNumerator && fractionDenominator)
        : Boolean(quotientInput && decimalPart)

  return {
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
    expectedQuotient,
    expectedRemainder,
    expectedDecimalPart,
  }
}

