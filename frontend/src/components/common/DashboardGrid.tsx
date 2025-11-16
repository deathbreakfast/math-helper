import { ReactNode, createContext, useContext } from 'react'

type GridSpan = {
  base?: number
  sm?: number
  md?: number
  lg?: number
  xl?: number
}

const GridItemContext = createContext<GridSpan | null>(null)

type DashboardGridProps = {
  children: ReactNode
  className?: string
}

export const DashboardGrid = ({ children, className = '' }: DashboardGridProps) => {
  return (
    <div className={`grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 ${className}`}>
      {children}
    </div>
  )
}

type DashboardGridItemProps = {
  children: ReactNode
  span?: GridSpan
  className?: string
}

export const DashboardGridItem = ({ children, span, className = '' }: DashboardGridItemProps) => {
  const getSpanClasses = (s?: GridSpan) => {
    if (!s) return ''
    const classes: string[] = []
    if (s.base) classes.push(`col-span-${s.base}`)
    if (s.sm) classes.push(`sm:col-span-${s.sm}`)
    if (s.md) classes.push(`md:col-span-${s.md}`)
    if (s.lg) classes.push(`lg:col-span-${s.lg}`)
    if (s.xl) classes.push(`xl:col-span-${s.xl}`)
    return classes.join(' ')
  }

  return <div className={`${getSpanClasses(span)} ${className}`}>{children}</div>
}

