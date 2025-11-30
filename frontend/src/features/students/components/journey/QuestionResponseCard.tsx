import React from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, Clock } from 'lucide-react'

type QuestionResponse = {
  question_id: number
  prompt: string
  correct_answer: string
  user_answer: string
  is_correct: boolean
  time_taken_ms: number
  answered_at: string | null
}

type QuestionResponseCardProps = {
  question: QuestionResponse
  index: number
}

const formatTime = (ms: number): string => {
  const seconds = ms / 1000
  return `${seconds.toFixed(1)}s`
}

export const QuestionResponseCard: React.FC<QuestionResponseCardProps> = ({ question, index }) => {
  return (
    <motion.div
      data-testid={`testid-question-response-${question.question_id}`}
      initial={{
        opacity: 0,
        x: -20,
      }}
      animate={{
        opacity: 1,
        x: 0,
      }}
      transition={{
        delay: index * 0.02,
      }}
      className={`rounded-lg border-2 p-3 ${
        question.is_correct
          ? 'border-green-300 bg-green-50'
          : 'border-red-300 bg-red-50'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Correct/Incorrect Indicator */}
        <div className="mt-1 flex-shrink-0">
          {question.is_correct ? (
            <CheckCircle className="h-5 w-5 text-green-500" data-testid="testid-question-correct" />
          ) : (
            <XCircle className="h-5 w-5 text-red-500" data-testid="testid-question-incorrect" />
          )}
        </div>

        {/* Question Content */}
        <div className="flex-1">
          <div className="mb-2 font-medium text-gray-900" data-testid="testid-question-prompt">
            {question.prompt}
          </div>

          <div className="space-y-1 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-600">Your answer:</span>
              <span
                className={`font-semibold ${question.is_correct ? 'text-green-700' : 'text-red-700'}`}
                data-testid="testid-question-user-answer"
              >
                {question.user_answer}
              </span>
            </div>

            {!question.is_correct && (
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-600">Correct answer:</span>
                <span className="font-semibold text-green-700" data-testid="testid-question-correct-answer">
                  {question.correct_answer}
                </span>
              </div>
            )}

            <div className="flex items-center gap-1 text-gray-500" data-testid="testid-question-time">
              <Clock className="h-3 w-3" />
              {formatTime(question.time_taken_ms)}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

