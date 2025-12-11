import { describe, it, expect, vi, beforeEach } from 'vitest'
import { server } from '../../../test-utils/mocks/server'
import { http, HttpResponse } from 'msw'
import {
  startSession,
  checkAnswer,
  completeSession,
  createSessionSummary,
  type StartSessionParams,
  type CheckAnswerParams,
  type CompleteSessionParams,
} from './usePracticeAPI'
import type { User } from '../types'

describe('usePracticeAPI', () => {
  const mockUser: User = {
    id: 1,
    name: 'Test User',
    avatar: '👧',
    level: 1,
    questionsAnswered: 0,
    averageSpeed: 0,
    stats: {
      currentStreak: 0,
      bestStreak: 0,
      additionAccuracy: 0,
      subtractionAccuracy: 0,
      multiplicationAccuracy: 0,
      divisionAccuracy: 0,
      additionSpeed: 0,
      subtractionSpeed: 0,
      multiplicationSpeed: 0,
      divisionSpeed: 0,
    },
    achievements: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('startSession', () => {
    it('should start a new session successfully', async () => {
      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'standard',
        searchParams: new URLSearchParams(),
      }

      const result = await startSession(params)

      expect(result.sessionId).toBeDefined()
      expect(result.sessionMode).toBe('standard')
      expect(result.sessionState.problems).toHaveLength(2)
      expect(result.sessionState.questionAnswers).toEqual({})
      expect(result.sessionState.currentQuestionIndex).toBe(0)
    })

    it('should handle multiplication mode', async () => {
      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'multiplication',
        searchParams: new URLSearchParams(),
      }

      const result = await startSession(params)

      expect(result.sessionMode).toBe('multiplication')
    })

    it('should handle division mode', async () => {
      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'division',
        searchParams: new URLSearchParams(),
      }

      const result = await startSession(params)

      expect(result.sessionMode).toBe('division')
    })

    it('should handle test mode from URL params', async () => {
      const searchParams = new URLSearchParams()
      searchParams.set('isTest', 'true')
      searchParams.set('testType', 'addition-1digit')

      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'standard',
        searchParams,
      }

      const result = await startSession(params)

      expect(result.sessionState).toBeDefined()
    })

    it('should handle API errors', async () => {
      server.use(
        http.post('/api/practice/sessions/start', () => {
          return HttpResponse.json({ error: 'Failed to create session' }, { status: 500 })
        })
      )

      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'standard',
        searchParams: new URLSearchParams(),
      }

      await expect(startSession(params)).rejects.toThrow('Failed to create session')
    })

    it('should handle network errors', async () => {
      server.use(
        http.post('/api/practice/sessions/start', () => {
          return HttpResponse.error()
        })
      )

      const params: StartSessionParams = {
        selectedUser: mockUser,
        practiceMode: 'standard',
        searchParams: new URLSearchParams(),
      }

      await expect(startSession(params)).rejects.toThrow()
    })
  })

  describe('checkAnswer', () => {
    it('should check answer successfully', async () => {
      const params: CheckAnswerParams = {
        sessionId: 1,
        questionId: 1,
        submittedAnswer: '4',
        durationMs: 2000,
      }

      const result = await checkAnswer(params)

      expect(result.is_correct).toBeDefined()
      expect(typeof result.is_correct).toBe('boolean')
    })

    it('should handle string question IDs', async () => {
      const params: CheckAnswerParams = {
        sessionId: 1,
        questionId: '1',
        submittedAnswer: '4',
        durationMs: 2000,
      }

      const result = await checkAnswer(params)

      expect(result.is_correct).toBeDefined()
    })

    it('should handle API errors', async () => {
      server.use(
        http.post('/api/practice/questions/check', () => {
          return HttpResponse.json({ error: 'Failed to check answer' }, { status: 500 })
        })
      )

      const params: CheckAnswerParams = {
        sessionId: 1,
        questionId: 1,
        submittedAnswer: '4',
        durationMs: 2000,
      }

      await expect(checkAnswer(params)).rejects.toThrow()
    })
  })

  describe('completeSession', () => {
    it('should complete session successfully', async () => {
      const params: CompleteSessionParams = {
        sessionId: 1,
        totalDurationMs: 60000,
      }

      const result = await completeSession(params)

      expect(result.session).toBeDefined()
      expect(result.session.id).toBeDefined()
      expect(result.session.completed_at).toBeDefined()
      expect(result.session.total_questions).toBe(2)
      expect(result.session.correct_count).toBe(2)
      expect(result.session.accuracy).toBe(100)
    })

    it('should handle level up response', async () => {
      server.use(
        http.post('/api/practice/sessions/:sessionId/complete', () => {
          return HttpResponse.json({
            session: {
              id: 1,
              completed_at: new Date().toISOString(),
              total_questions: 2,
              correct_count: 2,
              accuracy: 100,
            },
            level_up: {
              new_level: 2,
            },
            achievements: [],
          })
        })
      )

      const params: CompleteSessionParams = {
        sessionId: 1,
        totalDurationMs: 60000,
      }

      const result = await completeSession(params)

      expect(result.level_up).toBeDefined()
      expect(result.level_up?.new_level).toBe(2)
    })

    it('should handle achievements response', async () => {
      server.use(
        http.post('/api/practice/sessions/:sessionId/complete', () => {
          return HttpResponse.json({
            session: {
              id: 1,
              completed_at: new Date().toISOString(),
              total_questions: 2,
              correct_count: 2,
              accuracy: 100,
            },
            achievements: [
              {
                id: 'achievement-1',
                code: 'first-steps',
                title: 'First Steps',
              },
            ],
          })
        })
      )

      const params: CompleteSessionParams = {
        sessionId: 1,
        totalDurationMs: 60000,
      }

      const result = await completeSession(params)

      expect(result.achievements).toBeDefined()
      expect(result.achievements?.length).toBe(1)
      expect(result.achievements?.[0].code).toBe('first-steps')
    })

    it('should handle API errors', async () => {
      server.use(
        http.post('/api/practice/sessions/:sessionId/complete', () => {
          return HttpResponse.json({ error: 'Failed to complete session' }, { status: 500 })
        })
      )

      const params: CompleteSessionParams = {
        sessionId: 1,
        totalDurationMs: 60000,
      }

      await expect(completeSession(params)).rejects.toThrow()
    })
  })

  describe('createSessionSummary', () => {
    it('should create session summary from complete result', () => {
      const completeResult = {
        session: {
          id: 1,
          completed_at: '2024-01-01T00:00:00Z',
          total_questions: 3,
          correct_count: 2,
          accuracy: 67,
        },
        achievements: [
          {
            code: 'first-steps',
            title: 'First Steps',
          },
        ],
      }

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
          question_id: 1,
        },
        {
          id: '2',
          prompt: '3 + 3',
          operation: 'addition' as const,
          operand1: 3,
          operand2: 3,
          correctAnswer: '6',
          difficulty: 'Level 1',
          targetMs: 4000,
          question_id: 2,
        },
      ]

      const questionAnswers = {
        '1': {
          answer: '4',
          isChecked: true,
          feedback: 'correct' as const,
          elapsedMs: 2000,
        },
        '2': {
          answer: '7',
          isChecked: true,
          feedback: 'incorrect' as const,
          elapsedMs: 3000,
        },
      }

      const summary = createSessionSummary(completeResult, problems, questionAnswers, mockUser)

      expect(summary.id).toBe('1')
      expect(summary.status).toBe('completed')
      expect(summary.totals.questions).toBe(3)
      expect(summary.totals.correct).toBe(2)
      expect(summary.totals.accuracy).toBe(67)
      expect(summary.attempts).toHaveLength(2)
      expect(summary.achievements).toHaveLength(1)
      expect(summary.user.id).toBe(mockUser.id)
      expect(summary.user.name).toBe(mockUser.name)
    })

    it('should handle missing session data', () => {
      const completeResult = {
        session: {},
      }

      const problems = []
      const questionAnswers = {}

      const summary = createSessionSummary(completeResult, problems, questionAnswers, mockUser)

      expect(summary.id).toMatch(/^session-\d+$/)
      expect(summary.totals.questions).toBe(0)
      expect(summary.totals.correct).toBe(0)
    })

    it('should calculate accuracy from session data', () => {
      const completeResult = {
        session: {
          total_questions: 10,
          correct_count: 8,
        },
      }

      const problems = []
      const questionAnswers = {}

      const summary = createSessionSummary(completeResult, problems, questionAnswers, mockUser)

      expect(summary.totals.accuracy).toBe(80)
    })

    it('should handle level up data', () => {
      const completeResult = {
        session: {
          id: 1,
          completed_at: '2024-01-01T00:00:00Z',
        },
        level_up: {
          new_level: 2,
        },
      }

      const problems = []
      const questionAnswers = {}

      const summary = createSessionSummary(completeResult, problems, questionAnswers, mockUser)

      expect(summary.level_up?.new_level).toBe(2)
      expect(summary.user.level).toBe(2)
    })
  })
})


