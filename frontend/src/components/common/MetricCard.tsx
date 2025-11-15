import { motion } from 'framer-motion'
import type { ComponentType, SVGProps } from 'react'

type MetricCardProps = {
  label: string
  value: string | number
  icon: ComponentType<SVGProps<SVGSVGElement>>
  accentClass: string
  subtitle?: string
  index?: number
}

const MetricCard = ({ label, value, icon: Icon, accentClass, subtitle, index = 0 }: MetricCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.1 * (index + 1) }}
    className="rounded-2xl bg-white p-6 shadow-card"
  >
    <div className="mb-4 flex items-center gap-3">
      <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${accentClass}`}>
        <Icon className="h-6 w-6" />
      </div>
      <div className="text-sm font-semibold text-slate-500">{label}</div>
    </div>
    <div className="text-4xl font-bold text-slate-900">{value}</div>
    {subtitle && <div className="mt-2 text-sm text-slate-500">{subtitle}</div>}
  </motion.div>
)

export default MetricCard

