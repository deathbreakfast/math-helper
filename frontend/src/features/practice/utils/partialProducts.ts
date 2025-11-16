import type { PracticeQuestion, PartialProductsMode } from '../types'

export type ExpectedPartial = {
  expectedValue: number
  promptLabel?: string
}

export const buildExpectedPartials = (question: PracticeQuestion, mode: PartialProductsMode): ExpectedPartial[] => {
  const { operand1, operand2 } = question

  if (mode === 'easy') {
    const digits = operand1
      .toString()
      .split('')
      .reverse()
      .map((value) => Number(value))

    const rows: ExpectedPartial[] = []

    digits.forEach((digit, index) => {
      if (digit === 0) return
      const placeValue = digit * Math.pow(10, index)
      rows.push({
        expectedValue: placeValue * operand2,
        promptLabel: `${operand2} × ${placeValue}`,
      })
    })

    if (rows.length === 0) {
      rows.push({
        expectedValue: operand1 * operand2,
        promptLabel: `${operand2} × ${operand1}`,
      })
    }

    return rows
  }

  const digits = operand2
    .toString()
    .split('')
    .reverse()
    .map((value) => Number(value))

  const rows: ExpectedPartial[] = []

  digits.forEach((digit, index) => {
    if (digit === 0) return
    rows.push({
      expectedValue: operand1 * digit * Math.pow(10, index),
    })
  })

  if (rows.length === 0) {
    rows.push({ expectedValue: operand1 * operand2 })
  }

  return rows
}

