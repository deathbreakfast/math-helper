"""Concept configuration keyed by concept_id.

This is the backend source of truth for question generation per concept.
"""

from __future__ import annotations

from typing import Any


# Concept definitions (c_concept_001 through c_concept_045)
CONCEPTS_CONFIG: dict[str, dict[str, Any]] = {
    "c_concept_001": {
        "operation": "addition",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 0, "max": 9},
        "constraints": {"answer_min": 0},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.1,
    },
    "c_concept_003": {
        "operation": "subtraction",
        "operand1_range": {"min": 1, "max": 10},
        "operand2_range": {"min": 1, "max": 10},
        "constraints": {"exclude_zeros": True, "answer_min": 1},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.2,
    },
    "c_concept_005": {
        "operation": "addition",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.0,
    },
    "c_concept_006": {
        "operation": "subtraction",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {"answer_min": 0},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.2,
    },
    "c_concept_007": {
        "operation": "addition",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 3.0,
    },
    "c_concept_008": {
        "operation": "subtraction",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {"answer_min": 0},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 4.0,
    },
    "c_concept_010": {
        "operation": "subtraction",
        "operand1_range": {"min": -99, "max": 0},
        "operand2_range": {"min": 0, "max": 99},
        "constraints": {"answer_min": -100},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.0,
    },
    "c_concept_011": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 1, "max": 1},
        "constraints": {"fixed_operand2": 1},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.0,
    },
    "c_concept_012": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 4, "max": 4},
        "constraints": {"fixed_operand2": 4},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.2,
    },
    "c_concept_013": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 5, "max": 5},
        "constraints": {"fixed_operand2": 5},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.1,
    },
    "c_concept_014": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 6, "max": 6},
        "constraints": {"fixed_operand2": 6},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_015": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 7, "max": 7},
        "constraints": {"fixed_operand2": 7},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_016": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 8, "max": 8},
        "constraints": {"fixed_operand2": 8},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_017": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 9, "max": 9},
        "constraints": {"fixed_operand2": 9},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.3,
    },
    "c_concept_018": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {"fixed_operand2": 0},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.0,
    },
    "c_concept_019": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {"fixed_operand2": 10},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.1,
    },
    "c_concept_020": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 11, "max": 11},
        "constraints": {"fixed_operand2": 11},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_021": {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 12, "max": 12},
        "constraints": {"fixed_operand2": 12},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_022": {
        "operation": "addition",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 6.0,
    },
    "c_concept_023": {
        "operation": "subtraction",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {"answer_min": 0},
        "layout_type": "vertical",
        "answer_format": "integer",
        "speed_multiplier": 6.5,
    },
    "c_concept_024": {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "easy",
        "answer_format": "integer",
        "speed_multiplier": 6.0,
    },
    "c_concept_025": {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "normal",
        "answer_format": "integer",
        "speed_multiplier": 10.0,
    },
    "c_concept_026": {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 1, "max": 1},
        "constraints": {"fixed_operand2": 1, "no_remainder": True},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.0,
    },
    "c_concept_027": {
        "operation": "division",
        "operand1_range": {"min": 2, "max": 24},
        "operand2_range": {"min": 2, "max": 2},
        "constraints": {"fixed_operand2": 2, "no_remainder": True, "multiple_of": 2},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.2,
    },
    "c_concept_028": {
        "operation": "division",
        "operand1_range": {"min": 3, "max": 36},
        "operand2_range": {"min": 3, "max": 3},
        "constraints": {"fixed_operand2": 3, "no_remainder": True, "multiple_of": 3},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.3,
    },
    "c_concept_029": {
        "operation": "division",
        "operand1_range": {"min": 4, "max": 48},
        "operand2_range": {"min": 4, "max": 4},
        "constraints": {"fixed_operand2": 4, "no_remainder": True, "multiple_of": 4},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.3,
    },
    "c_concept_030": {
        "operation": "division",
        "operand1_range": {"min": 5, "max": 60},
        "operand2_range": {"min": 5, "max": 5},
        "constraints": {"fixed_operand2": 5, "no_remainder": True, "multiple_of": 5},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.2,
    },
    "c_concept_031": {
        "operation": "division",
        "operand1_range": {"min": 6, "max": 72},
        "operand2_range": {"min": 6, "max": 6},
        "constraints": {"fixed_operand2": 6, "no_remainder": True, "multiple_of": 6},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_032": {
        "operation": "division",
        "operand1_range": {"min": 7, "max": 84},
        "operand2_range": {"min": 7, "max": 7},
        "constraints": {"fixed_operand2": 7, "no_remainder": True, "multiple_of": 7},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_033": {
        "operation": "division",
        "operand1_range": {"min": 8, "max": 96},
        "operand2_range": {"min": 8, "max": 8},
        "constraints": {"fixed_operand2": 8, "no_remainder": True, "multiple_of": 8},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.4,
    },
    "c_concept_034": {
        "operation": "division",
        "operand1_range": {"min": 9, "max": 108},
        "operand2_range": {"min": 9, "max": 9},
        "constraints": {"fixed_operand2": 9, "no_remainder": True, "multiple_of": 9},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.3,
    },
    "c_concept_035": {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 120},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {"fixed_operand2": 10, "no_remainder": True, "multiple_of": 10},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.1,
    },
    "c_concept_036": {
        "operation": "division",
        "operand1_range": {"min": 11, "max": 132},
        "operand2_range": {"min": 11, "max": 11},
        "constraints": {"fixed_operand2": 11, "no_remainder": True, "multiple_of": 11},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.5,
    },
    "c_concept_037": {
        "operation": "division",
        "operand1_range": {"min": 0, "max": 0},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {"fixed_operand2": 0, "no_remainder": True, "allow_division_by_zero": True},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.5,
    },
    "c_concept_038": {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 120},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {"fixed_operand2": 10, "no_remainder": True, "multiple_of": 10},
        "layout_type": "longDivision",
        "answer_format": "integer",
        "speed_multiplier": 1.1,
    },
    "c_concept_039": {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
        "speed_multiplier": 3.0,
    },
    "c_concept_040": {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
        "speed_multiplier": 6.0,
    },
    "c_concept_041": {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
        "speed_multiplier": 3.5,
    },
    "c_concept_042": {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
        "speed_multiplier": 7.0,
    },
    "c_concept_043": {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "normal",
        "answer_format": "integer",
        "speed_multiplier": 7.0,
    },
    "c_concept_044": {
        "operation": "division",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
        "speed_multiplier": 12.0,
    },
    "c_concept_045": {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "decimal",
        "speed_multiplier": 11.0,
    },
}

