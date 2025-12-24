"""Legacy mapping from old test_type identifiers to a practice level.

The app no longer exposes a Tests feature, but some legacy level progression
requirements still reference `metadata_filter.test_type`.

Until those requirements are migrated to concept_id metadata, we translate
`test_type` filters into an equivalent `concept_id` filter (c_concept_XXX format).
This mapping is used by translation layers in user_service.py and routes/levels.py.
"""

from __future__ import annotations

LEGACY_TEST_TYPE_TO_LEVEL: dict[str, int] = {
    # Addition
    "addition-1digit": 1,
    "addition-1digit-zeros": 1,
    "addition-1digit-negative": 1,
    "addition-2digit": 2,
    "addition-3digit": 8,
    # Subtraction
    "subtraction-1digit": 3,
    "subtraction-1digit-zeros": 3,
    "subtraction-1digit-negative": 3,
    "subtraction-2digit": 4,
    "subtraction-3digit": 23,
    # Mixed
    "basic-math-mixed": 5,
    # Multiplication tables
    "multiplication-by-0": 18,
    "multiplication-by-1": 7,
    "multiplication-by-2": 9,
    "multiplication-by-3": 10,
    "multiplication-by-4": 11,
    "multiplication-by-5": 12,
    "multiplication-by-6": 13,
    "multiplication-by-7": 14,
    "multiplication-by-8": 15,
    "multiplication-by-9": 16,
    "multiplication-by-10": 19,
    "multiplication-by-11": 20,
    "multiplication-by-12": 21,
    # Multiplication (multi-digit)
    "multiplication-2digit": 24,
    "multiplication-3digit": 25,
    # Division tables
    "division-by-0": 34,
    "division-by-1": 25,
    "division-by-2": 26,
    "division-by-3": 27,
    "division-by-4": 28,
    "division-by-5": 29,
    "division-by-6": 30,
    "division-by-7": 31,
    "division-by-8": 32,
    "division-by-9": 33,
    "division-by-10": 35,
    "division-by-11": 36,
    "division-by-12": 37,
    # Division formats
    "division-no-remainder-single": 38,
    "division-remainder": 39,
    "division-fraction": 40,
    "division-decimal": 44,
    "division-long": 45,
}

