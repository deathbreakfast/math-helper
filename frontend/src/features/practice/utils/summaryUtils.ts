export const getOperationSymbol = (operation: string): string => {
  switch (operation) {
    case 'addition':
      return '+'
    case 'subtraction':
      return '-'
    case 'multiplication':
      return '×'
    case 'division':
      return '÷'
    default:
      return '?'
  }
}

export const getOperationColor = (operation: string): string => {
  switch (operation) {
    case 'addition':
      return 'text-blue-600 bg-blue-50'
    case 'subtraction':
      return 'text-purple-600 bg-purple-50'
    case 'multiplication':
      return 'text-green-600 bg-green-50'
    case 'division':
      return 'text-orange-600 bg-orange-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export const parsePrompt = (
  prompt: string,
): { operand1: number; operand2: number; operation: 'addition' | 'subtraction' | 'multiplication' | 'division' } => {
  // Try to parse prompts like "5 + 3" or "What is 5 + 3?"
  const match = prompt.match(/(\d+)\s*([+\-×÷x*])\s*(\d+)/i)
  if (match) {
    const [, op1, symbol, op2] = match
    let operation: 'addition' | 'subtraction' | 'multiplication' | 'division' = 'addition'
    if (symbol === '+' || symbol.toLowerCase() === 'plus') operation = 'addition'
    else if (symbol === '-' || symbol.toLowerCase() === 'minus') operation = 'subtraction'
    else if (symbol === '×' || symbol === '*' || symbol.toLowerCase() === 'x' || symbol.toLowerCase() === 'times')
      operation = 'multiplication'
    else if (symbol === '÷' || symbol === '/' || symbol.toLowerCase() === 'divided') operation = 'division'
    return { operand1: Number(op1), operand2: Number(op2), operation }
  }
  // Fallback
  return { operand1: 0, operand2: 0, operation: 'addition' as const }
}

export const getEncouragementMessage = (accuracy: number): string => {
  if (accuracy === 100) return "🎉 Perfect Score! Outstanding work!"
  if (accuracy >= 90) return "🌟 Excellent job! You're doing great!"
  if (accuracy >= 80) return "👍 Great work! Keep it up!"
  if (accuracy >= 70) return "💪 Good effort! You're improving!"
  if (accuracy >= 60) return "📚 Keep practicing! You're getting there!"
  return "🎯 Keep trying! Practice makes perfect!"
}