# Descriptive concept IDs (subset from MATH_CONCEPTS.md)
# Single Digit Addition (Ns): operand2 fixed to N, operand1 1-9
def _addition_fixed_addend(addend: int, answer_min: int) -> dict[str, Any]:
    return {
        "operation": "addition",
        "operand1_range": {"min": 1, "max": 9},
        "operand2_range": {"min": addend, "max": addend},
        "constraints": {"fixed_operand2": addend, "answer_min": answer_min},
        "layout_type": "vertical",
        "answer_format": "integer",
    }


CONCEPTS_CONFIG.update(
    {
        "c_add_1s": {**_addition_fixed_addend(1, 2), "speed_multiplier": 1.0},
        "c_add_2s": {**_addition_fixed_addend(2, 3), "speed_multiplier": 1.0},
        "c_add_3s": {**_addition_fixed_addend(3, 4), "speed_multiplier": 1.1},
        "c_add_4s": {**_addition_fixed_addend(4, 5), "speed_multiplier": 1.1},
        "c_add_5s": {**_addition_fixed_addend(5, 6), "speed_multiplier": 1.0},
        "c_add_6s": {**_addition_fixed_addend(6, 7), "speed_multiplier": 1.1},
        "c_add_7s": {**_addition_fixed_addend(7, 8), "speed_multiplier": 1.1},
        "c_add_8s": {**_addition_fixed_addend(8, 9), "speed_multiplier": 1.1},
        "c_add_9s": {**_addition_fixed_addend(9, 10), "speed_multiplier": 1.0},
        "c_add_10s": {**_addition_fixed_addend(10, 11), "speed_multiplier": 1.0},
        # Single Digit Addition (0s): operand2 fixed 0, operand1 1-9
        "c_add_0s": {
            "operation": "addition",
            "operand1_range": {"min": 1, "max": 9},
            "operand2_range": {"min": 0, "max": 0},
            "constraints": {"fixed_operand2": 0, "answer_min": 1},
            "layout_type": "vertical",
            "answer_format": "integer",
            "speed_multiplier": 1.0,
        },
    }
)

