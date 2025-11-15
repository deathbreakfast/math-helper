import type { ButtonHTMLAttributes, ReactNode } from 'react'

import { cn } from '../../utils/cn'
import { getGradientClass, type GradientTone } from '../../theme/tokens'

type PillButtonVariant = 'solid' | 'surface' | 'outline' | 'ghost'

type PillButtonProps = {
  variant?: PillButtonVariant
  tone?: GradientTone
  fullWidth?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  className?: string
  children: ReactNode
} & ButtonHTMLAttributes<HTMLButtonElement>

const baseClasses =
  'inline-flex items-center justify-center gap-2 rounded-2xl px-6 py-3 font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'

const solidToneClasses: Record<GradientTone, string> = {
  indigo: `${getGradientClass('indigo')} text-white shadow-lg hover:shadow-xl`,
  emerald: `${getGradientClass('emerald')} text-white shadow-lg hover:shadow-xl`,
  amber: `${getGradientClass('amber')} text-white shadow-lg hover:shadow-xl`,
  rose: `${getGradientClass('rose')} text-white shadow-lg hover:shadow-xl`,
}

const surfaceClasses =
  'bg-white text-slate-700 shadow-md hover:bg-slate-50 hover:shadow-lg border border-slate-200'

const outlineClasses =
  'border border-slate-300 text-slate-700 hover:border-slate-400 hover:bg-white/70'

const ghostClasses = 'text-slate-600 hover:bg-slate-100'

const variantMap: Record<PillButtonVariant, (tone: GradientTone) => string> = {
  solid: (tone) => solidToneClasses[tone],
  surface: () => surfaceClasses,
  outline: () => outlineClasses,
  ghost: () => ghostClasses,
}

const PillButton = ({
  variant = 'solid',
  tone = 'indigo',
  fullWidth,
  leftIcon,
  rightIcon,
  className,
  children,
  type = 'button',
  ...rest
}: PillButtonProps) => (
  <button
    type={type}
    className={cn(baseClasses, variantMap[variant](tone), fullWidth && 'w-full', className)}
    {...rest}
  >
    {leftIcon}
    {children}
    {rightIcon}
  </button>
)

export default PillButton


