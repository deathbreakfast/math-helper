import { useEffect } from 'react'
import { useParams, useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { LevelProgressionSystem } from '../components/LevelProgressionSystem'
import { mapUserToProgressData } from '../utils/progressMapping'
import { useLearners } from '../hooks/useLearners'
import { useAchievementDefinitions } from '../../../lib/levels/hooks'
import type { TabId } from '../components/journey/JourneyTabNavigation'
import { logError } from '../../../utils/logger'

const JourneyPage = () => {
  const { userId, tab } = useParams<{ userId: string; tab?: TabId }>()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const { state: { users, isLoadingUsers, isLoadingFullData }, actions: { fetchUserFullData } } = useLearners()

  // Find the user by ID
  const user = users.find((u) => u.id === userId) || null

  const { definitions: achievementDefinitions } = useAchievementDefinitions()
  const userProgressData = user ? mapUserToProgressData(user, undefined, achievementDefinitions) : undefined

  // Redirect to add tab if missing (preserve query params)
  useEffect(() => {
    if (!isLoadingUsers && userId && user && !tab) {
      // No tab in URL, redirect to overview tab with query params preserved
      const queryString = searchParams.toString() ? `?${searchParams.toString()}` : ''
      navigate(`/journey/${userId}/overview${queryString}`, { replace: true })
    }
  }, [userId, user, tab, isLoadingUsers, navigate, searchParams])

  // Redirect if user not found and users are loaded
  useEffect(() => {
    if (!isLoadingUsers && userId && users.length > 0 && !user) {
      // User not found, redirect to dashboard
      navigate('/', { replace: true })
    }
  }, [userId, user, users, isLoadingUsers, navigate])

  // Always refetch full user data when journey page loads to ensure latest achievements are loaded
  // This is especially important after completing a practice session
  // Use location.pathname as dependency to ensure refetch on every navigation (even to same user)
  useEffect(() => {
    if (userId && fetchUserFullData) {
      // Always refetch when navigating to journey page to get latest achievements
      // This ensures achievements earned in the current session are displayed immediately
      fetchUserFullData(userId).catch((error) => {
        logError('Failed to fetch full user data:', error)
      })
    }
  }, [userId, fetchUserFullData, location.pathname])

  // Handle back navigation
  const handleBack = () => {
    navigate('/')
  }

  // Determine if we're waiting for achievements to load
  // We show loading if:
  // 1. Users are still loading
  // 2. OR we're currently fetching full data for this user
  const isLoading = isLoadingUsers || (isLoadingFullData && userId)

  if (isLoadingUsers) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <span className="text-gray-600">Loading...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <div className="text-center">
          <p className="text-slate-600 mb-4">User not found.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <LevelProgressionSystem 
        userData={userProgressData} 
        user={user} 
        onBack={handleBack}
        initialTab={tab || 'overview'}
        searchParams={searchParams}
      />
    </div>
  )
}

export default JourneyPage

