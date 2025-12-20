/**
 * Practice Start Strategies
 * 
 * Factory pattern for selecting how to start a practice session.
 * Allows for different selection methods (random, adaptive, etc.)
 */

import type { MathConcept } from '../../students/data/mathConcepts'
import type { UserProgressData } from '../../students/utils/progressMapping'
import { getUnlockedConcepts } from '../../students/utils/conceptUnlock'
import { getAllMathConcepts } from '../../students/data/mathConcepts'

/**
 * Strategy interface for selecting a practice concept
 */
export interface PracticeStartStrategy {
  selectConcept(userData: UserProgressData, devMode?: boolean): MathConcept | null
  getName(): string
}

/**
 * Random unlocked concept strategy
 * Selects a random concept from all unlocked concepts
 */
export class RandomUnlockedConceptStrategy implements PracticeStartStrategy {
  getName(): string {
    return 'random-unlocked'
  }

  selectConcept(userData: UserProgressData, devMode: boolean = false): MathConcept | null {
    const allConcepts = getAllMathConcepts()
    
    // Get unlocked concepts
    const unlockedConcepts = getUnlockedConcepts(
      allConcepts,
      userData.achievements || [],
      devMode
    )

    if (unlockedConcepts.length === 0) {
      return null
    }

    // Select random concept
    const randomIndex = Math.floor(Math.random() * unlockedConcepts.length)
    return unlockedConcepts[randomIndex]
  }
}

/**
 * Factory for creating practice start strategies
 */
export class PracticeStartStrategyFactory {
  private static strategies: Map<string, () => PracticeStartStrategy> = new Map([
    ['random-unlocked', () => new RandomUnlockedConceptStrategy()],
    // Future strategies can be added here:
    // ['adaptive', () => new AdaptiveConceptStrategy()],
    // ['weakest-area', () => new WeakestAreaStrategy()],
  ])

  /**
   * Get a strategy by name
   */
  static getStrategy(name: string = 'random-unlocked'): PracticeStartStrategy {
    const strategyFactory = this.strategies.get(name)
    if (!strategyFactory) {
      // Fallback to default strategy
      return new RandomUnlockedConceptStrategy()
    }
    return strategyFactory()
  }

  /**
   * Get the default strategy
   */
  static getDefaultStrategy(): PracticeStartStrategy {
    return this.getStrategy('random-unlocked')
  }

  /**
   * Register a new strategy
   */
  static registerStrategy(name: string, factory: () => PracticeStartStrategy): void {
    this.strategies.set(name, factory)
  }
}

/**
 * Hook-friendly wrapper for strategy selection
 * This allows strategies to be used in React components
 */
export function usePracticeStartStrategy(
  strategyName: string = 'random-unlocked'
): (userData: UserProgressData) => MathConcept | null {
  return (userData: UserProgressData) => {
    const strategy = PracticeStartStrategyFactory.getStrategy(strategyName)
    return strategy.selectConcept(userData)
  }
}
