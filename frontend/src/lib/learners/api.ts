import type { ApiLearner, ApiLearnerAchievement, Learner, LearnerAchievement, LearnerStats } from './types'

export const AVATAR_OPTIONS = ['👧', '👦', '🧒', '👨', '👩', '🧑', '👶', '🦸', '🦹', '🧙', '🧚', '🦄']

export const sanitizeStats = (stats: Partial<LearnerStats> | undefined): LearnerStats => ({
  additionAccuracy: stats?.additionAccuracy ?? 0,
  subtractionAccuracy: stats?.subtractionAccuracy ?? 0,
  multiplicationAccuracy: stats?.multiplicationAccuracy ?? 0,
  divisionAccuracy: stats?.divisionAccuracy ?? 0,
  additionSpeed: stats?.additionSpeed ?? 0,
  subtractionSpeed: stats?.subtractionSpeed ?? 0,
  multiplicationSpeed: stats?.multiplicationSpeed ?? 0,
  divisionSpeed: stats?.divisionSpeed ?? 0,
  currentStreak: stats?.currentStreak ?? 0,
  bestStreak: stats?.bestStreak ?? 0,
})

const mapAchievement = (achievement: ApiLearnerAchievement): LearnerAchievement => ({
  ...achievement,
  earnedAt: achievement.earnedAt ? new Date(achievement.earnedAt) : new Date(),
})

export const mapApiLearner = (payload: ApiLearner): Learner => {
  const mappedAchievements = (payload.achievements || []).map(mapAchievement)
  
  // Step 2: Log post-mapping to verify metadata preservation
  if (import.meta.env.DEV) {
    const withMetadata = mappedAchievements.filter(a => a.metadata?.concept_id)
    const withoutMetadata = mappedAchievements.filter(a => !a.metadata?.concept_id)
    
    console.group('🔍 Step 2: Post-API Mapping (LearnerAchievement[])')
    console.log('Mapped Achievements:', {
      totalCount: mappedAchievements.length,
      withMetadata: withMetadata.length,
      withoutMetadata: withoutMetadata.length,
    })
    console.log('Sample Mapped Achievements WITH metadata (first 5):', 
      withMetadata.slice(0, 5).map(a => ({
        id: a.id,
        code: a.code,
        metadata: a.metadata,
        concept_id: a.metadata?.concept_id,
      }))
    )
    console.log('Sample Mapped Achievements WITHOUT metadata (first 5):', 
      withoutMetadata.slice(0, 5).map(a => ({
        id: a.id,
        code: a.code,
        metadata: a.metadata,
      }))
    )
    console.groupEnd()
  }
  
  return {
    id: String(payload.id),
    name: payload.name,
    avatar: payload.avatar || AVATAR_OPTIONS[0],
    // PIN is not included in API responses for security
    level: payload.level ?? 1,
    experience: payload.experience ?? 0,
    xp_progress: payload.xp_progress,
    questionsAnswered: payload.questionsAnswered ?? 0,
    weeklyGain: payload.weeklyGain ?? 0,
    averageSpeed: payload.averageSpeed ?? 0,
    achievements: mappedAchievements,
    stats: sanitizeStats(payload.stats),
  }
}


