import { ReactNode } from 'react'

type SectionHeaderProps = {
  title: string
  children?: ReactNode
  className?: string
}

const SectionHeader = ({ title, children, className = '' }: SectionHeaderProps) => {
  return (
    <div className={`mb-6 flex items-center justify-between ${className}`}>
      <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
      {children}
    </div>
  )
}

export default SectionHeader

