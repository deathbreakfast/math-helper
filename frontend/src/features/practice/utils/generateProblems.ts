import type { Operation, PracticeQuestion } from '../types'

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

export const generateProblems = (level: number, count = 10): PracticeQuestion[] => {
  const problems: PracticeQuestion[] = []

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
    problems.push({
      id: `${level}-${i}`,
      operation,
      operand1,
      operand2,
      prompt,
      correctAnswer: solve(operation, operand1, operand2).toString(),
      difficulty: `Level ${level}`,
      targetMs: 4000 + level * 500,
      hint: 'Stack the digits and carry if needed.',
      layout: {
        type: 'vertical',
      },
      answerFormat: 'integer',
    })
  }

  return problems
}

