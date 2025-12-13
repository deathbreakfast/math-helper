import { http, HttpResponse } from 'msw'

// Practice API handlers
export const practiceHandlers = [
  // Start practice session
  http.post('/api/practice/sessions/start', async ({ request }) => {
    const body = await request.json() as any
    const sessionId = Math.floor(Math.random() * 1000)
    
    return HttpResponse.json({
      session_id: sessionId,
      mode: body.mode || 'standard',
      questions: [
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
          hint: '',
        },
        {
          id: 2,
          question_id: 2,
          prompt: '3 + 3',
          operation: 'addition',
          operand1: 3,
          operand2: 3,
          correct_answer: '6',
          difficulty: 'Level 1',
          target_ms: 4000,
          hint: '',
        },
      ],
    })
  }),

  // Check answer
  http.post('/api/practice/questions/check', async ({ request }) => {
    const body = await request.json() as any
    const submittedAnswer = body.submitted_answer?.toString().trim()
    const questionId = body.question_id
    
    // Mock correct answer logic (simplified)
    const correctAnswers: Record<number, string> = {
      1: '4',
      2: '6',
    }
    
    const isCorrect = correctAnswers[questionId] === submittedAnswer
    
    return HttpResponse.json({
      is_correct: isCorrect,
    })
  }),

  // Complete session
  http.post('/api/practice/sessions/:sessionId/complete', async ({ params }) => {
    const sessionId = parseInt(params.sessionId as string)
    
    return HttpResponse.json({
      session: {
        id: sessionId,
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
  }),
]

// Tests API handlers
export const testsHandlers = [
  // Get test definitions
  http.get('/api/tests/definitions', async ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')
    
    return HttpResponse.json({
      definitions: [
        {
          test_type: 'addition-basics',
          display_name: 'Addition Basics',
          operation: 'addition',
          level_requirement: 1,
          question_count: 10,
          constraints: {},
          unlock_status: {
            is_unlocked: true,
            requirements_met: 1,
            requirements_total: 1,
          },
        },
      ],
    })
  }),

  // Get test attempts
  http.get('/api/tests/attempts', async ({ request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')
    
    return HttpResponse.json({
      attempts: [
        {
          id: 1,
          test_type: 'addition-basics',
          tier: 'Gold',
          accuracy: 100,
          attempted_at: new Date().toISOString(),
        },
      ],
    })
  }),

  // Get test attempts for specific test type
  http.get('/api/tests/:testType/attempts', async ({ params, request }) => {
    const url = new URL(request.url)
    const userId = url.searchParams.get('user_id')
    
    return HttpResponse.json({
      attempts: [
        {
          id: 1,
          test_type: params.testType,
          tier: 'Gold',
          accuracy: 100,
          attempted_at: new Date().toISOString(),
        },
      ],
    })
  }),

  // Get test attempt detail
  http.get('/api/tests/attempts/:attemptId/details', async ({ params }) => {
    return HttpResponse.json({
      id: parseInt(params.attemptId as string),
      test_type: 'addition-basics',
      tier: 'Gold',
      accuracy: 100,
      attempted_at: new Date().toISOString(),
      questions: [],
    })
  }),
]

// Users/Learners API handlers
export const usersHandlers = [
  // Get all users
  http.get('/api/users', async ({ request }) => {
    const url = new URL(request.url)
    const minimal = url.searchParams.get('minimal') === 'true'
    
    return HttpResponse.json({
      users: [
        {
          id: 1,
          name: 'Test User',
          avatar: '👧',
          level: 1,
          questionsAnswered: 0,
          weeklyGain: 0,
          averageSpeed: 0,
          achievements: minimal ? [] : [
            {
              code: 'first-steps',
              title: 'First Steps',
              earnedAt: new Date().toISOString(),
            },
          ],
          stats: {
            additionAccuracy: 0,
            subtractionAccuracy: 0,
            multiplicationAccuracy: 0,
            divisionAccuracy: 0,
            additionSpeed: 0,
            subtractionSpeed: 0,
            multiplicationSpeed: 0,
            divisionSpeed: 0,
            currentStreak: 0,
            bestStreak: 0,
          },
        },
      ],
    })
  }),

  // Get single user
  http.get('/api/users/:userId', async ({ params }) => {
    const userId = params.userId
    
    return HttpResponse.json({
      id: parseInt(userId as string),
      name: 'Test User',
      avatar: '👧',
      level: 1,
      questionsAnswered: 0,
      weeklyGain: 0,
      averageSpeed: 0,
      achievements: [
        {
          code: 'first-steps',
          title: 'First Steps',
          earnedAt: new Date().toISOString(),
        },
      ],
      stats: {
        additionAccuracy: 0,
        subtractionAccuracy: 0,
        multiplicationAccuracy: 0,
        divisionAccuracy: 0,
        additionSpeed: 0,
        subtractionSpeed: 0,
        multiplicationSpeed: 0,
        divisionSpeed: 0,
        currentStreak: 0,
        bestStreak: 0,
      },
    })
  }),

  // Create user
  http.post('/api/users', async ({ request }) => {
    const body = await request.json() as any
    
    return HttpResponse.json({
      id: Math.floor(Math.random() * 1000),
      name: body.name,
      avatar: body.avatar || '👧',
      pin: body.pin,
      level: 1,
      questionsAnswered: 0,
      weeklyGain: 0,
      averageSpeed: 0,
      achievements: [],
      stats: {
        additionAccuracy: 0,
        subtractionAccuracy: 0,
        multiplicationAccuracy: 0,
        divisionAccuracy: 0,
        additionSpeed: 0,
        subtractionSpeed: 0,
        multiplicationSpeed: 0,
        divisionSpeed: 0,
        currentStreak: 0,
        bestStreak: 0,
      },
    }, { status: 201 })
  }),
]

// Combine all handlers
export const handlers = [
  ...practiceHandlers,
  ...testsHandlers,
  ...usersHandlers,
]



