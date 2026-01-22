import { Link, useSearchParams } from 'react-router-dom'
import { TrendingUp, Network, Trophy } from 'lucide-react'

export type TabId = 'overview' | 'achievements' | 'math-types'

type JourneyTabNavigationProps = {
  activeTab: TabId
  onTabChange?: (tab: TabId) => void
  userId: string
}

export const JourneyTabNavigation = ({ activeTab, onTabChange, userId }: JourneyTabNavigationProps) => {
  const [searchParams] = useSearchParams()
  const queryString = searchParams.toString() ? `?${searchParams.toString()}` : ''
  
  const tabs = [
    {
      id: 'overview' as TabId,
      label: 'Overview',
      icon: TrendingUp,
    },
    {
      id: 'achievements' as TabId,
      label: 'Achievements',
      icon: Trophy,
    },
    {
      id: 'math-types' as TabId,
      label: 'Math Types',
      icon: Network,
    },
  ]

  // If onTabChange is provided, use it (for modal)
  // Otherwise, use Link components (for route-based navigation)
  if (onTabChange) {
    return (
      <div className="mb-8 flex flex-wrap gap-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            data-testid={`testid-journey-tab-${tab.id}`}
            onClick={() => onTabChange(tab.id)}
            className={`flex items-center gap-2 rounded-xl px-6 py-3 font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 shadow hover:bg-gray-50'
            }`}
          >
            <tab.icon className="h-5 w-5" />
            {tab.label}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="mb-8 flex flex-wrap gap-4">
      {tabs.map((tab) => {
        const to = `/journey/${userId}/${tab.id}${queryString}`
        return (
          <Link
            key={tab.id}
            to={to}
            data-testid={`testid-journey-tab-${tab.id}`}
            className={`flex items-center gap-2 rounded-xl px-6 py-3 font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                : 'bg-white text-gray-700 shadow hover:bg-gray-50'
            }`}
          >
            <tab.icon className="h-5 w-5" />
            {tab.label}
          </Link>
        )
      })}
    </div>
  )
}

