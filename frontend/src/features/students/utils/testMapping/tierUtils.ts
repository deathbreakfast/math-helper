// New metal/prestige tier system
export type NewTier = 'Bronze' | 'Silver' | 'Gold' | 'Platinum' | 'Diamond' | 'Master' | 'Grandmaster' | 'Legendary' | 'Mythic' | 'Divine' | 'Champion'
export type OldTier = 'B' | 'A' | 'S' | 'SS' | 'SSS'
export type Tier = NewTier | OldTier

// Old to New tier mapping
const OLD_TO_NEW_TIER: Record<OldTier, NewTier> = {
  'B': 'Bronze',
  'A': 'Silver',
  'S': 'Gold',
  'SS': 'Platinum',
  'SSS': 'Diamond',
}

// New tier hierarchy (for comparison/sorting)
const TIER_HIERARCHY: Record<NewTier, number> = {
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

/**
 * Map old tier (B/A/S/SS/SSS) to new tier system (Bronze/Silver/Gold/Platinum/Diamond/...)
 */
export function mapOldTierToNew(oldTier: OldTier | string): NewTier {
  if (oldTier in OLD_TO_NEW_TIER) {
    return OLD_TO_NEW_TIER[oldTier as OldTier]
  }
  // If already a new tier, return as-is (case-insensitive)
  const normalized = oldTier.charAt(0).toUpperCase() + oldTier.slice(1).toLowerCase()
  if (normalized in TIER_HIERARCHY) {
    return normalized as NewTier
  }
  // Default to Bronze if unknown
  return 'Bronze'
}

/**
 * Get tier hierarchy value for comparison
 */
export function getTierHierarchy(tier: Tier | string): number {
  const newTier = mapOldTierToNew(tier)
  return TIER_HIERARCHY[newTier] || 0
}

/**
 * Compare two tiers - returns positive if tier1 > tier2, negative if tier1 < tier2, 0 if equal
 */
export function compareTiers(tier1: Tier | string, tier2: Tier | string): number {
  return getTierHierarchy(tier2) - getTierHierarchy(tier1)
}



