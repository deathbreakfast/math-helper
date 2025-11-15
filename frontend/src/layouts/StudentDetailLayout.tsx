import { ReactNode } from 'react'
import { motion } from 'framer-motion'

type StudentDetailLayoutProps = {
  title: string
  action: ReactNode
  children: ReactNode
}

const StudentDetailLayout = ({ title, action, children }: StudentDetailLayoutProps) => {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-10 space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>
        {action}
      </div>
      {children}
    </motion.div>
  )
}

export default StudentDetailLayout

