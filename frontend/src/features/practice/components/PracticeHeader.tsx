import { Award, Home } from 'lucide-react'
import type { PracticeQuestion, User } from '../types'
import { Badge } from '../../../components/ui'

type PracticeHeaderProps = {
  selectedUser: User | null
  cardCounterDisplay: string
  currentQuestion?: PracticeQuestion
  progressPercent: number
  isTest?: boolean
}

const PracticeHeader = ({
  selectedUser,
  cardCounterDisplay,
  currentQuestion,
  progressPercent,
  isTest = false,
}: PracticeHeaderProps) => {
  const learnerLabel = selectedUser
    ? `${selectedUser.name} • Level ${selectedUser.level ?? 1}`
    : 'Share a learner link to begin'

  const operationLabel = currentQuestion
    ? currentQuestion.operation.charAt(0).toUpperCase() + currentQuestion.operation.slice(1)
    : null

  return (
    <header className="mb-10 w-full space-y-4">
      <div className="flex w-full flex-col gap-3">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-3">
            <a
              href="/"
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
            >
              <Home className="h-4 w-4" />
              Dashboard
            </a>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">{isTest ? 'Math Test' : 'Math Practice'}</h1>
              <p className="text-base text-slate-600">{learnerLabel}</p>
            </div>
          </div>
          <div className="text-right space-y-2">
            <p className="text-3xl font-bold text-slate-900">{cardCounterDisplay}</p>
            {currentQuestion && (
              <div className="flex flex-col items-end gap-1 text-right">
                <Badge tone="amber" className="text-xs">
                  <Award className="h-3 w-3" />
                  {operationLabel}
                </Badge>
                {currentQuestion.mathTypeLabel && (
                  <span className="text-xs font-semibold uppercase tracking-wide text-indigo-500">
                    {currentQuestion.mathTypeLabel}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-white shadow-inner">
          <div
            data-testid="testid-progress-bar"
            className="h-full rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all"
            style={{ width: `${Math.min(Math.max(progressPercent, 0), 100)}%` }}
          />
        </div>
      </div>
    </header>
  )
}

export default PracticeHeader

