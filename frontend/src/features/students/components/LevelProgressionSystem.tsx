import React, { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import type { UserProgressData } from '../utils/progressMapping'
import { JourneyHeader } from './journey/JourneyHeader'
import { JourneyStatsOverview } from './journey/JourneyStatsOverview'
import { JourneyTabNavigation, type TabId } from './journey/JourneyTabNavigation'
import { OverviewTab } from './journey/OverviewTab'
import { TestsTab } from './journey/TestsTab'
import { AchievementsTab } from './journey/AchievementsTab'
import { LevelsTab } from './journey/LevelsTab'
import { useJourneyFilters } from '../hooks/useJourneyFilters'
import { useFilteredAchievements } from '../hooks/useFilteredAchievements'

type LevelProgressionSystemProps = {
  userData?: UserProgressData
  onBack?: () => void
}

export const LevelProgressionSystem: React.FC<LevelProgressionSystemProps> = ({ userData, onBack }) => {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  const {
    achievementFilter,
    statusFilter,
    testFilter,
    tierFilter,
    setAchievementFilter,
    setStatusFilter,
    setTestFilter,
    setTierFilter,
  } = useJourneyFilters()

  const {
    filteredAchievements,
    testAchievements,
    filteredTestAchievements,
    totalAchievements,
    unlockedAchievements,
    inProgressAchievements,
    unlockedTestAchievements,
    sssRankAchievements,
  } = useFilteredAchievements({
    achievements: userData?.achievements || [],
    achievementFilter,
    statusFilter,
    testFilter,
    tierFilter,
  })

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
            <OverviewTab testAchievements={testAchievements} onViewAllTests={() => setActiveTab('tests')} />
          )}

          {activeTab === 'tests' && (
            <TestsTab
              filteredTestAchievements={filteredTestAchievements}
              testFilter={testFilter}
              tierFilter={tierFilter}
              statusFilter={statusFilter}
              onTestFilterChange={setTestFilter}
              onTierFilterChange={setTierFilter}
              onStatusFilterChange={setStatusFilter}
            />
          )}

          {activeTab === 'achievements' && (
            <AchievementsTab
              filteredAchievements={filteredAchievements}
              achievementFilter={achievementFilter}
              statusFilter={statusFilter}
              onAchievementFilterChange={setAchievementFilter}
              onStatusFilterChange={setStatusFilter}
            />
          )}

          {activeTab === 'levels' && <LevelsTab userData={userData} />}
        </AnimatePresence>
      </div>
    </div>
  )
}

export { mapUserToProgressData } from '../utils/progressMapping'

export default LevelProgressionSystem
