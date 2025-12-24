import { Clock, Target, TrendingUp, Zap, ExternalLink } from 'lucide-react'
import { StatCard } from '../../../components/ui'
import { cn } from '../../../utils/cn'
import type { User } from '../hooks/useLearners'

type Props = {
  user: User
  onLevelCardClick?: () => void
}

const LearnerStatsCards = ({ user, onLevelCardClick }: Props) => {
  const stats = [
    {
      label: 'Current Level',
      value: user.level,
      icon: Target,
      tone: 'amber',
      subtitle: 'Select here to explore your journey',
      onClick: onLevelCardClick,
      actionButton: onLevelCardClick ? (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onLevelCardClick()
          }}
          className="absolute right-4 top-4 rounded-lg bg-gradient-to-r from-yellow-400 to-yellow-600 p-2 text-white shadow-md transition-all hover:scale-110 hover:shadow-lg"
          aria-label="View Journey"
        >
          <ExternalLink className="h-5 w-5" />
        </button>
      ) : undefined,
    },
    {
      label: 'Questions Answered',
      value: user.questionsAnswered,
      icon: TrendingUp,
      tone: 'rose',
      subtitle: user.weeklyGain ? `+${user.weeklyGain} this week` : 'Keep the momentum going',
    },
    {
      label: 'Avg Speed',
      value: `${user.averageSpeed}s`,
      icon: Clock,
      tone: 'emerald',
      subtitle: 'Per question',
    },
    {
      label: 'Current Streak',
      value: user.stats.currentStreak,
      icon: Zap,
      tone: 'amber',
      subtitle: `Best: ${user.stats.bestStreak} days`,
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, idx) => {
        const isLevelCard = stat.label === 'Current Level'
        return (
          <div key={stat.label} className="relative" data-testid={isLevelCard ? 'testid-level-card' : undefined}>
            <StatCard
              label={stat.label}
              value={stat.value}
              icon={stat.icon}
              subtitle={stat.subtitle}
              tone={stat.tone as 'amber' | 'rose' | 'emerald' | 'indigo' | 'slate'}
              index={idx}
              onClick={stat.onClick}
              className={cn(
                stat.onClick ? 'cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl' : '',
                isLevelCard ? 'bg-gradient-to-br from-yellow-50 to-amber-50 border-yellow-200' : '',
              )}
            />
            {stat.actionButton}
          </div>
        )
      })}
    </div>
  )
}

export default LearnerStatsCards

