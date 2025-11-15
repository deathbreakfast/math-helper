export const gradientStops = {
  indigo: 'from-blue-500 to-purple-600',
  emerald: 'from-green-500 to-emerald-600',
  amber: 'from-amber-500 to-orange-500',
  rose: 'from-rose-500 to-pink-500',
} as const

export const softGradientStops = {
  neutral: 'from-white to-slate-50',
  indigo: 'from-blue-50 to-purple-50',
  emerald: 'from-emerald-50 to-green-50',
  amber: 'from-amber-50 to-orange-50',
  rose: 'from-rose-50 to-pink-50',
} as const

export type GradientTone = keyof typeof gradientStops
export type SoftTone = keyof typeof softGradientStops

export const accentText = {
  indigo: 'text-blue-600',
  emerald: 'text-emerald-600',
  amber: 'text-amber-600',
  rose: 'text-rose-600',
  slate: 'text-slate-700',
} as const

export const accentBg = {
  indigo: 'bg-blue-100',
  emerald: 'bg-emerald-100',
  amber: 'bg-amber-100',
  rose: 'bg-rose-100',
  slate: 'bg-slate-100',
} as const

export const accentBorder = {
  indigo: 'border-blue-200',
  emerald: 'border-emerald-200',
  amber: 'border-amber-200',
  rose: 'border-rose-200',
  slate: 'border-slate-200',
} as const

export const getGradientClass = (tone: GradientTone, direction: 'r' | 'br' = 'r') =>
  `bg-gradient-to-${direction} ${gradientStops[tone]}`

export const getSoftGradientClass = (tone: SoftTone = 'neutral', direction: 'r' | 'br' = 'r') =>
  `bg-gradient-to-${direction} ${softGradientStops[tone]}`


