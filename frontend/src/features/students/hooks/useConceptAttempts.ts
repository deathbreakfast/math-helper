/**
 * Hook to fetch concept practice attempts
 * For now, concepts map 1:1 to levels, so we fetch practice sessions by level
 */

import { useState, useEffect } from 'react'
import { logError } from '../../../utils/logger'

export type ConceptAttempt = {
  attempt_id: number
  session_id: number
  conceptId: string
  accuracy: number
  total_questions: number
  correct_count: number
  attempted_at: Date
  total_duration_ms?: number
}

export type ConceptAttemptDetail = ConceptAttempt & {
  questions?: Array<{
    question_id: number
    prompt: string
    submitted_answer: string
    correct_answer: string
    is_correct: boolean
    duration_ms?: number
  }>
}

/**
 * Fetch concept attempts for a given concept
 * For now, we fetch practice sessions by level (since concept maps 1:1 to level)
 */
export async function getConceptAttempts(
  conceptId: string,
  userId: number
): Promise<ConceptAttempt[]> {
  try {
    // Fetch practice sessions for this user and concept
    const response = await fetch(
      `/api/practice/sessions?user_id=${userId}&concept_id=${encodeURIComponent(conceptId)}&completed=true`
    )
    
    if (!response.ok) {
      throw new Error(`Failed to fetch concept attempts: ${response.statusText}`)
    }

    const data = await response.json()
    
    // Transform sessions to concept attempts
    const sessions = data.sessions || []
    return sessions.map((session: any) => ({
      attempt_id: session.id,
      session_id: session.id,
      conceptId,
      accuracy: session.accuracy || 0,
      total_questions: session.total_questions || 0,
      correct_count: session.correct_count || 0,
      attempted_at: new Date(session.completed_at || session.started_at),
      total_duration_ms: session.total_duration_ms,
    }))
  } catch (error) {
    logError('Error fetching concept attempts:', error)
    throw error
  }
}

/**
 * Fetch detailed attempt information
 */
export async function getConceptAttemptDetail(
  attemptId: number
): Promise<ConceptAttemptDetail | null> {
  try {
    // Fetch session details
    const response = await fetch(`/api/practice/sessions/${attemptId}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch attempt detail: ${response.statusText}`)
    }

    const data = await response.json()
    
    // Extract session and questions from response
    // Backend returns: { session: {...}, questions: [...] }
    const session = data.session || data
    const questionsData = data.questions || []
    
    // Use concept_id from session if available, otherwise infer from level
    const inferredConceptId = session.concept_id || (session.level ? `c_concept_${String(session.level).padStart(3, '0')}` : 'c_concept_001')
    
    // Preserve original attempt data - ensure we use session data correctly
    return {
      attempt_id: attemptId,
      session_id: attemptId,
      conceptId: inferredConceptId,
      accuracy: session.accuracy || 0,
      total_questions: session.total_questions || 0,
      correct_count: session.correct_count || 0,
      attempted_at: new Date(session.completed_at || session.started_at),
      total_duration_ms: session.total_duration_ms,
      questions: questionsData.map((q: any) => ({
        question_id: q.question_id || q.id,
        prompt: q.prompt,
        submitted_answer: q.response?.submitted_answer || '',
        correct_answer: q.correctAnswer || q.correct_answer,
        is_correct: q.response?.is_correct || false,
        duration_ms: q.response?.duration_ms,
      })),
    }
  } catch (error) {
    logError('Error fetching attempt detail:', error)
    return null
  }
}

/**
 * Hook to fetch and manage concept attempts
 */
export function useConceptAttempts(conceptId: string | null, userId: number | null, enabled: boolean = true) {
  const [attempts, setAttempts] = useState<ConceptAttempt[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!enabled || !conceptId || !userId) {
      setAttempts([])
      setIsLoading(false)
      return
    }

    const fetchAttempts = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const fetchedAttempts = await getConceptAttempts(conceptId, userId)
        setAttempts(fetchedAttempts)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch attempts')
        setAttempts([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchAttempts()
  }, [conceptId, userId, enabled])

  return { attempts, isLoading, error }
}
