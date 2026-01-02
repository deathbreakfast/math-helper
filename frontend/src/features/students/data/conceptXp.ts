/**
 * Concept XP values (XP per correct answer).
 *
 * For now this supports legacy `c_concept_###` IDs (1-45), sourced from `MATH_CONCEPTS.md`.
 * Descriptive concept IDs (e.g. `c_add_1s`) will be supported once the frontend concept
 * catalog is driven from the doc/config instead of placeholder level mapping.
 */

export const CONCEPT_XP_PER_CORRECT: Record<string, number> = {
  c_concept_001: 97,
  // c_concept_002 removed (merged into c_concept_001)
  c_concept_003: 177,
  // c_concept_004 removed (covered by c_sub_0s)
  c_concept_005: 102,
  c_concept_006: 182,
  c_concept_007: 107,
  c_concept_008: 187,
  // c_concept_009 removed
  c_concept_010: 202,
  c_concept_011: 212,
  c_concept_012: 227,
  c_concept_013: 222,
  c_concept_014: 242,
  c_concept_015: 247,
  c_concept_016: 252,
  c_concept_017: 257,
  c_concept_018: 207,
  c_concept_019: 217,
  c_concept_020: 232,
  c_concept_021: 237,
  c_concept_022: 112,
  c_concept_023: 192,
  c_concept_024: 262,
  c_concept_025: 267,
  c_concept_026: 277,
  c_concept_027: 282,
  c_concept_028: 297,
  c_concept_029: 302,
  c_concept_030: 307,
  c_concept_031: 312,
  c_concept_032: 317,
  c_concept_033: 322,
  c_concept_034: 327,
  c_concept_035: 287,
  c_concept_036: 332,
  c_concept_037: 337,
  c_concept_038: 292,
  c_concept_039: 342,
  c_concept_040: 347,
  c_concept_041: 352,
  c_concept_042: 357,
  c_concept_043: 272,
  c_concept_044: 362,
  c_concept_045: 367,

  // Descriptive concept IDs (starting set)
  c_add_0s: 47,
  c_add_1s: 37,
  c_add_2s: 57,
  c_add_3s: 62,
  c_add_4s: 67,
  c_add_5s: 72,
  c_add_6s: 77,
  c_add_7s: 82,
  c_add_8s: 87,
  c_add_9s: 92,
  c_add_10s: 52,

  c_sub_0s: 122,
  c_sub_1s: 127,
  c_sub_2s: 132,
  c_sub_3s: 137,
  c_sub_4s: 142,
  c_sub_5s: 147,
  c_sub_6s: 152,
  c_sub_7s: 157,
  c_sub_8s: 162,
  c_sub_9s: 167,
  c_sub_10s: 172,

  c_mul_2s: 215,
  c_mul_3s: 220,
}

export function getConceptXpPerCorrect(conceptId: string | undefined | null): number | null {
  if (!conceptId) return null
  return CONCEPT_XP_PER_CORRECT[conceptId] ?? null
}

