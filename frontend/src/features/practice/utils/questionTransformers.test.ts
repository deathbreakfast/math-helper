import { describe, it, expect } from 'vitest'
import { transformBackendQuestionsToPracticeQuestions } from './questionTransformers'

describe('questionTransformers', () => {
  describe('transformBackendQuestionsToPracticeQuestions', () => {
    it('should transform basic backend question format', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: '2 + 2',
          operation: 'addition',
          operand1: 2,
          operand2: 2,
          correct_answer: '4',
          difficulty: 'Level 1',
          target_ms: 4000,
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result).toHaveLength(1)
      expect(result[0]).toEqual({
        id: 1,
        prompt: '2 + 2',
        operation: 'addition',
        operand1: 2,
        operand2: 2,
        correctAnswer: '4',
        difficulty: 'Level 1',
        targetMs: 4000,
        hint: '',
        layout: undefined,
        question_id: 1,
      })
    })

    it('should handle camelCase fields', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: '3 + 3',
          correctAnswer: '6',
          targetMs: 5000,
          answerFormat: 'number',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].correctAnswer).toBe('6')
      expect(result[0].targetMs).toBe(5000)
      expect(result[0].answerFormat).toBe('number')
    })

    it('should handle snake_case fields', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: '4 + 4',
          correct_answer: '8',
          target_ms: 6000,
          answer_format: 'number',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].correctAnswer).toBe('8')
      expect(result[0].targetMs).toBe(6000)
      expect(result[0].answerFormat).toBe('number')
    })

    it('should generate id from question_id if id is missing', () => {
      const backendQuestions = [
        {
          question_id: 42,
          prompt: 'Test',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].id).toBe('q-42')
      expect(result[0].question_id).toBe(42)
    })

    it('should handle layout as JSON string', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: 'Test',
          layout: '{"type":"horizontal"}',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].layout).toEqual({ type: 'horizontal' })
    })

    it('should handle layout as object', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: 'Test',
          layout: { type: 'vertical', columns: 2 },
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].layout).toEqual({ type: 'vertical', columns: 2 })
    })

    it('should handle invalid JSON layout gracefully', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: 'Test',
          layout: 'invalid json',
          layout_type: 'vertical',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].layout).toEqual({ type: 'vertical' })
    })

    it('should use layout_type if layout is missing', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: 'Test',
          layout_type: 'horizontal',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].layout).toEqual({ type: 'horizontal' })
    })

    it('should provide default values for missing fields', () => {
      const backendQuestions = [
        {
          question_id: 1,
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0]).toMatchObject({
        prompt: '',
        operation: 'addition',
        operand1: 0,
        operand2: 0,
        correctAnswer: '',
        difficulty: 'Level 1',
        targetMs: 4000,
        hint: '',
      })
    })

    it('should handle multiple questions', () => {
      const backendQuestions = [
        { id: 1, question_id: 1, prompt: 'Question 1', correct_answer: '1' },
        { id: 2, question_id: 2, prompt: 'Question 2', correct_answer: '2' },
        { id: 3, question_id: 3, prompt: 'Question 3', correct_answer: '3' },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result).toHaveLength(3)
      expect(result.map((q) => q.prompt)).toEqual(['Question 1', 'Question 2', 'Question 3'])
    })

    it('should handle empty array', () => {
      const result = transformBackendQuestionsToPracticeQuestions([], 'standard')
      expect(result).toEqual([])
    })

    it('should handle optional fields', () => {
      const backendQuestions = [
        {
          id: 1,
          question_id: 1,
          prompt: 'Test',
          acceptedAnswers: ['6', 'six'],
          decimalPlaces: 2,
          mathTypeLabel: 'Addition',
        },
      ]

      const result = transformBackendQuestionsToPracticeQuestions(backendQuestions, 'standard')

      expect(result[0].acceptedAnswers).toEqual(['6', 'six'])
      expect(result[0].decimalPlaces).toBe(2)
      expect(result[0].mathTypeLabel).toBe('Addition')
    })
  })
})