# Multiplication by N: operand2 fixed N, operand1 1-12
def _multiplication_table(multiplier: int) -> dict[str, Any]:
    return {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": multiplier, "max": multiplier},
        "constraints": {"fixed_operand2": multiplier},
        "layout_type": "vertical",
        "answer_format": "integer",
    }


CONCEPTS_CONFIG.update(
    {
        "c_mul_2s": {**_multiplication_table(2), "speed_multiplier": 1.1},
        "c_mul_3s": {**_multiplication_table(3), "speed_multiplier": 1.1},
    }
)

# Single Digit Subtraction (Ns): operand2 fixed to N, operand1 range ensures answer >= 1
def _subtraction_fixed_subtrahend(subtrahend: int, op1_min: int, op1_max: int) -> dict[str, Any]:
    return {
        "operation": "subtraction",
        "operand1_range": {"min": op1_min, "max": op1_max},
        "operand2_range": {"min": subtrahend, "max": subtrahend},
        "constraints": {"fixed_operand2": subtrahend, "answer_min": 1},
        "layout_type": "vertical",
        "answer_format": "integer",
    }


CONCEPTS_CONFIG.update(
    {
        "c_sub_0s": {
            "operation": "subtraction",
            "operand1_range": {"min": 1, "max": 10},
            "operand2_range": {"min": 0, "max": 0},
            "constraints": {"fixed_operand2": 0, "answer_min": 1},
            "layout_type": "vertical",
            "answer_format": "integer",
            "speed_multiplier": 1.0,
        },
        "c_sub_1s": {**_subtraction_fixed_subtrahend(1, 2, 11), "speed_multiplier": 1.0},
        "c_sub_2s": {**_subtraction_fixed_subtrahend(2, 3, 12), "speed_multiplier": 1.0},
        "c_sub_3s": {**_subtraction_fixed_subtrahend(3, 4, 13), "speed_multiplier": 1.1},
        "c_sub_4s": {**_subtraction_fixed_subtrahend(4, 5, 14), "speed_multiplier": 1.1},
        "c_sub_5s": {**_subtraction_fixed_subtrahend(5, 6, 15), "speed_multiplier": 1.0},
        "c_sub_6s": {**_subtraction_fixed_subtrahend(6, 7, 16), "speed_multiplier": 1.1},
        "c_sub_7s": {**_subtraction_fixed_subtrahend(7, 8, 17), "speed_multiplier": 1.1},
        "c_sub_8s": {**_subtraction_fixed_subtrahend(8, 9, 18), "speed_multiplier": 1.1},
        "c_sub_9s": {**_subtraction_fixed_subtrahend(9, 10, 19), "speed_multiplier": 1.0},
        "c_sub_10s": {**_subtraction_fixed_subtrahend(10, 11, 20), "speed_multiplier": 1.0},
    }
)


def get_concept_speed_multiplier(concept_id: str | None) -> float:
    """Get the speed multiplier for a concept.
    
    Speed multipliers adjust speed achievement thresholds based on concept difficulty.
    For example, long division might have a 2.5x multiplier, meaning the speed threshold
    is multiplied by 2.5 (making it easier to achieve for harder concepts).
    
    Args:
        concept_id: The concept ID (e.g., "c_concept_037", "c_add_1s")
        
    Returns:
        The speed multiplier for the concept, or 1.0 if concept_id is None or not found
    """
    if not concept_id:
        return 1.0
    
    concept_config = CONCEPTS_CONFIG.get(concept_id)
    if not concept_config:
        return 1.0
    
    return float(concept_config.get("speed_multiplier", 1.0))

