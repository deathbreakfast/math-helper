/**
 * Concept ID utilities for parsing concept ID formats.
 * 
 * Note: Legacy level system has been removed. These utilities are kept for
 * minimal backward compatibility with c_concept_### format.
 */

/**
 * Extract level number from c_concept_### format concept ID.
 * 
 * Supports:
 * - Format: c_concept_001 -> 1
 * - Descriptive format: c_add_1s -> null (no level mapping)
 * 
 * @param conceptId The concept ID to parse
 * @returns The level number if found, null otherwise
 */
export function legacyLevelFromConceptId(conceptId: string): number | null {
  if (!conceptId) return null

  // Format: c_concept_001, c_concept_002, etc.
  const match = conceptId.match(/^c_concept_(\d+)$/)
  if (match) {
    return parseInt(match[1], 10)
  }

  // Descriptive format (c_add_1s, c_sub_2s, etc.) - no level mapping
  return null
}

/**
 * Parse a concept ID and extract useful information.
 * 
 * @param conceptId The concept ID to parse
 * @returns Parsed concept ID information
 */
export function parseConceptId(conceptId: string): {
  format: 'legacy' | 'descriptive'
  legacyLevel: number | null
  raw: string
} {
  const legacyLevel = legacyLevelFromConceptId(conceptId)
  
  if (conceptId.startsWith('c_concept_')) {
    return {
      format: 'legacy',
      legacyLevel,
      raw: conceptId,
    }
  }
  
  // Descriptive format (c_add_1s, c_sub_2s, etc.)
  return {
    format: 'descriptive',
    legacyLevel: null,
    raw: conceptId,
  }
}

/**
 * Get the concept number from a concept ID (for c_concept_XXX format).
 * 
 * @param conceptId The concept ID (e.g., "c_concept_001")
 * @returns The concept number (e.g., 1) or null if not applicable
 */
export function conceptNumberFromId(conceptId: string): number | null {
  const match = conceptId.match(/^c_concept_(\d+)$/)
  if (match) {
    return parseInt(match[1], 10)
  }
  return legacyLevelFromConceptId(conceptId)
}

/**
 * Generate a new-format concept ID from a legacy level number.
 * 
 * @param level The legacy level number (1-45)
 * @returns The new-format concept ID (e.g., "c_concept_001")
 */
export function conceptIdFromLegacyLevel(level: number): string {
  return `c_concept_${String(level).padStart(3, '0')}`
}
