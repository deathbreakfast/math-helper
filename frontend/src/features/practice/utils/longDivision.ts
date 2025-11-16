export type DivisionStepType = 'divide' | 'multiply' | 'subtract' | 'bringDown'

export type DivisionStep = {
  id: string
  stepType: DivisionStepType
  value: string
  expectedValue: number | null
  isCorrect?: boolean
}

export const buildDivisionSteps = (dividend: number, divisor: number): DivisionStep[] => {
  const dividendStr = dividend.toString()
  const steps: DivisionStep[] = []
  let workingDividend = 0

  for (let index = 0; index < dividendStr.length; index += 1) {
    workingDividend = workingDividend * 10 + parseInt(dividendStr[index], 10)

    if (workingDividend >= divisor || index > 0) {
      const quotientDigit = Math.floor(workingDividend / divisor)
      const multiplyResult = quotientDigit * divisor
      const subtractResult = workingDividend - multiplyResult

      steps.push({
        id: `divide-${index}`,
        stepType: 'divide',
        value: '',
        expectedValue: quotientDigit,
      })
      steps.push({
        id: `multiply-${index}`,
        stepType: 'multiply',
        value: '',
        expectedValue: multiplyResult,
      })
      steps.push({
        id: `subtract-${index}`,
        stepType: 'subtract',
        value: '',
        expectedValue: subtractResult,
      })

      if (index < dividendStr.length - 1) {
        steps.push({
          id: `bringDown-${index}`,
          stepType: 'bringDown',
          value: '',
          expectedValue: parseInt(dividendStr[index + 1], 10),
        })
      }

      workingDividend = subtractResult
    }
  }

  return steps
}

export const calculateExpectedAnswers = (dividend: number, divisor: number) => {
  const expectedQuotient = Math.floor(dividend / divisor)
  const expectedRemainder = dividend % divisor
  const expectedDecimalString = (dividend / divisor).toFixed(2)
  const expectedDecimalPart = expectedDecimalString.split('.')[1] ?? '00'

  return {
    expectedQuotient,
    expectedRemainder,
    expectedDecimalPart,
  }
}

export const getAnswerDisplay = (dividend: number, divisor: number, answerMode: 'remainder' | 'fraction' | 'decimal') => {
  const { expectedQuotient, expectedRemainder } = calculateExpectedAnswers(dividend, divisor)

  switch (answerMode) {
    case 'fraction': {
      const fractionPart = expectedRemainder === 0 ? '' : ` ${expectedRemainder}/${divisor}`
      return `${expectedQuotient}${fractionPart}`
    }
    case 'decimal':
      return (dividend / divisor).toFixed(2)
    case 'remainder':
    default:
      return expectedRemainder === 0 ? `${expectedQuotient}` : `${expectedQuotient} R ${expectedRemainder}`
  }
}

