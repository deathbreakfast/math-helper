import { describe, it, expect } from 'vitest'
import { getTestDisplayName } from './testDisplayNames'

describe('testDisplayNames', () => {
  describe('getTestDisplayName', () => {
    it('should convert unknown test types by replacing dashes with spaces', () => {
      expect(getTestDisplayName('unknown-test-type')).toBe('unknown test type')
      expect(getTestDisplayName('my-custom-test')).toBe('my custom test')
    })

    it('should convert known legacy test types by replacing dashes with spaces', () => {
      expect(getTestDisplayName('addition-1digit')).toBe('addition 1digit')
      expect(getTestDisplayName('addition-1digit-zeros')).toBe('addition 1digit zeros')
      expect(getTestDisplayName('multiplication-by-5')).toBe('multiplication by 5')
      expect(getTestDisplayName('division-by-10')).toBe('division by 10')
    })

    it('should handle single-word test types', () => {
      expect(getTestDisplayName('addition')).toBe('addition')
      expect(getTestDisplayName('test')).toBe('test')
    })

    it('should handle empty string', () => {
      expect(getTestDisplayName('')).toBe('')
    })

    it('should handle test types with multiple dashes', () => {
      expect(getTestDisplayName('very-long-test-type-name')).toBe('very long test type name')
    })
  })
})




