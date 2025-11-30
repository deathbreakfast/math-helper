import { ReactNode } from 'react'
import { motion } from 'framer-motion'

type LearnerDetailLayoutProps = {
  title: string
  action: ReactNode
  children: ReactNode
}

const LearnerDetailLayout = ({ title, action, children }: LearnerDetailLayoutProps) => {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-10 space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <h2 className="text-2xl font-semibold text-slate-900" data-testid="testid-learner-progress-title">{title}</h2>
        {action}
      </div>
      {children}
    </motion.div>
  )
}

export default LearnerDetailLayout

