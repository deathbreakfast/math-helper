import type { User } from '../hooks/useStudents'

const DATE_LABELS = ['Jan 1', 'Jan 8', 'Jan 15', 'Jan 22', 'Jan 29', 'Feb 5', 'Feb 12']

export type AccuracyHistoryPoint = {
  date: string
  addition: number
  subtraction: number
  multiplication: number
  division: number
}

export type SpeedHistoryPoint = AccuracyHistoryPoint

const clamp = (value: number, min: number, max: number) => Math.min(Math.max(value, min), max)

const hashSeed = (seed: string) => {
  let hash = 0
  for (let index = 0; index < seed.length; index += 1) {
    hash = (hash << 5) - hash + seed.charCodeAt(index)
    hash |= 0
  }
  return Math.abs(hash)
}

const getVariation = (seed: string, index: number) => {
  const hash = hashSeed(`${seed}-${index}`)
  return ((hash % 1000) / 1000) * 2 - 1
}

const createHistory = (user: User, buildValue: (operation: keyof AccuracyHistoryPoint, dateIndex: number) => number) =>
  DATE_LABELS.map((date, index) => ({
    date,
    addition: buildValue('addition', index),
    subtraction: buildValue('subtraction', index),
    multiplication: buildValue('multiplication', index),
    division: buildValue('division', index),
  }))

export const generateAccuracyHistory = (user: User): AccuracyHistoryPoint[] => {
  const { stats } = user

  const getBaseValue = (operation: keyof AccuracyHistoryPoint) => {
    switch (operation) {
      case 'addition':
        return stats.additionAccuracy
      case 'subtraction':
        return stats.subtractionAccuracy
      case 'multiplication':
        return stats.multiplicationAccuracy
      case 'division':
        return stats.divisionAccuracy
      default:
        return 0
    }
  }

  return createHistory(user, (operation, index) => {
    const base = getBaseValue(operation)
    const variation = getVariation(`${user.id}-${operation}`, index) * 6
    return clamp(Math.round(base + variation), 0, 100)
  })
}

export const generateSpeedHistory = (user: User): SpeedHistoryPoint[] => {
  const { stats } = user

  const getBaseValue = (operation: keyof SpeedHistoryPoint) => {
    switch (operation) {
      case 'addition':
        return stats.additionSpeed
      case 'subtraction':
        return stats.subtractionSpeed
      case 'multiplication':
        return stats.multiplicationSpeed
      case 'division':
        return stats.divisionSpeed
      default:
        return 0
    }
  }

  return createHistory(user, (operation, index) => {
    const base = getBaseValue(operation)
    const variation = getVariation(`${user.id}-${operation}`, index) * 0.8
    const value = Math.max(base + variation, 0)
    return Number(value.toFixed(1))
  })
}


