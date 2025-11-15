import type { PracticeSessionSummary } from '../types'

type SessionSummaryProps = {
  sessionSummary: PracticeSessionSummary | null
}

const SessionSummary = ({ sessionSummary }: SessionSummaryProps) => {
  if (!sessionSummary) {
    return null
  }

  return (
    <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-inner">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm uppercase text-slate-400">Session summary</p>
          <h4 className="text-2xl font-semibold text-slate-900">{sessionSummary.id}</h4>
          <p className="text-xs text-slate-500">
            Submitted at {new Date(sessionSummary.submittedAt).toLocaleTimeString()}
          </p>
        </div>
        <div className="flex gap-4">
          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-2 text-center">
            <p className="text-xs uppercase text-slate-500">Accuracy</p>
            <p className="text-2xl font-bold text-slate-900">{sessionSummary.totals.accuracy}%</p>
          </div>
          <div className="rounded-2xl border border-slate-100 bg-slate-50 px-4 py-2 text-center">
            <p className="text-xs uppercase text-slate-500">Correct</p>
            <p className="text-2xl font-bold text-slate-900">
              {sessionSummary.totals.correct}/{sessionSummary.totals.questions}
            </p>
          </div>
        </div>
      </div>
      <div className="mt-6 space-y-3">
        {sessionSummary.attempts.map((attempt) => (
          <div
            key={attempt.questionId}
            className="flex flex-col gap-2 rounded-2xl border border-slate-100 bg-slate-50 p-4 text-sm text-slate-600 md:flex-row md:items-center md:justify-between"
          >
            <div>
              <p className="font-semibold text-slate-900">{attempt.prompt}</p>
              <p className="text-xs text-slate-500">
                Your answer: {attempt.submittedAnswer || '—'} · Correct answer: {attempt.correctAnswer}
              </p>
            </div>
            <div
              className={`rounded-2xl px-4 py-2 text-sm font-semibold ${
                attempt.isCorrect ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
              }`}
            >
              {attempt.isCorrect ? 'Correct' : 'Try again'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SessionSummary

