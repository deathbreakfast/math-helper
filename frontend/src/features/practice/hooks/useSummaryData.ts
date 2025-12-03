import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { PracticeSessionSummary } from '../types'
import { parsePrompt } from '../utils/summaryUtils'
import { useLearners } from '../../../lib/learners/hooks'

export type FilterType = 'all' | 'correct' | 'incorrect' | 'flagged'

export interface ProblemResult {
  id: string
  operand1: number
  operand2: number
  operation: 'addition' | 'subtraction' | 'multiplication' | 'division'
  correctAnswer: number
  userAnswer?: number
  isCorrect: boolean
  isMarkedForReview: boolean
  timeSpent: number
  difficulty: number
}

export interface AchievementBadge {
  id: string
  title: string
  description: string
  icon: string
  category: 'speed' | 'accuracy' | 'streak' | 'milestone'
  earnedAt?: Date
}

export interface SummaryMetrics {
  totalProblems: number
  correctProblems: number
  incorrectProblems: number
  flaggedProblems: number
  accuracy: number
  totalTime: number
  averageSpeed: number
  previousBestAccuracy: number
  previousBestSpeed: number
  currentStreak: number
  isNewBestAccuracy: boolean
  isNewBestSpeed: boolean
}

export const useSummaryData = (filter: FilterType) => {
  const { learners } = useLearners()
  const [searchParams] = useSearchParams()

  // Get session data from URL parameters or localStorage
  const sessionSummary = useMemo<PracticeSessionSummary | null>(() => {
    // Read sessionId from URL (new approach - only ID in URL)
    const sessionId = searchParams.get('sessionId')
    
    // Also support legacy 'session' param for backward compatibility during transition
    const legacySessionParam = searchParams.get('session')

    // If legacy session param exists, try to parse it (backward compatibility)
    if (legacySessionParam) {
      try {
        return JSON.parse(decodeURIComponent(legacySessionParam)) as PracticeSessionSummary
      } catch {
        // Invalid JSON, fall through to localStorage
      }
    }

    // Get session from localStorage (stored with key 'lastPracticeSession')
    const savedSession = localStorage.getItem('lastPracticeSession')
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession) as PracticeSessionSummary
        // If sessionId was provided in URL, verify it matches (for future multi-session support)
        if (!sessionId || parsed.id === sessionId) {
          return parsed
        }
      } catch {
        // Invalid JSON
      }
    }

    return null
  }, [searchParams])

  // Find user data
  const user = useMemo(() => {
    if (!sessionSummary?.user) return null
    return learners.find((l) => l.id === String(sessionSummary.user.id)) || null
  }, [sessionSummary, learners])

  // Transform attempts to ProblemResult format
  const problems = useMemo<ProblemResult[]>(() => {
    if (!sessionSummary) return []
    return sessionSummary.attempts.map((attempt, index) => {
      const parsed = parsePrompt(attempt.prompt)
      return {
        id: attempt.questionId || `problem-${index}`,
        operand1: parsed.operand1,
        operand2: parsed.operand2,
        operation: parsed.operation,
        correctAnswer: Number(attempt.correctAnswer),
        userAnswer: attempt.submittedAnswer ? Number(attempt.submittedAnswer) : undefined,
        isCorrect: attempt.isCorrect,
        isMarkedForReview: false, // We don't track this in current data structure
        timeSpent: attempt.elapsedMs ? attempt.elapsedMs / 1000 : 0,
        difficulty: 1, // Default difficulty, could be enhanced
      }
    })
  }, [sessionSummary])

  // Calculate metrics
  const metrics = useMemo<SummaryMetrics>(() => {
    const totalProblems = problems.length
    const correctProblems = problems.filter((p) => p.isCorrect).length
    const incorrectProblems = problems.filter((p) => !p.isCorrect).length
    const flaggedProblems = problems.filter((p) => p.isMarkedForReview).length
    const accuracy = totalProblems > 0 ? Math.round((correctProblems / totalProblems) * 100) : 0
    const totalTime = problems.reduce((sum, p) => sum + p.timeSpent, 0)
    const averageSpeed = totalProblems > 0 ? Math.round((totalTime / totalProblems) * 10) / 10 : 0

    // Get previous bests from user stats
    const previousBestAccuracy = user?.stats?.additionAccuracy || 0
    const previousBestSpeed = user?.averageSpeed || 0
    const currentStreak = user?.stats?.currentStreak || 0

    // Check if this is a new personal best
    const isNewBestAccuracy = accuracy > previousBestAccuracy
    const isNewBestSpeed = averageSpeed < previousBestSpeed || previousBestSpeed === 0

    return {
      totalProblems,
      correctProblems,
      incorrectProblems,
      flaggedProblems,
      accuracy,
      totalTime,
      averageSpeed,
      previousBestAccuracy,
      previousBestSpeed,
      currentStreak,
      isNewBestAccuracy,
      isNewBestSpeed,
    }
  }, [problems, user])

  // Calculate performance by difficulty
  const performanceByDifficulty = useMemo(() => {
    return problems.reduce(
      (acc, problem) => {
        if (!acc[problem.difficulty]) {
          acc[problem.difficulty] = { correct: 0, total: 0 }
        }
        acc[problem.difficulty].total++
        if (problem.isCorrect) acc[problem.difficulty].correct++
        return acc
      },
      {} as Record<number, { correct: number; total: number }>
    )
  }, [problems])

  // Use achievements from backend (earned during this session)
  // Convert backend achievement format to AchievementBadge format
  const achievements = useMemo<AchievementBadge[]>(() => {
    if (!sessionSummary?.achievements || sessionSummary.achievements.length === 0) {
      // Return empty array if no achievements (removed fallback "Session Complete")
      return []
    }
    
    // Convert backend achievements to AchievementBadge format
    return sessionSummary.achievements.map((backendAchievement: any) => ({
      id: backendAchievement.code || backendAchievement.id || `achievement-${Date.now()}`,
      title: backendAchievement.title || 'Achievement',
      description: backendAchievement.description || '',
      icon: backendAchievement.icon || '🏆',
      category: (backendAchievement.category === 'consistency' ? 'streak' : 
                 backendAchievement.category === 'speed' ? 'speed' :
                 backendAchievement.category === 'accuracy' ? 'accuracy' : 'milestone') as AchievementBadge['category'],
      earnedAt: backendAchievement.earnedAt ? new Date(backendAchievement.earnedAt) : new Date(),
    }))
  }, [sessionSummary, metrics.totalProblems])

  // Filter problems
  const filteredProblems = useMemo(() => {
    return problems.filter((problem) => {
      if (filter === 'correct') return problem.isCorrect
      if (filter === 'incorrect') return !problem.isCorrect
      if (filter === 'flagged') return problem.isMarkedForReview
      return true
    })
  }, [problems, filter])

  // Extract level up information
  const levelUp = useMemo(() => {
    return sessionSummary?.level_up || null
  }, [sessionSummary])

  return {
    sessionSummary,
    user,
    problems,
    metrics,
    performanceByDifficulty,
    achievements,
    filteredProblems,
    levelUp,
  }
}

