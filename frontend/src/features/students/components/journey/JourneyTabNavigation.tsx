import { TrendingUp, Award, Crown, FileText } from 'lucide-react'

export type TabId = 'overview' | 'achievements' | 'levels' | 'tests'

type JourneyTabNavigationProps = {
  activeTab: TabId
  onTabChange: (tab: TabId) => void
}

export const JourneyTabNavigation = ({ activeTab, onTabChange }: JourneyTabNavigationProps) => {
  const tabs = [
    {
      id: 'overview' as TabId,
      label: 'Overview',
      icon: TrendingUp,
    },
    {
      id: 'achievements' as TabId,
      label: 'All Achievements',
      icon: Award,
    },
    {
      id: 'levels' as TabId,
      label: 'Level Requirements',
      icon: Crown,
    },
    {
      id: 'tests' as TabId,
      label: 'Tests',
      icon: FileText,
    },
  ]

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

