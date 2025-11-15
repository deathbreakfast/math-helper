import { motion } from 'framer-motion'
import type { ComponentType, HTMLAttributes, SVGProps } from 'react'

import { cn } from '../../utils/cn'
import { accentBg, accentText } from '../../theme/tokens'
import GradientSurface from './GradientSurface'

type StatTone = keyof typeof accentBg

type StatCardProps = {
  label: string
  value: string | number
  icon: ComponentType<SVGProps<SVGSVGElement>>
  subtitle?: string
  tone?: StatTone
  index?: number
} & HTMLAttributes<HTMLDivElement>

const StatCard = ({
  label,
  value,
  icon: Icon,
  subtitle,
  tone = 'indigo',
  index = 0,
  className,
  ...rest
}: StatCardProps) => (
  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 * index }}>
    <GradientSurface variant="card" className={cn('p-6', className)} {...rest}>
      <div className="mb-4 flex items-center gap-3">
        <div className={cn('flex h-12 w-12 items-center justify-center rounded-xl', accentBg[tone], accentText[tone])}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="text-sm font-semibold text-slate-500">{label}</div>
      </div>
      <div className="text-4xl font-bold text-slate-900">{value}</div>
      {subtitle && <div className="mt-2 text-sm text-slate-500">{subtitle}</div>}
    </GradientSurface>
  </motion.div>
)

export default StatCard


