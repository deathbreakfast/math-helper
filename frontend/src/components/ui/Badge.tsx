import type { HTMLAttributes } from 'react'

import { cn } from '../../utils/cn'
import { accentBg, accentBorder, accentText } from '../../theme/tokens'

type BadgeTone = keyof typeof accentBg
type BadgeVariant = 'solid' | 'soft' | 'outline'

type BadgeProps = {
  tone?: BadgeTone
  variant?: BadgeVariant
  className?: string
} & HTMLAttributes<HTMLSpanElement>

const variantClassMap: Record<BadgeVariant, (tone: BadgeTone) => string> = {
  solid: (tone) => `${accentBg[tone]} ${accentText[tone]}`,
  soft: (tone) => `${accentBg[tone]} ${accentText[tone]} bg-opacity-60`,
  outline: (tone) => `${accentBorder[tone]} ${accentText[tone]} border`,
}

const Badge = ({ tone = 'amber', variant = 'solid', className, children, ...rest }: BadgeProps) => (
  <span
    className={cn(
      'inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide',
      variantClassMap[variant](tone),
      className,
    )}
    {...rest}
  >
    {children}
  </span>
)

export default Badge


