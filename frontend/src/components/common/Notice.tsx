import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, Info, Lightbulb, XCircle } from 'lucide-react'

export type NoticeVariant = 'info' | 'warning' | 'success' | 'error'

export type NoticeTone = 'indigo' | 'blue' | 'orange' | 'emerald' | 'rose'

type NoticeProps = {
  variant?: NoticeVariant
  tone?: NoticeTone
  icon?: 'info' | 'lightbulb' | 'check' | 'alert' | 'error' | React.ReactNode
  title?: string
  body: string
  className?: string
}

const toneClasses: Record<NoticeTone, { container: string; icon: string }> = {
  indigo: {
    container: 'bg-indigo-50 border-indigo-200 text-indigo-900',
    icon: 'text-indigo-600',
  },
  blue: {
    container: 'bg-blue-50 border-blue-200 text-blue-900',
    icon: 'text-blue-600',
  },
  orange: {
    container: 'bg-orange-50 border-orange-200 text-orange-900',
    icon: 'text-orange-600',
  },
  emerald: {
    container: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    icon: 'text-emerald-600',
  },
  rose: {
    container: 'bg-rose-50 border-rose-200 text-rose-900',
    icon: 'text-rose-600',
  },
}

const variantDefaults: Record<NoticeVariant, { tone: NoticeTone; icon: 'info' | 'lightbulb' | 'check' | 'alert' | 'error' }> = {
  info: { tone: 'blue', icon: 'info' },
  warning: { tone: 'orange', icon: 'alert' },
  success: { tone: 'emerald', icon: 'check' },
  error: { tone: 'rose', icon: 'error' },
}

const NoticeIcon = ({ icon }: { icon: NoticeProps['icon'] }) => {
  if (typeof icon === 'string') {
    switch (icon) {
      case 'info':
        return <Info className="w-5 h-5" />
      case 'lightbulb':
        return <Lightbulb className="w-5 h-5" />
      case 'check':
        return <CheckCircle className="w-5 h-5" />
      case 'alert':
        return <AlertTriangle className="w-5 h-5" />
      case 'error':
        return <XCircle className="w-5 h-5" />
      default:
        return <Info className="w-5 h-5" />
    }
  }
  return icon as React.ReactElement
}

export const Notice = ({ variant = 'info', tone, icon, title, body, className = '' }: NoticeProps) => {
  const defaults = variantDefaults[variant]
  const finalTone = tone ?? defaults.tone
  const finalIcon = icon ?? defaults.icon
  const toneStyle = toneClasses[finalTone]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-2xl border p-4 flex items-start gap-3 ${toneStyle.container} ${className}`}
    >
      <div className={`flex h-11 w-11 items-center justify-center rounded-2xl bg-white/80 ${toneStyle.icon}`}>
        <NoticeIcon icon={finalIcon} />
      </div>
      <div>
        {title && <p className="text-sm font-semibold uppercase tracking-wide">{title}</p>}
        <p className="text-sm leading-relaxed">{body}</p>
      </div>
    </motion.div>
  )
}

