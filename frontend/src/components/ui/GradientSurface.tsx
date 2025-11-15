import { forwardRef, type HTMLAttributes } from 'react'

import { cn } from '../../utils/cn'
import { getSoftGradientClass, type SoftTone } from '../../theme/tokens'

type SurfaceVariant = 'card' | 'soft' | 'glass'

type GradientSurfaceProps = {
  variant?: SurfaceVariant
  tone?: SoftTone
  className?: string
} & HTMLAttributes<HTMLDivElement>

const variantBase: Record<SurfaceVariant, string> = {
  card: 'rounded-3xl border border-slate-100 bg-white shadow-card',
  soft: 'rounded-3xl border border-slate-100 shadow-inner',
  glass: 'rounded-[32px] border border-white/30 bg-white/80 shadow-glass backdrop-blur',
}

const GradientSurface = forwardRef<HTMLDivElement, GradientSurfaceProps>(
  ({ variant = 'card', tone = 'neutral', className, children, ...rest }, ref) => {
    const toneClass = variant === 'soft' ? getSoftGradientClass(tone, 'r') : ''

    return (
      <div ref={ref} className={cn(variantBase[variant], toneClass, className)} {...rest}>
        {children}
      </div>
    )
  },
)

GradientSurface.displayName = 'GradientSurface'

export default GradientSurface


