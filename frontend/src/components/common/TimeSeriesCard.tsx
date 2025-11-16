import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { Filter } from 'lucide-react'
import SectionHeader from './SectionHeader'

type TimeSeriesCardProps = {
  title: string
  yLabel: string
  yDomain: [number, number]
  yTicks?: number[]
  filterControls?: ReactNode
  children: ReactNode
  className?: string
}

export const TimeSeriesCard = ({
  title,
  yLabel,
  yDomain,
  yTicks,
  filterControls,
  children,
  className = '',
}: TimeSeriesCardProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.4 }}
      className={`rounded-2xl bg-white p-6 shadow-card ${className}`}
    >
      <SectionHeader title={title} className="items-center">
        {filterControls && (
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Filter className="h-4 w-4" />
            {filterControls}
          </div>
        )}
      </SectionHeader>

      <div className="h-72">{children}</div>
    </motion.div>
  )
}

