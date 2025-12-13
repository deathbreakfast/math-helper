import { test, expect } from './fixtures/test-user'
import {
  startPracticeSessionViaAPI,
  answerQuestionViaAPI,
  navigateToPractice,
  handleSessionRestorationAndAnswerToSubmit,
  waitForSummaryPage,
  submitPracticeSession,
  getIncompleteSession,
} from './helpers/test-helpers'

test.describe('Summary Page - NEW BEST! Indicators', () => {
  test('SUM-NB-001: NEW BEST! shows for accuracy only when improved', async ({ page, request, testUser }) => {
    test.setTimeout(60000)
    
    // First session: 80% accuracy
    const session1Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session1Id, questions: questions1 } = session1Data
    
    // Answer 8 out of 10 questions correctly (80%)
    for (let i = 0; i < questions1.length; i++) {
      const question = questions1[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      const isCorrect = i < 8 // First 8 correct, last 2 wrong
      
      await answerQuestionViaAPI(
        request,
        session1Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        isCorrect ? String(correctAnswer) : '999',
        2000
      )
    }
    
    // Complete session 1
    const response1 = await request.post(`/api/practice/sessions/${session1Id}/complete`, {
      data: { totalDurationMs: questions1.length * 2000 }
    })
    expect(response1.ok()).toBeTruthy()
    
    // Navigate to practice and submit to see summary
    const startSession1Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession1Response = await startSession1Promise
    const session1DataUI = await startSession1Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session1Id,
      session1DataUI.session_id,
      questions1,
      session1DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // First session should show NEW BEST! (first time achieving this accuracy)
    const newBestAccuracy1 = page.getByTestId('testid-new-best-accuracy')
    const newBestVisible1 = await newBestAccuracy1.isVisible({ timeout: 3000 }).catch(() => false)
    // This might or might not show depending on previous stats - check if it exists
    
    // Second session: 80% accuracy again (should NOT show NEW BEST!)
    await page.goto('/')
    const session2Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session2Id, questions: questions2 } = session2Data
    
    // Answer 8 out of 10 correctly again (same 80%)
    for (let i = 0; i < questions2.length; i++) {
      const question = questions2[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      const isCorrect = i < 8
      
      await answerQuestionViaAPI(
        request,
        session2Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        isCorrect ? String(correctAnswer) : '999',
        2000
      )
    }
    
    await request.post(`/api/practice/sessions/${session2Id}/complete`, {
      data: { totalDurationMs: questions2.length * 2000 }
    })
    
    const startSession2Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession2Response = await startSession2Promise
    const session2DataUI = await startSession2Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session2Id,
      session2DataUI.session_id,
      questions2,
      session2DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Second session with same accuracy should NOT show NEW BEST!
    const newBestAccuracy2 = page.getByTestId('testid-new-best-accuracy')
    const newBestVisible2 = await newBestAccuracy2.isVisible({ timeout: 2000 }).catch(() => false)
    expect(newBestVisible2).toBe(false)
    
    // Third session: 90% accuracy (should show NEW BEST!)
    await page.goto('/')
    const session3Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session3Id, questions: questions3 } = session3Data
    
    // Answer 9 out of 10 correctly (90%)
    for (let i = 0; i < questions3.length; i++) {
      const question = questions3[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      const isCorrect = i < 9
      
      await answerQuestionViaAPI(
        request,
        session3Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        isCorrect ? String(correctAnswer) : '999',
        2000
      )
    }
    
    await request.post(`/api/practice/sessions/${session3Id}/complete`, {
      data: { totalDurationMs: questions3.length * 2000 }
    })
    
    const startSession3Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession3Response = await startSession3Promise
    const session3DataUI = await startSession3Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session3Id,
      session3DataUI.session_id,
      questions3,
      session3DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Third session with better accuracy should show NEW BEST!
    const newBestAccuracy3 = page.getByTestId('testid-new-best-accuracy')
    await expect(newBestAccuracy3).toBeVisible({ timeout: 3000 })
  })

  test('SUM-NB-002: NEW BEST! shows for speed only when improved', async ({ page, request, testUser }) => {
    test.setTimeout(60000)
    
    // First session: 3s average speed
    const session1Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session1Id, questions: questions1 } = session1Data
    
    // Answer all questions quickly (3000ms each = 3s average)
    for (let i = 0; i < questions1.length; i++) {
      const question = questions1[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      await answerQuestionViaAPI(
        request,
        session1Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        3000 // 3 seconds
      )
    }
    
    await request.post(`/api/practice/sessions/${session1Id}/complete`, {
      data: { totalDurationMs: questions1.length * 3000 }
    })
    
    // Navigate and submit
    const startSession1Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession1Response = await startSession1Promise
    const session1DataUI = await startSession1Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session1Id,
      session1DataUI.session_id,
      questions1,
      session1DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Second session: 3s average speed again (should NOT show NEW BEST!)
    await page.goto('/')
    const session2Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session2Id, questions: questions2 } = session2Data
    
    for (let i = 0; i < questions2.length; i++) {
      const question = questions2[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      await answerQuestionViaAPI(
        request,
        session2Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        3000 // Same speed
      )
    }
    
    await request.post(`/api/practice/sessions/${session2Id}/complete`, {
      data: { totalDurationMs: questions2.length * 3000 }
    })
    
    const startSession2Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession2Response = await startSession2Promise
    const session2DataUI = await startSession2Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session2Id,
      session2DataUI.session_id,
      questions2,
      session2DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Same speed should NOT show NEW BEST!
    const newBestSpeed2 = page.getByTestId('testid-new-best-speed')
    const newBestVisible2 = await newBestSpeed2.isVisible({ timeout: 2000 }).catch(() => false)
    expect(newBestVisible2).toBe(false)
    
    // Third session: 2s average speed (faster - should show NEW BEST!)
    await page.goto('/')
    const session3Data = await startPracticeSessionViaAPI(request, testUser.id)
    const { session_id: session3Id, questions: questions3 } = session3Data
    
    for (let i = 0; i < questions3.length; i++) {
      const question = questions3[i]
      const questionId = question.question_id || question.id
      const correctAnswer = question.correctAnswer || question.correct_answer
      
      await answerQuestionViaAPI(
        request,
        session3Id,
        typeof questionId === 'string' ? parseInt(questionId) : questionId,
        String(correctAnswer),
        2000 // Faster: 2 seconds
      )
    }
    
    await request.post(`/api/practice/sessions/${session3Id}/complete`, {
      data: { totalDurationMs: questions3.length * 2000 }
    })
    
    const startSession3Promise = page.waitForResponse(
      (r) => r.url().includes('/api/practice/sessions/start') && r.request().method() === 'POST',
      { timeout: 15000 }
    )
    
    await navigateToPractice(page, testUser)
    const startSession3Response = await startSession3Promise
    const session3DataUI = await startSession3Response.json()
    
    await handleSessionRestorationAndAnswerToSubmit(
      page,
      session3Id,
      session3DataUI.session_id,
      questions3,
      session3DataUI.questions
    )
    
    await submitPracticeSession(page)
    await waitForSummaryPage(page)
    
    // Better speed should show NEW BEST!
    const newBestSpeed3 = page.getByTestId('testid-new-best-speed')
    await expect(newBestSpeed3).toBeVisible({ timeout: 3000 })
  })
})
