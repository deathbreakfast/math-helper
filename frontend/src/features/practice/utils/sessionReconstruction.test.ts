import { describe, it, expect } from 'vitest'
import { reconstructSessionStateFromResponse } from './sessionReconstruction'
import type { ReconstructedSessionState } from './sessionReconstruction'

describe('sessionReconstruction', () => {
  describe('reconstructSessionStateFromResponse', () => {
    it('should reconstruct state for new session with no answers', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            operation: 'addition',
            operand1: 2,
            operand2: 2,
            correct_answer: '4',
          },
          {
            id: 2,
            question_id: 2,
            prompt: '3 + 3',
            operation: 'addition',
            operand1: 3,
            operand2: 3,
            correct_answer: '6',
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.problems).toHaveLength(2)
      expect(result.questionAnswers).toEqual({})
      expect(result.currentQuestionIndex).toBe(0)
      expect(result.questionStartTimes).toEqual({})
      expect(result.flaggedQuestions).toEqual({})
    })

    it('should reconstruct state for incomplete session with some answers', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            operation: 'addition',
            operand1: 2,
            operand2: 2,
            correct_answer: '4',
            response: {
              submitted_answer: '4',
              is_correct: true,
              duration_ms: 2000,
            },
          },
          {
            id: 2,
            question_id: 2,
            prompt: '3 + 3',
            operation: 'addition',
            operand1: 3,
            operand2: 3,
            correct_answer: '6',
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.problems).toHaveLength(2)
      expect(result.questionAnswers).toHaveProperty('1')
      expect(result.questionAnswers['1']).toEqual({
        answer: '4',
        isChecked: true,
        feedback: 'correct',
        elapsedMs: 2000,
      })
      expect(result.currentQuestionIndex).toBe(1) // First unanswered question
    })

    it('should handle incorrect answers', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            correct_answer: '4',
            response: {
              submitted_answer: '5',
              is_correct: false,
              duration_ms: 1500,
            },
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.questionAnswers['1']).toEqual({
        answer: '5',
        isChecked: true,
        feedback: 'incorrect',
        elapsedMs: 1500,
      })
    })

    it('should set currentQuestionIndex to last question if all are answered', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            correct_answer: '4',
            response: {
              submitted_answer: '4',
              is_correct: true,
              duration_ms: 2000,
            },
          },
          {
            id: 2,
            question_id: 2,
            prompt: '3 + 3',
            correct_answer: '6',
            response: {
              submitted_answer: '6',
              is_correct: true,
              duration_ms: 1800,
            },
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.currentQuestionIndex).toBe(1) // Last question index
    })

    it('should handle missing response data', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            correct_answer: '4',
            response: {
              submitted_answer: '',
              is_correct: false,
            },
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.questionAnswers['1']).toEqual({
        answer: '',
        isChecked: true,
        feedback: 'incorrect',
        elapsedMs: undefined,
      })
    })

    it('should handle empty questions array', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.problems).toEqual([])
      expect(result.questionAnswers).toEqual({})
      expect(result.currentQuestionIndex).toBe(0)
    })

    it('should handle missing questions property', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.problems).toEqual([])
      expect(result.questionAnswers).toEqual({})
      expect(result.currentQuestionIndex).toBe(0)
    })

    it('should use default mode if not provided', () => {
      const responseData = {
        session_id: 1,
        questions: [
          {
            id: 1,
            question_id: 1,
            prompt: '2 + 2',
            correct_answer: '4',
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      expect(result.problems).toHaveLength(1)
    })

    it('should match questions by question_id or id', () => {
      const responseData = {
        session_id: 1,
        mode: 'standard',
        questions: [
          {
            id: 100,
            question_id: 42,
            prompt: '2 + 2',
            correct_answer: '4',
            response: {
              submitted_answer: '4',
              is_correct: true,
              duration_ms: 2000,
            },
          },
        ],
      }

      const result = reconstructSessionStateFromResponse(responseData)

      // Should find the question by question_id (42) and match it
      expect(result.problems).toHaveLength(1)
      // The question should have the transformed id
      const questionId = result.problems[0].id
      expect(result.questionAnswers[questionId]).toBeDefined()
    })
  })
})


