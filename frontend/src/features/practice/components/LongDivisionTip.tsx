import { motion } from 'framer-motion'
import { Info, Lightbulb } from 'lucide-react'
import type { TipConfig } from '../types'

type LongDivisionTipProps = {
  tip?: TipConfig
}

export const LongDivisionTip = ({ tip }: LongDivisionTipProps) => {
  if (!tip) return null

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
      <div className="rounded-2xl border border-orange-100 bg-gradient-to-r from-orange-50 to-amber-50 p-5 shadow-inner">
        <p className="mb-2 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-orange-600">
          {tip.icon === 'info' ? <Info className="h-4 w-4" /> : <Lightbulb className="h-4 w-4" />}
          {tip.title ?? 'Tip'}
        </p>
        <p className="text-sm text-orange-800 leading-relaxed">{tip.body}</p>
      </div>
    </motion.div>
  )
}

