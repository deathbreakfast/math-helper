import { Clock, Target, TrendingUp, Zap } from 'lucide-react'
import MetricCard from '../../../components/common/MetricCard'
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
      accent: 'bg-blue-100 text-blue-600',
      subtitle: 'Multi-digit operations',
    },
    {
      label: 'Questions Answered',
      value: user.questionsAnswered,
      icon: TrendingUp,
      accent: 'bg-purple-100 text-purple-600',
      subtitle: user.weeklyGain ? `+${user.weeklyGain} this week` : 'Keep the momentum going',
    },
    {
      label: 'Avg Speed',
      value: `${user.averageSpeed}s`,
      icon: Clock,
      accent: 'bg-green-100 text-green-600',
      subtitle: 'Per question',
    },
    {
      label: 'Current Streak',
      value: user.stats.currentStreak,
      icon: Zap,
      accent: 'bg-orange-100 text-orange-600',
      subtitle: `Best: ${user.stats.bestStreak} days`,
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, idx) => (
        <MetricCard
          key={stat.label}
          label={stat.label}
          value={stat.value}
          icon={stat.icon}
          accentClass={stat.accent}
          subtitle={stat.subtitle}
          index={idx}
        />
      ))}
    </div>
  )
}

export default StudentStatsCards

