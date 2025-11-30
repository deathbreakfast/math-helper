import { Page } from '@playwright/test'

export type TestUser = {
  id: number
  name: string
  avatar: string
  pin: string
  level: number
}

export type PracticeElements = {
  answerInput: ReturnType<Page['getByTestId']>
  checkButton: ReturnType<Page['getByTestId']>
  nextButton: ReturnType<Page['getByTestId']>
  submitButton: ReturnType<Page['getByTestId']>
  questionDisplay: ReturnType<Page['getByTestId']>
  progressBar: ReturnType<Page['getByTestId']>
  flagButton: ReturnType<Page['getByTestId']>
  previousButton: ReturnType<Page['getByTestId']>
}

