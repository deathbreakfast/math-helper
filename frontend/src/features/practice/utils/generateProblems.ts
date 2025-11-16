import type { AnswerMode, Operation, PracticeQuestion } from '../types'

const OPERATIONS: Operation[] = ['addition', 'subtraction', 'multiplication', 'division']

const getOperationSymbol = (operation: Operation) => {
  switch (operation) {
    case 'addition':
      return '+'
    case 'subtraction':
      return '-'
    case 'multiplication':
      return '×'
    case 'division':
      return '÷'
  }
}

const solve = (operation: Operation, a: number, b: number) => {
  switch (operation) {
    case 'addition':
      return a + b
    case 'subtraction':
      return a - b
    case 'multiplication':
      return a * b
    case 'division':
      return Math.floor(a / b)
  }
}

const DEFAULT_MATH_TYPE_LABELS: Record<Operation, string> = {
  addition: 'Addition (Standard)',
  subtraction: 'Subtraction (Standard)',
  multiplication: 'Multiplication (Standard)',
  division: 'Division (Standard)',
}

type MultiplicationVariant = 'standard' | 'partialEasy' | 'partialNormal'

const MULTIPLICATION_VARIANTS: MultiplicationVariant[] = [
  'standard',
  'standard',
  'standard',
  'standard',
  'partialEasy',
  'partialEasy',
  'partialNormal',
  'partialNormal',
  'partialEasy',
  'partialNormal',
]

const createMultiplicationQuestion = (
  variant: MultiplicationVariant,
  index: number,
): PracticeQuestion => {
  const operand1 =
    variant === 'standard' ? Math.floor(Math.random() * 12) + 1 : Math.floor(Math.random() * 90) + 10
  const operand2 =
    variant === 'standard'
      ? Math.floor(Math.random() * 12) + 1
      : variant === 'partialEasy'
        ? Math.floor(Math.random() * 8) + 2
        : Math.floor(Math.random() * 90) + 10

  const layout =
    variant === 'standard'
      ? { type: 'vertical' as const }
      : {
          type: 'partialProducts' as const,
          showWork: true,
          partialProductsMode: (variant === 'partialEasy' ? 'easy' : 'normal') as 'easy' | 'normal',
        }

  const mathTypeLabel =
    variant === 'standard'
      ? 'Multiplication • Normal Up To 12 × 12'
      : variant === 'partialEasy'
        ? 'Multiplication • Partial Products (Easy)'
        : 'Multiplication • Partial Products (Normal)'

  const hint =
    variant === 'standard'
      ? 'Stack the digits and carry when needed.'
      : variant === 'partialEasy'
        ? 'Break the multiplier into ones and tens. Fill each row before you add.'
        : 'Add rows for every digit in the multiplier, then total the partial products.'

  return {
    id: `3-${variant}-${index}`,
    prompt: `${operand1} ${getOperationSymbol('multiplication')} ${operand2}`,
    operation: 'multiplication',
    operand1,
    operand2,
    correctAnswer: solve('multiplication', operand1, operand2).toString(),
    difficulty: 'Level 3',
    targetMs: 4000 + 3 * 500,
    hint,
    layout,
    answerFormat: 'integer',
    mathTypeLabel,
  }
}

export const generateMultiplicationShowcase = (count = 10): PracticeQuestion[] => {
  const problems: PracticeQuestion[] = []
  for (let i = 0; i < count; i += 1) {
    const variant = MULTIPLICATION_VARIANTS[i % MULTIPLICATION_VARIANTS.length]
    problems.push(createMultiplicationQuestion(variant, i))
  }
  return problems
}

const createFormatDistribution = (count: number): AnswerMode[] => {
  const formatDistribution: AnswerMode[] = []
  
  // Create a varied distribution: ~40% remainder, ~30% fraction, ~30% decimal
  const remainderCount = Math.ceil(count * 0.4)
  const fractionCount = Math.ceil(count * 0.3)
  const decimalCount = count - remainderCount - fractionCount
  
  formatDistribution.push(...Array(remainderCount).fill('remainder'))
  formatDistribution.push(...Array(fractionCount).fill('fraction'))
  formatDistribution.push(...Array(decimalCount).fill('decimal'))
  
  // Shuffle the distribution for variety
  for (let i = formatDistribution.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [formatDistribution[i], formatDistribution[j]] = [formatDistribution[j], formatDistribution[i]]
  }
  
  return formatDistribution
}

