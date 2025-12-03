import React, { useState, useEffect } from 'react'
import { useSearchParams, useParams } from 'react-router-dom'
import { useRouter } from '../../../utils/routing'
import { AnimatePresence } from 'framer-motion'
import type { UserProgressData } from '../utils/progressMapping'
import { JourneyHeader } from './journey/JourneyHeader'
import { JourneyStatsOverview } from './journey/JourneyStatsOverview'
import { JourneyTabNavigation, type TabId } from './journey/JourneyTabNavigation'
import { OverviewTab } from './journey/OverviewTab'
import { AchievementsTab } from './journey/AchievementsTab'
import { LevelsTab } from './journey/LevelsTab'
import { TestsTab } from './journey/TestsTab'
import { useFilteredAchievements } from '../hooks/useFilteredAchievements'
import { useJourneyFilters } from '../hooks/useJourneyFilters'
import { useTests } from '../hooks/useTests'
import type { FrontendTest, NewTier } from '../utils/testMapping'
import { mapOldTierToNew } from '../utils/testMapping'

import type { User } from '../hooks/useLearners'

type LevelProgressionSystemProps = {
  userData?: UserProgressData
  user?: User | null
  onBack?: () => void
  initialTab?: TabId
  searchParams?: URLSearchParams
}

export const LevelProgressionSystem: React.FC<LevelProgressionSystemProps> = ({ userData, user, onBack, initialTab, searchParams: initialSearchParams }) => {
  const router = useRouter()
  const params = useParams<{ userId: string; tab?: TabId }>() || {}
  const [searchParams, setSearchParams] = useSearchParams(initialSearchParams || undefined)
  
  // Determine if we're in modal mode (onBack provided but not on a route)
  const isModalMode = !!onBack && !params.userId
  
  // For modal mode, use local state for active tab. For route mode, use URL params
  const [modalActiveTab, setModalActiveTab] = useState<TabId>(initialTab || 'overview')
  
  // Sync activeTab: route mode uses URL params, modal mode uses local state
  const activeTab = isModalMode 
    ? modalActiveTab 
    : (params.tab || initialTab || 'overview') as TabId
  
  // Update modal tab when initialTab changes
  useEffect(() => {
    if (isModalMode && initialTab) {
      setModalActiveTab(initialTab)
    }
  }, [isModalMode, initialTab])

  // Use URL params as single source of truth - no state sync needed!
  const {
    achievementFilter,
    statusFilter,
    textFilter,
    setAchievementFilter,
    setStatusFilter,
    setTextFilter,
  } = useJourneyFilters()

  const {
    filteredAchievements,
    totalAchievements,
    unlockedAchievements,
    inProgressAchievements,
    unlockedTestAchievements,
    sssRankAchievements,
  } = useFilteredAchievements({
    achievements: userData?.achievements || [],
    achievementFilter,
    statusFilter,
    tierFilter: 'all',
    textFilter,
  })

  // Tests data
  const userId = userData ? parseInt(userData.id, 10) : null
  const { tests, getTestAttempts, getTestAttemptDetail } = useTests({
    userId,
    userLevel: userData?.level || 1,
  })

  // Test filters - also use URL as single source of truth
  // Support both old and new tier systems for backward compatibility
  const tierParam = searchParams.get('tier') || 'all'
  const testTierFilter = (tierParam === 'all' 
    ? 'all' 
    : mapOldTierToNew(tierParam)) as 'all' | NewTier
  const testStatusFilter = (searchParams.get('testStatus') || 'all') as 'all' | 'locked' | 'unlocked' | 'attempted'
  const testTextFilter = searchParams.get('testText') || ''
  
  const setTestTierFilter = (tier: 'all' | NewTier) => {
    const newParams = new URLSearchParams(searchParams)
    if (tier !== 'all') {
      newParams.set('tier', tier)
    } else {
      newParams.delete('tier')
    }
    setSearchParams(newParams, { replace: true })
  }
  
  const setTestStatusFilter = (status: 'all' | 'locked' | 'unlocked' | 'attempted') => {
    const newParams = new URLSearchParams(searchParams)
    if (status !== 'all') {
      newParams.set('testStatus', status)
    } else {
      newParams.delete('testStatus')
    }
    setSearchParams(newParams, { replace: true })
  }
  
  const setTestTextFilter = (text: string) => {
    const newParams = new URLSearchParams(searchParams)
    if (text) {
      newParams.set('testText', text)
    } else {
      newParams.delete('testText')
    }
    setSearchParams(newParams, { replace: true })
  }

  if (!userData) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <JourneyHeader userData={userData} onBack={onBack} />

        <JourneyStatsOverview
          userData={userData}
          unlockedAchievements={unlockedAchievements}
          totalAchievements={totalAchievements}
          unlockedTestAchievements={unlockedTestAchievements}
          sssRankAchievements={sssRankAchievements}
          inProgressAchievements={inProgressAchievements}
        />

        <JourneyTabNavigation 
          activeTab={activeTab} 
          onTabChange={(tab) => {
            if (isModalMode) {
              // In modal mode, just update local state (don't navigate)
              setModalActiveTab(tab)
            } else {
              // In route mode, navigate to the tab (preserves searchParams automatically)
              const userId = userData?.id || params.userId
              if (userId) {
                router.navigate(`/journey/${userId}/${tab}`)
              }
            }
          }}
          userId={userData?.id || params.userId || ''}
        />

        {/* Content Based on Active Tab */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <OverviewTab 
              allAchievements={userData.achievements} 
              onViewAllTests={() => {
                const userId = userData?.id || params.userId
                if (userId) {
                  const queryString = searchParams.toString() ? `?${searchParams.toString()}` : ''
                  router.navigate(`/journey/${userId}/achievements${queryString}`)
                }
              }}
              userData={userData}
            />
          )}

          {activeTab === 'achievements' && (
            <AchievementsTab
              filteredAchievements={filteredAchievements}
              achievementFilter={achievementFilter}
              statusFilter={statusFilter}
              textFilter={textFilter}
              onAchievementFilterChange={setAchievementFilter}
              onStatusFilterChange={setStatusFilter}
              onTextFilterChange={setTextFilter}
            />
          )}

          {activeTab === 'levels' && <LevelsTab userData={userData} user={user} isActive={activeTab === 'levels'} />}

          {activeTab === 'tests' && (
            <TestsTab
              tests={tests}
              tierFilter={testTierFilter}
              statusFilter={testStatusFilter}
              textFilter={testTextFilter}
              onTierFilterChange={setTestTierFilter}
              onStatusFilterChange={setTestStatusFilter}
              onTextFilterChange={setTestTextFilter}
              onStartTest={handleStartTest}
              getTestAttempts={getTestAttempts}
              getTestAttemptDetail={getTestAttemptDetail}
              selectedUser={user || (userData ? {
                id: userData.id,
                name: userData.name,
                avatar: userData.avatar,
                level: userData.level,
                questionsAnswered: userData.totalQuestions,
                averageSpeed: 0,
                achievements: userData.achievements
                  .filter(ach => ach.unlockedAt) // Only include achievements with earnedAt
                  .map(ach => ({
                    id: ach.id,
                    code: ach.id, // Use id as code for Learner type
                    title: ach.title,
                    description: ach.description,
                    icon: ach.icon,
                    earnedAt: ach.unlockedAt!, // Non-null assertion since we filtered
                    category: ach.category,
                  })),
                stats: {
                  additionAccuracy: 0,
                  subtractionAccuracy: 0,
                  multiplicationAccuracy: 0,
                  divisionAccuracy: 0,
                  additionSpeed: 0,
                  subtractionSpeed: 0,
                  multiplicationSpeed: 0,
                  divisionSpeed: 0,
                  currentStreak: userData.currentStreak,
                  bestStreak: userData.bestStreak,
                },
              } : null)}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  )

  function handleStartTest(test: FrontendTest) {
    if (!userData) return

    // FrontendTest extends TestDefinition which has test_type property
    // TypeScript doesn't always infer extended properties, so we access it directly
    const testType = (test as FrontendTest & { test_type: string }).test_type

    // Start test session by navigating to practice page with test parameters
    // Router will preserve context params like env=dev
    router.navigate('/practice', {
      user: userData.name,
      userId: userData.id,
      avatar: userData.avatar,
      testType: testType,
      isTest: 'true',
    })
  }
}

export { mapUserToProgressData } from '../utils/progressMapping'

export default LevelProgressionSystem
