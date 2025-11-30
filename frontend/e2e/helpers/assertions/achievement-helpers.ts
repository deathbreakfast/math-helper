import { Page } from '@playwright/test'

/**
 * Filter achievements by category
 */
export async function filterAchievementsByCategory(page: Page, category: string): Promise<void> {
  const categoryFilter = page.getByTestId('testid-achievement-filter-category')
  await categoryFilter.selectOption(category)
  await page.waitForTimeout(300)
}

/**
 * Get achievement status (locked, unlocked, or in-progress)
 */
export async function getAchievementStatus(page: Page, achievementId: string): Promise<'locked' | 'unlocked' | 'in-progress'> {
  const achievementCard = page.getByTestId(`testid-achievement-card-${achievementId}`)
  const hasLockIcon = await achievementCard.locator('[data-testid="testid-achievement-lock-icon"]').isVisible()
  const hasUnlockIcon = await achievementCard.locator('[data-testid="testid-achievement-unlock-icon"]').isVisible()
  
  if (hasLockIcon) return 'locked'
  if (hasUnlockIcon) return 'unlocked'
  return 'in-progress'
}

/**
 * Get level requirement status from UI
 */
export async function getLevelRequirementStatus(page: Page, level: number): Promise<{
  isLocked: boolean
  completedCount: number
  totalCount: number
}> {
  const requirementCard = page.getByTestId(`testid-level-requirement-${level}`)
  const isLocked = await requirementCard.locator('[data-testid="testid-level-lock-icon"]').isVisible()
  const completedRequirements = await requirementCard.locator('[data-testid="testid-requirement-completed"]').count()
  const allRequirements = await requirementCard.locator('[data-testid^="testid-requirement-"]').count()
  
  return {
    isLocked,
    completedCount: completedRequirements,
    totalCount: allRequirements
  }
}

