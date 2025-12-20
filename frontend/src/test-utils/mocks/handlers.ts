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
        earned_xp: 1946,
        previous_total_xp: 0,
        total_xp: 1946,
        previous_level: 1,
        leveled_up: true,
        xp_progress: {
          level: 2,
          total_xp: 1946,
          current_level_total_xp: 500,
          next_level_total_xp: 1500,
          xp_into_level: 1446,
          xp_to_next_level: 0,
        },
        xp_breakdown: {
          concept_id: 'c_concept_001',
          xp_per_correct: 97,
          correct_count: 2,
          base_xp: 194,
          multipliers: [],
          total_multiplier: 1,
          multiplied_xp: 194,
          bonus_xp: 0,
          bonus_xp_sources: [],
          total_awarded_xp_raw: 194,
        },
      },
      achievements: [],
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
          experience: 0,
          xp_progress: {
            level: 1,
            total_xp: 0,
            current_level_total_xp: 0,
            next_level_total_xp: 500,
            xp_into_level: 0,
            xp_to_next_level: 500,
          },
          questionsAnswered: 0,
          weeklyGain: 0,
          averageSpeed: 0,
          achievements: minimal ? [] : [
            {
              code: 'first-steps',
              title: 'First Steps',
              earnedAt: new Date().toISOString(),
              xp_reward: {
                bonus_xp: 50,
                multiplier: 1.01,
              },
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
      experience: 0,
      xp_progress: {
        level: 1,
        total_xp: 0,
        current_level_total_xp: 0,
        next_level_total_xp: 500,
        xp_into_level: 0,
        xp_to_next_level: 500,
      },
      questionsAnswered: 0,
      weeklyGain: 0,
      averageSpeed: 0,
      achievements: [
        {
          code: 'first-steps',
          title: 'First Steps',
          earnedAt: new Date().toISOString(),
          xp_reward: {
            bonus_xp: 50,
            multiplier: 1.01,
          },
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
      experience: 0,
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
  ...usersHandlers,
  http.get('/api/concepts/requirements', async ({ request }) => {
    const url = new URL(request.url)
    const conceptIdsParam = url.searchParams.get('concept_ids') || ''
    const conceptIds = conceptIdsParam.split(',').filter(Boolean)

    // Provide minimal unlock requirements for mocks; treat everything as unlocked.
    const requirements: Record<string, any[]> = {}
    for (const cid of conceptIds) {
      requirements[cid] = []
    }

    return HttpResponse.json({ requirements })
  }),
  http.get('/api/achievements/definitions', async () => {
    return HttpResponse.json({
      achievements: {
        'first-steps': {
          code: 'first-steps',
          title: 'First Steps',
          description: 'Your first practice session',
          icon: '🔥',
          category: 'milestone',
          requirements: {},
          xp_reward: {
            bonus_xp: 50,
            multiplier: 1.01,
          },
        },
        'accuracy-ace-bronze': {
          code: 'accuracy-ace-bronze',
          title: 'Accuracy Ace (Bronze)',
          description: 'Session accuracy of 80% or higher',
          icon: '🎯',
          category: 'accuracy',
          requirements: {},
          xp_reward: {
            bonus_xp: 10,
            multiplier: 1.01,
          },
        },
      },
    })
  }),
]




