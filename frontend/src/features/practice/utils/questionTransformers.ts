import type { PracticeQuestion } from '../types'

/**
 * Transform backend question format to frontend PracticeQuestion format.
 * Handles layout parsing (JSON string or object) and field mapping.
 */
export function transformBackendQuestionsToPracticeQuestions(
  backendQuestions: any[],
  sessionMode: string
): PracticeQuestion[] {
  return backendQuestions.map((q) => {
    // Handle layout config - may be JSON string or object
    let layout: PracticeQuestion['layout'] = undefined
    if (q.layout) {
      if (typeof q.layout === 'string') {
        try {
          layout = JSON.parse(q.layout)
        } catch {
          layout = { type: q.layout_type || 'vertical' }
        }
      } else {
        layout = q.layout
      }
    } else if (q.layout_type) {
      layout = { type: q.layout_type }
    }

    return {
      id: q.id || `q-${q.question_id}`,
      prompt: q.prompt || '',
      operation: q.operation || 'addition',
      operand1: q.operand1 || 0,
      operand2: q.operand2 || 0,
      correctAnswer: q.correctAnswer || q.correct_answer || '',
      difficulty: q.difficulty || 'Level 1',
      targetMs: q.targetMs || q.target_ms || 4000,
      hint: q.hint || '',
      layout,
      answerFormat: q.answerFormat || q.answer_format,
      acceptedAnswers: q.acceptedAnswers || q.accepted_answers,
      decimalPlaces: q.decimalPlaces || q.decimal_places,
      mathTypeLabel: q.mathTypeLabel || q.math_type_label,
      question_id: q.question_id || q.id,
    }
  })
}





