import { Check } from 'lucide-react'
import type { PracticeQuestion } from '../types'

type ProgressOverviewProps = {
  questions: PracticeQuestion[]
  currentQuestionIndex: number
  practiceAnswers: Record<string, string>
  onSelectQuestion: (index: number) => void
}

const ProgressOverview = ({
  questions,
  currentQuestionIndex,
  practiceAnswers,
  onSelectQuestion,
}: ProgressOverviewProps) => (
  <div className="mt-6 rounded-3xl border border-slate-100 bg-white p-6 shadow-inner">
    <div className="flex flex-wrap gap-3">
      {questions.map((question, index) => {
        const isCurrent = index === currentQuestionIndex
        const isAnswered = (practiceAnswers[question.id] || '').trim().length > 0
        return (
          <button
            key={question.id}
            type="button"
            onClick={() => onSelectQuestion(index)}
            className={`flex h-12 w-12 items-center justify-center rounded-2xl border text-sm font-semibold transition ${
              isCurrent
                ? 'border-blue-500 bg-blue-500 text-white'
                : isAnswered
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                  : 'border-slate-200 bg-white text-slate-500'
            }`}
            aria-label={`Go to card ${index + 1}`}
          >
            {isAnswered ? <Check className="h-4 w-4" /> : index + 1}
          </button>
        )
      })}
    </div>
  </div>
)

export default ProgressOverview

