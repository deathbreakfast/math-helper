import React, { useState, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import type { UserProgressData } from '../utils/progressMapping'
import { JourneyHeader } from './journey/JourneyHeader'
import { JourneyStatsOverview } from './journey/JourneyStatsOverview'
import { JourneyTabNavigation, type TabId } from './journey/JourneyTabNavigation'
import { OverviewTab } from './journey/OverviewTab'
import { AchievementsTab } from './journey/AchievementsTab'
import { LevelsTab } from './journey/LevelsTab'
import { TestsTab } from './journey/TestsTab'
import { useJourneyFilters } from '../hooks/useJourneyFilters'
import { useFilteredAchievements } from '../hooks/useFilteredAchievements'
import { useTests } from '../hooks/useTests'
import type { FrontendTest } from '../utils/testMapping'

import type { User } from '../hooks/useLearners'

type LevelProgressionSystemProps = {
  userData?: UserProgressData
  user?: User | null
  onBack?: () => void
}

export const LevelProgressionSystem: React.FC<LevelProgressionSystemProps> = ({ userData, user, onBack }) => {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

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
  const { tests, isLoading: isLoadingTests, getTestAttempts, getTestAttemptDetail } = useTests({
    userId,
    userLevel: userData?.level || 1,
  })

  // Test filters
  const [testTierFilter, setTestTierFilter] = useState<'all' | 'B' | 'A' | 'S' | 'SS' | 'SSS'>('all')
  const [testStatusFilter, setTestStatusFilter] = useState<'all' | 'locked' | 'unlocked' | 'attempted'>('all')
  const [testTextFilter, setTestTextFilter] = useState<string>('')

  // DEBUG: Log achievements data when it changes
  // [STACK: LevelProgressionSystem - After filtering achievements]
  useEffect(() => {
    if (userData) {
      console.log(`[ACH-008] [LEVEL PROGRESSION] UserData achievements count: ${userData.achievements?.length || 0}`)
      if (userData.achievements && userData.achievements.length > 0) {
        const achievementCodes = userData.achievements.map(a => a.code || a.id || a.title).filter(Boolean)
        console.log(`[ACH-008] [LEVEL PROGRESSION] UserData achievement codes:`, achievementCodes)
      }
      
      console.log(`[ACH-008] [LEVEL PROGRESSION] Filtered achievements count: ${filteredAchievements.length}`)
      console.log(`[ACH-008] [LEVEL PROGRESSION] Total achievements: ${totalAchievements}, Unlocked: ${unlockedAchievements}`)
      
      if (filteredAchievements.length > 0) {
        const filteredCodes = filteredAchievements.map(a => a.code || a.id || a.title).filter(Boolean)
        console.log(`[ACH-008] [LEVEL PROGRESSION] Filtered achievement codes:`, filteredCodes)
      }
    }
  }, [userData, filteredAchievements, totalAchievements, unlockedAchievements])

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

        <JourneyTabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Content Based on Active Tab */}
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <OverviewTab 
              allAchievements={userData.achievements} 
              onViewAllTests={() => setActiveTab('achievements')}
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
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  )

  function handleStartTest(test: FrontendTest) {
    if (!userData) return

    const userId = parseInt(userData.id, 10)
    const testType = test.test_type

    // Start test session by navigating to practice page with test parameters
    const params = new URLSearchParams({
      user: userData.name,
      userId: userData.id,
      avatar: userData.avatar,
      testType: testType,
      isTest: 'true',
    })

    window.location.assign(`/practice?${params.toString()}`)
  }
}

export { mapUserToProgressData } from '../utils/progressMapping'

export default LevelProgressionSystem
