import React, { useState, useEffect, useMemo } from 'react'
import { useSearchParams, useParams } from 'react-router-dom'
import { useRouter } from '../../../utils/routing'
import { AnimatePresence } from 'framer-motion'
import type { UserProgressData } from '../utils/progressMapping'
import { JourneyHeader } from './journey/JourneyHeader'
import { JourneyStatsOverview } from './journey/JourneyStatsOverview'
import { JourneyTabNavigation, type TabId } from './journey/JourneyTabNavigation'
import { OverviewTab } from './journey/OverviewTab'
import { AchievementsTab } from './journey/AchievementsTab'
import { ForceGraphTab } from './journey/ForceGraphTab'
import { useFilteredAchievements } from '../hooks/useFilteredAchievements'
import { useJourneyFilters } from '../hooks/useJourneyFilters'
import { useAchievementDefinitions } from '../../../lib/levels/hooks'
import { useMathConcepts } from '../hooks/useMathConcepts'

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

  const { definitions: achievementDefinitions } = useAchievementDefinitions()

  const {
    filteredAchievements,
    totalAchievements,
    unlockedAchievements,
    inProgressAchievements,
  } = useFilteredAchievements({
    achievements: userData?.achievements || [],
    achievementFilter,
    statusFilter,
    textFilter,
  })

  // Calculate unlocked math concepts count
  const { concepts: mathConcepts } = useMathConcepts({
    userData,
    isActive: true,
    userId: userData?.id || params.userId,
  })
  
  const unlockedConceptsCount = useMemo(() => {
    return mathConcepts.filter(c => !c.isLocked).length
  }, [mathConcepts])
  
  const totalConceptsCount = useMemo(() => {
    return mathConcepts.length
  }, [mathConcepts])

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
          unlockedConceptsCount={unlockedConceptsCount}
          totalConceptsCount={totalConceptsCount}
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
              onViewAllAchievements={() => {
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
              userId={userData?.id || params.userId || ''}
              achievementDefinitions={achievementDefinitions}
            />
          )}

          {activeTab === 'math-types' && (
            <ForceGraphTab
              achievements={userData.achievements || []}
              userData={userData}
              userId={userData?.id || params.userId || ''}
              achievementDefinitions={achievementDefinitions}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export { mapUserToProgressData } from '../utils/progressMapping'

export default LevelProgressionSystem
