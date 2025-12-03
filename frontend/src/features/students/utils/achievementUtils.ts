// All tiers in order (new metal/prestige system)
const ALL_TIERS = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'grandmaster', 'legendary', 'mythic', 'divine', 'champion']

// Old tier system mapping
const OLD_TIER_MAP: Record<string, string> = {
  'b': 'Bronze',
  'a': 'Silver',
  's': 'Gold',
  'ss': 'Platinum',
  'sss': 'Diamond',
}

// Tier hierarchy for comparison
export const TIER_HIERARCHY: Record<string, number> = {
  'Bronze': 1,
  'Silver': 2,
  'Gold': 3,
  'Platinum': 4,
  'Diamond': 5,
  'Master': 6,
  'Grandmaster': 7,
  'Legendary': 8,
  'Mythic': 9,
  'Divine': 10,
  'Champion': 11,
}

export const TIER_ORDER = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster', 'Legendary', 'Mythic', 'Divine', 'Champion']

/**
 * Extract tier from achievement code
 * Handles both old format (b/a/s/ss/sss) and new format (bronze/silver/etc.)
 */
export function extractTierFromCode(code: string): { baseCode: string; tier: string | null } {
  // Check for old tier suffixes first (longest first to avoid partial matches)
  const oldTierSuffixes = ['sss', 'ss', 's', 'a', 'b']
  for (const suffix of oldTierSuffixes) {
    if (code.endsWith(`-${suffix}`)) {
      const baseCode = code.slice(0, -(suffix.length + 1))
      const tier = OLD_TIER_MAP[suffix] || null
      return { baseCode, tier }
    }
  }
  
  // Check for new tier suffixes (longest first to avoid partial matches)
  const sortedTiers = [...ALL_TIERS].sort((a, b) => b.length - a.length)
  for (const tier of sortedTiers) {
    if (code.endsWith(`-${tier}`)) {
      const baseCode = code.slice(0, -(tier.length + 1))
      const capitalizedTier = tier.charAt(0).toUpperCase() + tier.slice(1)
      return { baseCode, tier: capitalizedTier }
    }
  }
  
  return { baseCode: code, tier: null }
}

/**
 * Clean title to remove tier suffix if present
 */
export function cleanTitle(title: string, tier: string | null): string {
  if (!tier) return title
  
  // Remove " (TierName)" pattern from end (case insensitive)
  const tierPattern = new RegExp(`\\s*\\(${tier}\\)$`, 'i')
  return title.replace(tierPattern, '').trim()
}

/**
 * Get next tier in hierarchy
 */
export function getNextTier(tier: string): string | null {
  const index = TIER_ORDER.indexOf(tier)
  return index >= 0 && index < TIER_ORDER.length - 1 ? TIER_ORDER[index + 1] : null
}

/**
 * Determine if an achievement should be shown based on tier visibility rules
 * Shows: unlocked achievements + next tier (n+1) if previous tier is unlocked
 * In dev mode: shows all achievements
 */
export function shouldShowAchievement(
  achievement: { id: string; status: string; tier: string },
  allAchievements: Array<{ id: string; status: string; tier: string }>,
  devMode: boolean
): boolean {
  if (devMode) return true
  
  // If unlocked, always show
  if (achievement.status === 'unlocked') return true
  
  // Extract base code and tier
  const { baseCode, tier } = extractTierFromCode(achievement.id)
  if (!tier) return true // Non-tiered achievements always show
  
  // Find all achievements with same base code
  const baseAchievements = allAchievements.filter(a => {
    const { baseCode: aBase } = extractTierFromCode(a.id)
    return aBase === baseCode
  })
  
  // Find all unlocked tiers for this base
  const unlockedTiers = baseAchievements
    .filter(a => a.status === 'unlocked')
    .map(a => {
      const { tier: aTier } = extractTierFromCode(a.id)
      return aTier
    })
    .filter((t): t is string => t !== null)
  
  if (unlockedTiers.length === 0) {
    // No unlocked tiers - only show Bronze (first tier)
    return tier === 'Bronze'
  }
  
  // Check if this tier is unlocked (show all unlocked tiers)
  if (unlockedTiers.includes(tier)) {
    return true
  }
  
  // Find highest unlocked tier to determine next tier to show
  const highestUnlocked = unlockedTiers.reduce((highest, current) => {
    const highestValue = TIER_HIERARCHY[highest] || 0
    const currentValue = TIER_HIERARCHY[current] || 0
    return currentValue > highestValue ? current : highest
  })
  
  // Show next tier (n+1) after highest unlocked
  const nextTier = getNextTier(highestUnlocked)
  return tier === nextTier
}

export const getTierColor = (tier: string): string => {
  const colors: Record<string, string> = {
    B: 'from-blue-400 to-blue-500',
    A: 'from-green-400 to-green-600',
    S: 'from-yellow-400 to-yellow-600',
    SS: 'from-orange-400 to-orange-600',
    SSS: 'from-purple-500 to-pink-600',
    Starter: 'from-gray-400 to-gray-500',
    Bronze: 'from-amber-600 to-amber-700',
    Silver: 'from-gray-400 to-gray-500',
    Gold: 'from-yellow-400 to-yellow-600',
    Platinum: 'from-cyan-400 to-blue-500',
    Diamond: 'from-blue-500 to-purple-600',
    Master: 'from-purple-500 to-indigo-600',
    Grandmaster: 'from-indigo-500 to-purple-600',
    Legendary: 'from-pink-500 to-rose-600',
    Mythic: 'from-rose-500 to-red-600',
    Divine: 'from-yellow-300 to-amber-400',
    Champion: 'from-yellow-200 to-yellow-400',
  }
  return colors[tier] || 'from-gray-400 to-gray-500'
}

