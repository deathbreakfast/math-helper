/* eslint-disable react-refresh/only-export-components */
import type { ComponentType } from 'react'

import type {
  AnswerFormat,
  PracticeQuestion,
  ProblemLayoutType,
  WorkStep,
} from '../types'

type ProblemLayoutProps = {
  question: PracticeQuestion
  answerFormat?: AnswerFormat
  showWork?: boolean
  workSteps?: WorkStep[]
}

const VerticalStackLayout = ({ question }: ProblemLayoutProps) => (
  <div className="text-center text-slate-900">
    <div className="text-7xl font-bold leading-tight">{question.operand1}</div>
    <div className="text-5xl font-bold text-slate-500">
      {question.operation === 'addition'
        ? '+'
        : question.operation === 'subtraction'
          ? '−'
          : question.operation === 'multiplication'
            ? '×'
            : '÷'}
    </div>
    <div className="text-7xl font-bold leading-tight">{question.operand2}</div>
  </div>
)

const PlaceholderLayout = ({ question }: ProblemLayoutProps) => (
  <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
    <p>{question.prompt}</p>
    <p className="mt-2 text-xs uppercase tracking-wide text-slate-400">Layout placeholder</p>
  </div>
)

const layoutComponents: Record<ProblemLayoutType, ComponentType<ProblemLayoutProps>> = {
  vertical: VerticalStackLayout,
  horizontal: PlaceholderLayout,
  longDivision: PlaceholderLayout,
  work: PlaceholderLayout,
}

export const renderProblemLayout = (type: ProblemLayoutType, props: ProblemLayoutProps) => {
  const Component = layoutComponents[type] ?? VerticalStackLayout
  return <Component {...props} />
}

export type { ProblemLayoutProps }


