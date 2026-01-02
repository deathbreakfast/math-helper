/**
 * Concept ID utilities for parsing concept ID formats.
 */

/**
 * Extract concept number from c_concept_### format concept ID.
 * 
 * @param conceptId The concept ID to parse
 * @returns The concept number if found, null otherwise
 */
export function numberFromConceptId(conceptId: string): number | null {
  if (!conceptId) return null

  const match = conceptId.match(/^c_concept_(\d+)$/)
  if (match) {
    return parseInt(match[1], 10)
  }
  return null
}

/**
 * Parse a concept ID and extract useful information.
 * 
 * @param conceptId The concept ID to parse
 * @returns Parsed concept ID information
 */
export function parseConceptId(conceptId: string): {
  format: 'numbered' | 'descriptive'
  number: number | null
  raw: string
} {
  const number = numberFromConceptId(conceptId)
  
  if (conceptId.startsWith('c_concept_')) {
    return {
      format: 'numbered',
      number,
      raw: conceptId,
    }
  }
  
  return {
    format: 'descriptive',
    number: null,
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
  return numberFromConceptId(conceptId)
}

/**
 * Generate a concept ID from a concept number.
 * 
 * @param number The concept number (1-45)
 * @returns The concept ID (e.g., "c_concept_001")
 */
export function conceptIdFromNumber(number: number): string {
  return `c_concept_${String(number).padStart(3, '0')}`
}
