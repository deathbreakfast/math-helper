import { useState, useEffect } from 'react'
import { useRouter } from '../../utils/routing'
import { PillButton } from '../../components/ui'
import { Home } from 'lucide-react'
import { useSummaryData, type FilterType, type ProblemResult } from './hooks/useSummaryData'
import { SummaryHeader } from './components/summary/SummaryHeader'
import { EncouragementBanner } from './components/summary/EncouragementBanner'
import { SummaryStatsCards } from './components/summary/SummaryStatsCards'
import { PerformanceByDifficulty } from './components/summary/PerformanceByDifficulty'
import { AchievementsSection } from './components/summary/AchievementsSection'
import { SessionStats } from './components/summary/SessionStats'
import { XPEarningsBreakdown } from './components/summary/XPEarningsBreakdown'
import { LevelUpCelebrationModal } from './components/summary/LevelUpCelebrationModal'
import { ProblemGrid } from './components/summary/ProblemGrid'
import { ProblemDetailModal } from './components/summary/ProblemDetailModal'
import { SummaryActionButtons } from './components/summary/SummaryActionButtons'

const SummaryPage = () => {
  const router = useRouter()
  const [filter, setFilter] = useState<FilterType>('all')
  const [selectedProblem, setSelectedProblem] = useState<ProblemResult | null>(null)
  const [showAchievements, setShowAchievements] = useState(false)
  const [showLevelUp, setShowLevelUp] = useState(true)

  const {
    sessionSummary,
    metrics,
    performanceByDifficulty,
    achievements,
    filteredProblems,
    levelUp,
  } = useSummaryData(filter)

  // Show achievements animation
  useEffect(() => {
    if (achievements.length > 0) {
      setTimeout(() => setShowAchievements(true), 1000)
    }
  }, [achievements.length])

  const handleBackToDashboard = () => {
    router.navigate('/')
  }

  const handlePracticeAgain = () => {
    if (sessionSummary?.user) {
      router.navigate('/practice', {
        user: sessionSummary.user.name,
        userId: String(sessionSummary.user.id),
        avatar: sessionSummary.user.avatar || '',
      })
    } else {
      router.navigate('/practice')
    }
  }

  const handleTryNextLevel = () => {
    if (sessionSummary?.user) {
      // Navigate to Journey page with Math Concepts tab selected and unlocked concepts filter
      router.navigate(`/journey/${sessionSummary.user.id}/concepts?status=unlocked`)
    }
  }

  const handleReviewFlagged = () => {
    setFilter('flagged')
  }

  if (!sessionSummary) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600 mb-4">No practice session data available.</p>
          <PillButton onClick={handleBackToDashboard} leftIcon={<Home className="h-4 w-4" />}>
            Back to Dashboard
          </PillButton>
        </div>
      </div>
    )
  }

  const studentName = sessionSummary.user?.name || 'Student'
  const level = sessionSummary.user?.level || 1
  const leveledUp = levelUp?.leveled_up === true

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <LevelUpCelebrationModal
          levelUp={levelUp}
          isOpen={showLevelUp && leveledUp}
          onClose={() => setShowLevelUp(false)}
        />
        <SummaryHeader studentName={studentName} level={level} onBackToDashboard={handleBackToDashboard} />

        <EncouragementBanner
          accuracy={metrics.accuracy}
          totalProblems={metrics.totalProblems}
          totalTime={metrics.totalTime}
          levelUp={levelUp}
        />

        <SummaryStatsCards metrics={metrics} />

        <div className="mb-8">
          <XPEarningsBreakdown levelUp={levelUp} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <PerformanceByDifficulty performanceByDifficulty={performanceByDifficulty} />
          <AchievementsSection achievements={achievements} showAchievements={showAchievements} />
          <SessionStats metrics={metrics} />
        </div>

        <ProblemGrid
          problems={filteredProblems}
          filter={filter}
          onFilterChange={setFilter}
          onProblemClick={setSelectedProblem}
        />

        <SummaryActionButtons
          sessionSummary={sessionSummary}
          metrics={metrics}
          levelUp={levelUp}
          onBackToDashboard={handleBackToDashboard}
          onPracticeAgain={handlePracticeAgain}
          onTryNextLevel={handleTryNextLevel}
          onReviewFlagged={handleReviewFlagged}
        />
      </div>

      <ProblemDetailModal problem={selectedProblem} onClose={() => setSelectedProblem(null)} />
    </div>
  )
}

export default SummaryPage
