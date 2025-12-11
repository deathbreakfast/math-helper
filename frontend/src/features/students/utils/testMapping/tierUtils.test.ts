import { describe, it, expect } from 'vitest'
import { mapOldTierToNew, getTierHierarchy, compareTiers } from './tierUtils'

describe('tierUtils', () => {
  describe('mapOldTierToNew', () => {
    it('should map old tier B to Bronze', () => {
      expect(mapOldTierToNew('B')).toBe('Bronze')
    })

    it('should map old tier A to Silver', () => {
      expect(mapOldTierToNew('A')).toBe('Silver')
    })

    it('should map old tier S to Gold', () => {
      expect(mapOldTierToNew('S')).toBe('Gold')
    })

    it('should map old tier SS to Platinum', () => {
      expect(mapOldTierToNew('SS')).toBe('Platinum')
    })

    it('should map old tier SSS to Diamond', () => {
      expect(mapOldTierToNew('SSS')).toBe('Diamond')
    })

    it('should return new tier as-is if already a new tier', () => {
      expect(mapOldTierToNew('Gold')).toBe('Gold')
      expect(mapOldTierToNew('Champion')).toBe('Champion')
      expect(mapOldTierToNew('Master')).toBe('Master')
    })

    it('should handle case-insensitive new tiers', () => {
      expect(mapOldTierToNew('gold')).toBe('Gold')
      expect(mapOldTierToNew('GOLD')).toBe('Gold')
      expect(mapOldTierToNew('ChAmPiOn')).toBe('Champion')
    })

    it('should default to Bronze for unknown tiers', () => {
      expect(mapOldTierToNew('Unknown')).toBe('Bronze')
      expect(mapOldTierToNew('XYZ')).toBe('Bronze')
      expect(mapOldTierToNew('')).toBe('Bronze')
    })

    it('should handle all new tier values', () => {
      const newTiers = [
        'Bronze',
        'Silver',
        'Gold',
        'Platinum',
        'Diamond',
        'Master',
        'Grandmaster',
        'Legendary',
        'Mythic',
        'Divine',
        'Champion',
      ]

      newTiers.forEach((tier) => {
        expect(mapOldTierToNew(tier)).toBe(tier)
      })
    })
  })

  describe('getTierHierarchy', () => {
    it('should return correct hierarchy values for old tiers', () => {
      expect(getTierHierarchy('B')).toBe(1) // Bronze
      expect(getTierHierarchy('A')).toBe(2) // Silver
      expect(getTierHierarchy('S')).toBe(3) // Gold
      expect(getTierHierarchy('SS')).toBe(4) // Platinum
      expect(getTierHierarchy('SSS')).toBe(5) // Diamond
    })

    it('should return correct hierarchy values for new tiers', () => {
      expect(getTierHierarchy('Bronze')).toBe(1)
      expect(getTierHierarchy('Silver')).toBe(2)
      expect(getTierHierarchy('Gold')).toBe(3)
      expect(getTierHierarchy('Platinum')).toBe(4)
      expect(getTierHierarchy('Diamond')).toBe(5)
      expect(getTierHierarchy('Master')).toBe(6)
      expect(getTierHierarchy('Grandmaster')).toBe(7)
      expect(getTierHierarchy('Legendary')).toBe(8)
      expect(getTierHierarchy('Mythic')).toBe(9)
      expect(getTierHierarchy('Divine')).toBe(10)
      expect(getTierHierarchy('Champion')).toBe(11)
    })

    it('should return hierarchy for unknown tiers (defaults to Bronze)', () => {
      // Unknown tiers default to Bronze, which has hierarchy 1
      expect(getTierHierarchy('Unknown')).toBe(1)
      expect(getTierHierarchy('XYZ')).toBe(1)
    })

    it('should handle case-insensitive tiers', () => {
      expect(getTierHierarchy('gold')).toBe(3)
      expect(getTierHierarchy('CHAMPION')).toBe(11)
    })
  })

  describe('compareTiers', () => {
    it('should return negative when tier1 > tier2 (sorts descending)', () => {
      // compareTiers returns tier2 - tier1 (for descending sort)
      expect(compareTiers('Gold', 'Bronze')).toBeLessThan(0)
      expect(compareTiers('Champion', 'Silver')).toBeLessThan(0)
      expect(compareTiers('Diamond', 'Platinum')).toBeLessThan(0)
    })

    it('should return positive when tier1 < tier2 (sorts descending)', () => {
      // compareTiers returns tier2 - tier1 (for descending sort)
      expect(compareTiers('Bronze', 'Gold')).toBeGreaterThan(0)
      expect(compareTiers('Silver', 'Champion')).toBeGreaterThan(0)
      expect(compareTiers('Platinum', 'Diamond')).toBeGreaterThan(0)
    })

    it('should return 0 when tiers are equal', () => {
      expect(compareTiers('Gold', 'Gold')).toBe(0)
      expect(compareTiers('Bronze', 'Bronze')).toBe(0)
      expect(compareTiers('Champion', 'Champion')).toBe(0)
    })

    it('should compare old and new tier formats', () => {
      expect(compareTiers('B', 'Bronze')).toBe(0)
      expect(compareTiers('A', 'Silver')).toBe(0)
      expect(compareTiers('S', 'Gold')).toBe(0)
      expect(compareTiers('SS', 'Platinum')).toBe(0)
      expect(compareTiers('SSS', 'Diamond')).toBe(0)
    })

    it('should handle case-insensitive comparison', () => {
      expect(compareTiers('gold', 'Gold')).toBe(0)
      expect(compareTiers('CHAMPION', 'champion')).toBe(0)
    })

    it('should correctly sort tiers in descending order', () => {
      const tiers = ['Bronze', 'Gold', 'Champion', 'Silver']
      // compareTiers already sorts descending (tier2 - tier1)
      const sorted = [...tiers].sort((a, b) => compareTiers(a, b))
      expect(sorted).toEqual(['Champion', 'Gold', 'Silver', 'Bronze'])
    })

    it('should correctly sort tiers in ascending order', () => {
      const tiers = ['Champion', 'Bronze', 'Gold', 'Silver', 'Platinum']
      // Negate to get ascending order
      const sorted = [...tiers].sort((a, b) => -compareTiers(a, b))
      expect(sorted).toEqual(['Bronze', 'Silver', 'Gold', 'Platinum', 'Champion'])
    })
  })
})


