import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { usePracticeState } from './usePracticeState'

describe('usePracticeState', () => {
  it('should initialize with default state', () => {
    const { result } = renderHook(() => usePracticeState())

    expect(result.current.state.problems).toEqual([])
    expect(result.current.state.currentQuestionIndex).toBe(0)
    expect(result.current.state.userAnswer).toBe('')
    expect(result.current.state.feedback).toBeNull()
    expect(result.current.state.showAnswer).toBe(false)
    expect(result.current.state.flaggedQuestions).toEqual({})
    expect(result.current.state.questionAnswers).toEqual({})
    expect(result.current.state.questionStartTimes).toEqual({})
    expect(result.current.state.sessionId).toBeNull()
    expect(result.current.state.sessionMode).toBe('standard') // Default is 'standard'
    expect(result.current.state.sessionError).toBeNull()
    expect(result.current.state.isLoadingProblems).toBe(false)
  })

  it('should update problems', () => {
    const { result } = renderHook(() => usePracticeState())

    const problems = [
      {
        id: '1',
        prompt: '2 + 2',
        operation: 'addition' as const,
        operand1: 2,
        operand2: 2,
        correctAnswer: '4',
        difficulty: 'Level 1',
        targetMs: 4000,
      },
    ]

    act(() => {
      result.current.actions.setProblems(problems)
    })

    expect(result.current.state.problems).toEqual(problems)
  })

  it('should update currentQuestionIndex', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setCurrentQuestionIndex(5)
    })

    expect(result.current.state.currentQuestionIndex).toBe(5)
  })

  it('should update userAnswer', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setUserAnswer('42')
    })

    expect(result.current.state.userAnswer).toBe('42')
  })

  it('should update feedback', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setFeedback('correct')
    })

    expect(result.current.state.feedback).toBe('correct')

    act(() => {
      result.current.actions.setFeedback('incorrect')
    })

    expect(result.current.state.feedback).toBe('incorrect')

    act(() => {
      result.current.actions.setFeedback(null)
    })

    expect(result.current.state.feedback).toBeNull()
  })

  it('should update showAnswer', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setShowAnswer(true)
    })

    expect(result.current.state.showAnswer).toBe(true)

    act(() => {
      result.current.actions.setShowAnswer(false)
    })

    expect(result.current.state.showAnswer).toBe(false)
  })

  it('should update flaggedQuestions with object', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setFlaggedQuestions({ '1': true, '2': false })
    })

    expect(result.current.state.flaggedQuestions).toEqual({ '1': true, '2': false })
  })

  it('should update flaggedQuestions with function', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setFlaggedQuestions({ '1': true })
    })

    act(() => {
      result.current.actions.setFlaggedQuestions((prev) => ({ ...prev, '2': true }))
    })

    expect(result.current.state.flaggedQuestions).toEqual({ '1': true, '2': true })
  })

  it('should update questionAnswers with object', () => {
    const { result } = renderHook(() => usePracticeState())

    const answers = {
      '1': {
        answer: '4',
        isChecked: true,
        feedback: 'correct' as const,
        elapsedMs: 2000,
      },
    }

    act(() => {
      result.current.actions.setQuestionAnswers(answers)
    })

    expect(result.current.state.questionAnswers).toEqual(answers)
  })

  it('should update questionAnswers with function', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setQuestionAnswers({
        '1': {
          answer: '4',
          isChecked: true,
          feedback: 'correct',
        },
      })
    })

    act(() => {
      result.current.actions.setQuestionAnswers((prev) => ({
        ...prev,
        '2': {
          answer: '6',
          isChecked: true,
          feedback: 'correct',
        },
      }))
    })

    expect(result.current.state.questionAnswers).toHaveProperty('1')
    expect(result.current.state.questionAnswers).toHaveProperty('2')
  })

  it('should update questionStartTimes', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setQuestionStartTimes({ '1': 1000, '2': 2000 })
    })

    expect(result.current.state.questionStartTimes).toEqual({ '1': 1000, '2': 2000 })
  })

  it('should update sessionId', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setSessionId(123)
    })

    expect(result.current.state.sessionId).toBe(123)

    act(() => {
      result.current.actions.setSessionId(null)
    })

    expect(result.current.state.sessionId).toBeNull()
  })

  it('should update sessionMode', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setSessionMode('multiplication')
    })

    expect(result.current.state.sessionMode).toBe('multiplication')
  })

  it('should update sessionError', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setSessionError('Something went wrong')
    })

    expect(result.current.state.sessionError).toBe('Something went wrong')

    act(() => {
      result.current.actions.setSessionError(null)
    })

    expect(result.current.state.sessionError).toBeNull()
  })

  it('should update isLoadingProblems', () => {
    const { result } = renderHook(() => usePracticeState())

    act(() => {
      result.current.actions.setIsLoadingProblems(true)
    })

    expect(result.current.state.isLoadingProblems).toBe(true)

    act(() => {
      result.current.actions.setIsLoadingProblems(false)
    })

    expect(result.current.state.isLoadingProblems).toBe(false)
  })

  it('should reset state to initial values', () => {
    const { result } = renderHook(() => usePracticeState())

    // Set some state
    act(() => {
      result.current.actions.setProblems([
        {
          id: '1',
          prompt: '2 + 2',
          operation: 'addition' as const,
          operand1: 2,
          operand2: 2,
          correctAnswer: '4',
          difficulty: 'Level 1',
          targetMs: 4000,
        },
      ])
      result.current.actions.setCurrentQuestionIndex(5)
      result.current.actions.setUserAnswer('42')
      result.current.actions.setSessionId(123)
    })

    // Reset
    act(() => {
      result.current.actions.resetState()
    })

    expect(result.current.state.problems).toEqual([])
    expect(result.current.state.currentQuestionIndex).toBe(0)
    expect(result.current.state.userAnswer).toBe('')
    expect(result.current.state.feedback).toBeNull()
    expect(result.current.state.showAnswer).toBe(false)
    expect(result.current.state.flaggedQuestions).toEqual({})
    expect(result.current.state.questionAnswers).toEqual({})
    expect(result.current.state.questionStartTimes).toEqual({})
    expect(result.current.state.sessionId).toBeNull()
    expect(result.current.state.sessionMode).toBe('standard')
    expect(result.current.state.sessionError).toBeNull()
    expect(result.current.state.isLoadingProblems).toBe(false)
  })
})


