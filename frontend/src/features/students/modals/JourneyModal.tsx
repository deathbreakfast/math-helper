import { useSearchParams } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import ModalShell from '../../../components/ModalShell'
import { LevelProgressionSystem } from '../components/LevelProgressionSystem'
import { mapUserToProgressData } from '../utils/progressMapping'
import type { User } from '../hooks/useLearners'
import { useLevelRequirements, useAchievementDefinitions } from '../../../lib/levels/hooks'

type JourneyModalProps = {
  isOpen: boolean
  onClose: () => void
  user: User | null
  isLoadingFullData?: boolean
}

const JourneyModal = ({ isOpen, onClose, user, isLoadingFullData = false }: JourneyModalProps) => {
  // Get current search params to preserve dev mode and other context params
  const [searchParams] = useSearchParams()
  
  // Don't fetch level requirements on mount - will be lazy loaded when Levels tab is opened
  const { requirements: levelRequirementsCache } = useLevelRequirements(user?.level ? user.level + 2 : 45, false)
  const { definitions: achievementDefinitions } = useAchievementDefinitions()
  const userProgressData = user ? mapUserToProgressData(user, levelRequirementsCache, achievementDefinitions) : undefined

  // Determine if we're waiting for achievements to load
  // We show loading if:
  // 1. isLoadingFullData is true (fetch is in progress)
  // 2. AND user exists
  // 3. AND user has no achievements (empty array)
  // 
  // Note: mapApiLearner always creates an achievements array (empty for minimal data)
  // So we can't distinguish minimal data from full data with no achievements from the object alone
  // We rely on isLoadingFullData to tell us if we're currently fetching
  // Once loading completes, if achievements is still empty, the user legitimately has none
  const isWaitingForAchievements = isLoadingFullData && user && (!user.achievements || user.achievements.length === 0)


  return (
    <ModalShell
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="xl"
      paddingClassName="p-0"
      showCloseButton={false}
      cardClassName="max-h-[90vh] overflow-hidden"
      overlayClassName="bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50"
    >
      <div className="max-h-[90vh] overflow-y-auto">
        {isWaitingForAchievements ? (
          <div className="flex min-h-[400px] items-center justify-center py-12">
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <span className="text-gray-600">Loading achievements...</span>
            </div>
          </div>
        ) : (
          <LevelProgressionSystem 
            userData={userProgressData} 
            user={user} 
            onBack={onClose}
            searchParams={searchParams}
          />
        )}
      </div>
    </ModalShell>
  )
}

export default JourneyModal

