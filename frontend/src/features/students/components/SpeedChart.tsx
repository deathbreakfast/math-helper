import { motion } from 'framer-motion'
import { useMemo } from 'react'
import { Filter } from 'lucide-react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipProps,
} from 'recharts'
import SectionHeader from '../../../components/common/SectionHeader'
import type { User } from '../hooks/useStudents'
import { generateSpeedHistory } from '../utils/timeSeries'

type Props = {
  user: User
  filterLevel: string
  onFilterChange: (level: string) => void
}

const speedSeries = [
  { key: 'addition', label: 'Addition', color: '#3b82f6' },
  { key: 'subtraction', label: 'Subtraction', color: '#a855f7' },
  { key: 'multiplication', label: 'Multiplication', color: '#22c55e' },
  { key: 'division', label: 'Division', color: '#f97316' },
] as const

type CustomTooltipProps = TooltipProps<number, string> & {
  formatValue: (value: number) => string
}

const CustomTooltip = ({ active, payload, label, formatValue }: CustomTooltipProps) => {
  if (!active || !payload || payload.length === 0) {
    return null
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white/95 p-4 shadow-lg backdrop-blur">
      <p className="mb-2 text-sm font-semibold text-slate-900">{label}</p>
      <div className="space-y-1">
        {payload.map((entry) => {
          if (!entry.value && entry.value !== 0) return null
          return (
            <div key={entry.name} className="flex items-center gap-2 text-sm text-slate-700">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: entry.color || '#0f172a' }}
              />
              <span className="flex-1">{entry.name}</span>
              <span className="font-semibold text-slate-900">
                {formatValue(typeof entry.value === 'number' ? entry.value : Number(entry.value))}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

const SpeedChart = ({ user, filterLevel, onFilterChange }: Props) => {
  const speedHistory = useMemo(() => generateSpeedHistory(user), [user])

  return (
    <motion.div
      initial={{ opacity: 0, x: 0 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-2xl bg-white p-6 shadow-card"
    >
      <SectionHeader
        title="Speed by operation"
        className="items-center"
      >
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Filter className="h-4 w-4" />
          <select
            value={filterLevel}
            onChange={(event) => onFilterChange(event.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="all">All levels</option>
            <option value="1">Level 1</option>
            <option value="2">Level 2</option>
            <option value="3">Level 3</option>
            <option value="4">Level 4</option>
            <option value="5">Level 5+</option>
          </select>
        </div>
      </SectionHeader>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={speedHistory}>
            <CartesianGrid strokeDasharray="4 4" stroke="#e2e8f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: '#64748b' }}
              stroke="#cbd5f5"
              tickLine={false}
              axisLine={{ stroke: '#cbd5f5' }}
            />
            <YAxis
              domain={[0, 10]}
              ticks={[0, 2, 4, 6, 8, 10]}
              tick={{ fontSize: 12, fill: '#64748b' }}
              stroke="#cbd5f5"
              axisLine={{ stroke: '#cbd5f5' }}
              tickLine={false}
              label={{
                value: 'Speed (seconds)',
                angle: -90,
                position: 'insideLeft',
                style: { fontSize: 12, fill: '#94a3b8' },
              }}
            />
            <Tooltip content={<CustomTooltip formatValue={(value) => `${value.toFixed(1)}s`} />} />
            <Legend
              wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
              iconType="plainline"
              verticalAlign="bottom"
            />
            {speedSeries.map((series, index) => (
              <Line
                key={series.key}
                type="monotone"
                dataKey={series.key}
                stroke={series.color}
                name={series.label}
                strokeWidth={2}
                dot={{
                  r: 4,
                  strokeWidth: 2,
                  stroke: '#fff',
                  fill: series.color,
                }}
                animationDuration={1200}
                animationBegin={index * 150}
                activeDot={{ r: 6 }}
                isAnimationActive
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}

export default SpeedChart

