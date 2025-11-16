import { useEffect, useMemo, useState } from 'react'
import type { PartialProductsMode } from '../types'
import type { ExpectedPartial } from '../utils/partialProducts'
import { buildExpectedPartials } from '../utils/partialProducts'

export type PartialProductRow = {
  id: string
  value: string
  expectedValue?: number
  isCorrect?: boolean
  promptLabel?: string
}

export type VerificationResults = {
  partialProducts: boolean[]
  finalAnswer: boolean
  message: string
}

type UsePartialProductsProps = {
  question: { operand1: number; operand2: number; correctAnswer: string }
  mode: PartialProductsMode
  onComplete?: (isCorrect: boolean) => void
}

export const usePartialProducts = ({ question, mode, onComplete }: UsePartialProductsProps) => {
  const expectedPartials = useMemo(() => buildExpectedPartials(question as any, mode), [question, mode])

  const [partialProducts, setPartialProducts] = useState<PartialProductRow[]>([])
  const [finalAnswer, setFinalAnswer] = useState('')
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | 'partial' | null>(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [verificationResults, setVerificationResults] = useState<VerificationResults | null>(null)

  useEffect(() => {
    const basePartials =
      mode === 'normal'
        ? [
            {
              id: '1',
              value: '',
              expectedValue: expectedPartials[0]?.expectedValue,
            },
          ]
        : expectedPartials.map((expected, idx) => ({
            id: `${idx + 1}`,
            value: '',
            expectedValue: expected.expectedValue,
            promptLabel: expected.promptLabel,
          }))

    setPartialProducts(basePartials.length > 0 ? basePartials : [{ id: '1', value: '', expectedValue: 0 }])
    setFinalAnswer('')
    setFeedback(null)
    setShowAnswer(false)
    setVerificationResults(null)
  }, [expectedPartials, mode])

  const handlePartialProductChange = (id: string, value: string, inputRefs: Record<string, HTMLInputElement | null>) => {
    const numericValue = value.replace(/[^0-9]/g, '')
    setPartialProducts((prev) =>
      prev.map((row) =>
        row.id === id
          ? {
              ...row,
              value: numericValue,
            }
          : row,
      ),
    )

    if (numericValue) {
      const currentIndex = partialProducts.findIndex((row) => row.id === id)
      const nextRow = partialProducts[currentIndex + 1]
      if (nextRow) {
        setTimeout(() => inputRefs[nextRow.id]?.focus(), 80)
      } else {
        setTimeout(() => inputRefs.final?.focus(), 80)
      }
    }
  }

  const handleAddPartialProduct = (inputRefs: Record<string, HTMLInputElement | null>) => {
    if (mode !== 'normal') return
    const newId = `${partialProducts.length + 1}`
    const nextExpected = expectedPartials[partialProducts.length]?.expectedValue ?? 0
    const nextLabel = expectedPartials[partialProducts.length]?.promptLabel

    setPartialProducts((prev) => [
      ...prev,
      {
        id: newId,
        value: '',
        expectedValue: nextExpected,
        promptLabel: nextLabel,
      },
    ])

    setTimeout(() => inputRefs[newId]?.focus(), 120)
  }

  const handleRemovePartialProduct = (id: string) => {
    if (mode !== 'normal' || partialProducts.length === 1) return
    setPartialProducts((prev) => prev.filter((row) => row.id !== id))
  }

  const verify = () => {
    const userPartials = partialProducts.map((row) => Number(row.value) || 0).filter((val) => val > 0)
    const expectedValues = expectedPartials.map((entry) => entry.expectedValue)

    const userSorted = [...userPartials].sort((a, b) => a - b)
    const expectedSorted = [...expectedValues].sort((a, b) => a - b)
    const partialsMatch =
      userSorted.length === expectedSorted.length && userSorted.every((val, idx) => val === expectedSorted[idx])

    const userSum = userPartials.reduce((sum, value) => sum + value, 0)
    const sumCorrect = userSum === Number(question.correctAnswer)

    const finalCorrect = Number(finalAnswer) === Number(question.correctAnswer)

    const rowResults = partialProducts.map((row) => {
      const numericValue = Number(row.value) || 0
      if (numericValue === 0) return false
      return expectedValues.includes(numericValue)
    })

    setPartialProducts((prev) =>
      prev.map((row, index) => ({
        ...row,
        isCorrect: rowResults[index],
      })),
    )

    setShowAnswer(true)

    let message = ''
    if (partialsMatch && finalCorrect) {
      setFeedback('correct')
      message = '🎉 Perfect work! Every partial product and the final answer are correct.'
    } else if (partialsMatch && !finalCorrect) {
      setFeedback('partial')
      message = '👍 Partial products look great. Re-check the addition for the final answer.'
    } else if (!partialsMatch && finalCorrect) {
      setFeedback('partial')
      message = '👍 Final answer is correct. Review the partial products to show your work.'
    } else if (sumCorrect && !finalCorrect) {
      setFeedback('partial')
      message = '👍 Partial products add up correctly. Make sure the final answer matches your sum.'
    } else {
      setFeedback('incorrect')
      message = "❌ Let's review your work. Check each row carefully."
    }

    setVerificationResults({
      partialProducts: rowResults,
      finalAnswer: finalCorrect,
      message,
    })

    if (partialsMatch && finalCorrect && onComplete) {
      setTimeout(() => onComplete(true), 1200)
    }
  }

  const reset = (inputRefs: Record<string, HTMLInputElement | null>) => {
    setPartialProducts((prev) =>
      prev.map((row) => ({
        ...row,
        value: '',
        isCorrect: undefined,
      })),
    )
    setFinalAnswer('')
    setFeedback(null)
    setShowAnswer(false)
    setVerificationResults(null)

    setTimeout(() => inputRefs['1']?.focus(), 120)
  }

  const allowRowManagement = mode === 'normal'

  return {
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
  }
}

