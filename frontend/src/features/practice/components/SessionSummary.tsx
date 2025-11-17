import { Clock } from 'lucide-react'
import type { PracticeSessionSummary } from '../types'

type SessionSummaryProps = {
  sessionSummary: PracticeSessionSummary | null
  showHeader?: boolean
}

const SessionSummary = ({ sessionSummary, showHeader = true }: SessionSummaryProps) => {
  if (!sessionSummary) {
    return null
  }

  const formatTime = (ms?: number) => {
    if (!ms) return '—'
    const seconds = Math.round(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-inner">
      {showHeader && (
        <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm uppercase text-slate-400">Session details</p>
            <h4 className="text-2xl font-semibold text-slate-900">Session {sessionSummary.id}</h4>
            <p className="text-xs text-slate-500">
              Completed at {new Date(sessionSummary.submittedAt).toLocaleString()}
            </p>
          </div>
          {sessionSummary.message && (
            <div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-4 py-2">
              <p className="text-sm text-indigo-700">{sessionSummary.message}</p>
            </div>
          )}
        </div>
      )}
      <div className="space-y-3">
        <h5 className="text-lg font-semibold text-slate-900">Question Results</h5>
        {sessionSummary.attempts.map((attempt, index) => (
          <div
            key={attempt.questionId || index}
            className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-slate-50 p-4 text-sm text-slate-600 transition hover:border-slate-200 hover:shadow-sm md:flex-row md:items-center md:justify-between"
          >
            <div className="flex-1">
              <div className="mb-1 flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-400">#{index + 1}</span>
                <p className="font-semibold text-slate-900">{attempt.prompt}</p>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                <span>
                  <span className="font-medium">Your answer:</span> {attempt.submittedAnswer || '—'}
                </span>
                <span className="text-slate-300">·</span>
                <span>
                  <span className="font-medium">Correct answer:</span> {attempt.correctAnswer}
                </span>
                {attempt.elapsedMs && (
                  <>
                    <span className="text-slate-300">·</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTime(attempt.elapsedMs)}
                    </span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              {attempt.awardedPoints > 0 && (
                <div className="text-xs font-semibold text-amber-600">+{attempt.awardedPoints} pts</div>
              )}
              <div
                className={`rounded-xl px-4 py-2 text-sm font-semibold ${
                  attempt.isCorrect
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-rose-100 text-rose-700'
                }`}
              >
                {attempt.isCorrect ? '✓ Correct' : '✗ Incorrect'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SessionSummary

