import { test, expect } from './fixtures/test-user'
import {
  startTestSession,
  answerQuestionViaAPI,
  scenario,
} from './helpers/test-helpers'

test.describe('Test Flow', () => {

  test('TEST-003: Test submission', async ({ page, request }) => {
    // Create user at level 1 with 3 completed practice sessions (for eligibility)
    const context = await scenario()
      .withUser({ level: 1 })
      .withCompletedSessions(1, 3)
      .build(request)
    
    try {
      // Start test session via API
      const testSession = await startTestSession(request, context.user.id, 'addition-1digit')
      expect(testSession.session_id).toBeDefined()
      expect(testSession.questions).toBeDefined()
      expect(testSession.questions.length).toBeGreaterThan(0)
      
      const sessionId = testSession.session_id
      const questions = testSession.questions
      
      // Answer questions via API
      for (const question of questions) {
        await answerQuestionViaAPI(
          request,
          sessionId,
          question.question_id || question.id,
          question.correct_answer || question.correctAnswer,
          2000 // 2 seconds per question
        )
      }
      
      // Submit test session via API
      const submitResponse = await request.post(`/api/practice/sessions/${sessionId}/complete`, {
        data: {
          total_duration_ms: questions.length * 2000
        }
      })
      
      expect(submitResponse.ok()).toBe(true)
      
      const result = await submitResponse.json()
      expect(result).toBeDefined()
      expect(result.session).toBeDefined()
      expect(result.session.completed_at).toBeDefined()
    } finally {
      await context.cleanup()
    }
  })
})


