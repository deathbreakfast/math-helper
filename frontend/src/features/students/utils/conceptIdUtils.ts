/**
 * Concept ID utilities for parsing and converting between concept ID formats.
 * 
 * Supports both old format (c_level_1) and new format (c_concept_001, c_add_1s, etc.)
 * during the migration period.
 */

/**
 * Extract the legacy level number from a concept ID.
 * 
 * Supports:
 * - Old format: c_level_1 -> 1
 * - New format: c_concept_001 -> 1
 * - Descriptive format: c_add_1s -> null (no legacy level mapping)
 * 
 * @param conceptId The concept ID to parse
 * @returns The legacy level number if found, null otherwise
 */
export function legacyLevelFromConceptId(conceptId: string): number | null {
  if (!conceptId) return null

  // Old format: c_level_1, c_level_2, etc.
  const oldFormatMatch = conceptId.match(/^c_level_(\d+)$/)
  if (oldFormatMatch) {
    return parseInt(oldFormatMatch[1], 10)
  }

  // New format: c_concept_001, c_concept_002, etc.
  const newFormatMatch = conceptId.match(/^c_concept_(\d+)$/)
  if (newFormatMatch) {
    return parseInt(newFormatMatch[1], 10)
  }

  // Descriptive format (c_add_1s, c_sub_2s, etc.) - no legacy level mapping
  return null
}

/**
 * Parse a concept ID and extract useful information.
 * 
 * @param conceptId The concept ID to parse
 * @returns Parsed concept ID information
 */
export function parseConceptId(conceptId: string): {
  format: 'old' | 'new' | 'descriptive'
  legacyLevel: number | null
  raw: string
} {
  const legacyLevel = legacyLevelFromConceptId(conceptId)
  
  if (conceptId.startsWith('c_level_')) {
    return {
      format: 'old',
      legacyLevel,
      raw: conceptId,
    }
  }
  
  if (conceptId.startsWith('c_concept_')) {
    return {
      format: 'new',
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
