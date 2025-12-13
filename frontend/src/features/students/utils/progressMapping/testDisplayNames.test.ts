import { describe, it, expect } from 'vitest'
import { getTestDisplayName } from './testDisplayNames'

describe('testDisplayNames', () => {
  describe('getTestDisplayName', () => {
    it('should return mapped display names for known test types', () => {
      expect(getTestDisplayName('addition-1digit')).toBe('1 Digit Addition')
      expect(getTestDisplayName('addition-2digit')).toBe('2 Digit Addition')
      expect(getTestDisplayName('subtraction-1digit')).toBe('1 Digit Subtraction')
      expect(getTestDisplayName('multiplication-by-5')).toBe('Multiplication by 5')
      expect(getTestDisplayName('division-by-10')).toBe('Division by 10')
    })

    it('should handle test types with special formatting', () => {
      expect(getTestDisplayName('addition-1digit-zeros')).toBe('1 Digit Addition w/ Zeros')
      expect(getTestDisplayName('subtraction-1digit-zeros')).toBe('1 Digit Subtraction w/ Zeros')
    })

    it('should handle all multiplication test types', () => {
      for (let i = 1; i <= 12; i++) {
        expect(getTestDisplayName(`multiplication-by-${i}`)).toBe(`Multiplication by ${i}`)
      }
    })

    it('should handle all division test types', () => {
      for (let i = 1; i <= 12; i++) {
        expect(getTestDisplayName(`division-by-${i}`)).toBe(`Division by ${i}`)
      }
    })

    it('should convert unknown test types by replacing dashes with spaces', () => {
      expect(getTestDisplayName('unknown-test-type')).toBe('unknown test type')
      expect(getTestDisplayName('my-custom-test')).toBe('my custom test')
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



