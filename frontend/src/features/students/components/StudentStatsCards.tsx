import { Clock, Target, TrendingUp, Zap } from 'lucide-react'
import { StatCard } from '../../../components/ui'
import type { User } from '../hooks/useStudents'

type Props = {
  user: User
}

const StudentStatsCards = ({ user }: Props) => {
  const stats = [
    {
      label: 'Current Level',
      value: user.level,
      icon: Target,
      tone: 'indigo',
      subtitle: 'Multi-digit operations',
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
      {stats.map((stat, idx) => (
        <StatCard
          key={stat.label}
          label={stat.label}
          value={stat.value}
          icon={stat.icon}
          subtitle={stat.subtitle}
          tone={stat.tone}
          index={idx}
        />
      ))}
    </div>
  )
}

export default StudentStatsCards

