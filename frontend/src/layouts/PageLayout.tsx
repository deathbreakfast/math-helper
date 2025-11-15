import { ReactNode } from 'react'
import { motion } from 'framer-motion'

type PageLayoutProps = {
  title: string
  subtitle?: string
  cta?: ReactNode
  children: ReactNode
}

const PageLayout = ({ title, subtitle, cta, children }: PageLayoutProps) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
        >
          <div>
            <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl">{title}</h1>
            {subtitle && <p className="mt-1 text-base text-slate-600">{subtitle}</p>}
          </div>
          {cta}
        </motion.div>

        {children}
      </div>
    </div>
  )
}

export default PageLayout