const createDivisionQuestion = (index: number, answerMode?: AnswerMode): PracticeQuestion => {
  const divisor = Math.floor(Math.random() * 11) + 2
  const quotient = Math.floor(Math.random() * 11) + 2
  const dividend = divisor * quotient

  const formats: AnswerMode[] = ['remainder', 'fraction', 'decimal']
  const selectedFormat: AnswerMode = answerMode ?? formats[index % formats.length]
  const formatLabel = selectedFormat.charAt(0).toUpperCase() + selectedFormat.slice(1)

  return {
    id: `4-division-${index}`,
    prompt: `${dividend} ${getOperationSymbol('division')} ${divisor}`,
    operation: 'division',
    operand1: dividend,
    operand2: divisor,
    correctAnswer: quotient.toString(),
    difficulty: 'Level 4',
    targetMs: 4000 + 4 * 500,
    hint: 'Use the long division algorithm: divide, multiply, subtract, bring down.',
    layout: {
      type: 'longDivision',
      notice: {
        tone: 'orange',
        icon: 'lightbulb',
        title: 'Long Division',
        body: `Use the long division algorithm to solve ${dividend} ÷ ${divisor}.`,
      },
      tip: {
        icon: 'lightbulb',
        title: 'Long Division Tip',
        body: 'Remember the cycle: Divide, Multiply, Subtract, then Bring Down the next digit.',
      },
      answerFormats: [selectedFormat],
    },
    answerFormat: selectedFormat === 'remainder' ? 'remainder' : selectedFormat === 'fraction' ? 'fraction' : 'decimal',
    mathTypeLabel: `Division • Long Division • ${formatLabel}`,
  }
}

export const generateDivisionShowcase = (count = 10): PracticeQuestion[] => {
  const problems: PracticeQuestion[] = []
  const formatDistribution = createFormatDistribution(count)
  
  for (let i = 0; i < count; i += 1) {
    problems.push(createDivisionQuestion(i, formatDistribution[i]))
  }
  return problems
}

export const generateProblems = (level: number, count = 10): PracticeQuestion[] => {
  const problems: PracticeQuestion[] = []

  if (level === 3) {
    return generateMultiplicationShowcase(count)
  }

  // Pre-generate format distribution for division questions if needed
  const hasDivision = level >= 4
  const formatDistribution = hasDivision ? createFormatDistribution(count) : null
  let divisionIndex = 0 // Track which division question we're on

  for (let i = 0; i < count; i += 1) {
    let operation: Operation = 'addition'
    let operand1 = 0
    let operand2 = 0

    if (level === 1) {
      operation = Math.random() > 0.5 ? 'addition' : 'subtraction'
      operand1 = Math.floor(Math.random() * 9) + 1
      operand2 = Math.floor(Math.random() * 9) + 1
    } else if (level === 2) {
      operation = Math.random() > 0.5 ? 'addition' : 'subtraction'
      operand1 = Math.floor(Math.random() * 90) + 10
      operand2 = Math.floor(Math.random() * 90) + 10
    } else if (level === 3) {
      operation = 'multiplication'
      operand1 = Math.floor(Math.random() * 12) + 1
      operand2 = Math.floor(Math.random() * 12) + 1
    } else if (level === 4) {
      operation = 'division'
      operand2 = Math.floor(Math.random() * 12) + 1
      const quotient = Math.floor(Math.random() * 12) + 1
      operand1 = operand2 * quotient
    } else {
      operation = OPERATIONS[Math.floor(Math.random() * OPERATIONS.length)]
      operand1 = Math.floor(Math.random() * 50) + 1
      operand2 = Math.floor(Math.random() * 12) + 1
      if (operation === 'division') {
        operand1 = operand2 * (Math.floor(Math.random() * 12) + 1)
      }
    }

    const prompt = `${operand1} ${getOperationSymbol(operation)} ${operand2}`
    let layout: PracticeQuestion['layout'] = {
      type: 'vertical',
    }
    let mathTypeLabel: string = DEFAULT_MATH_TYPE_LABELS[operation]
    let hint = 'Stack the digits and carry if needed.'
    let answerFormat: PracticeQuestion['answerFormat'] = 'integer'

    if (operation === 'division' && level >= 4 && formatDistribution) {
      const answerMode: AnswerMode = formatDistribution[divisionIndex]
      const formatLabel = answerMode.charAt(0).toUpperCase() + answerMode.slice(1)
      mathTypeLabel = `Division • Long Division • ${formatLabel}`
      hint = 'Use the long division algorithm: divide, multiply, subtract, bring down.'
      answerFormat = answerMode === 'remainder' ? 'remainder' : answerMode === 'fraction' ? 'fraction' : 'decimal'
      layout = {
        type: 'longDivision',
        notice: {
          tone: 'orange',
          icon: 'lightbulb',
          title: 'Long Division',
          body: `Use the long division algorithm to solve ${operand1} ÷ ${operand2}.`,
        },
        tip: {
          icon: 'lightbulb',
          title: 'Long Division Tip',
          body: 'Remember the cycle: Divide, Multiply, Subtract, then Bring Down the next digit.',
        },
        answerFormats: [answerMode],
      }
      divisionIndex += 1
    }

    problems.push({
      id: `${level}-${i}`,
      operation,
      operand1,
      operand2,
      prompt,
      correctAnswer: solve(operation, operand1, operand2).toString(),
      difficulty: `Level ${level}`,
      targetMs: 4000 + level * 500,
      hint,
      layout,
      answerFormat,
      mathTypeLabel,
    })
  }

  return problems
}

