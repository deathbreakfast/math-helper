"""Concept configuration keyed by concept_id.

This is the backend source of truth for question generation per concept.

For now, legacy concepts `c_concept_###` map 1:1 to the existing `LEVELS_CONFIG`
entries (levels 1-45). This keeps behavior stable while enabling the system to
support descriptive concept IDs (e.g. `c_add_1s`) without depending on levels.
"""

from __future__ import annotations

from typing import Any

from .levels_config import LEVELS_CONFIG


# Speed multipliers mapped by level
SPEED_MULTIPLIERS_BY_LEVEL: dict[int, float] = {
    1: 1.1,   # Basic Single Digit Addition
    2: 1.1,   # Addition with Zero (Adding 0)
    3: 1.2,   # Basic Single Digit Subtraction
    4: 1.2,   # Subtraction with Zero (Subtracting 0)
    5: 1.0,   # Single and Two Digit Addition
    6: 1.2,   # Single and Two Digit Subtraction
    7: 3.0,   # Two Digit Addition
    8: 4.0,   # Two Digit Subtraction
    9: 1.2,   # Subtraction with Borrowing (Small Numbers)
    10: 1.0,  # Negative Number Subtraction
    11: 1.0,  # Multiplication by 1
    12: 1.2,  # Multiplication by 4
    13: 1.1,  # Multiplication by 5
    14: 1.4,  # Multiplication by 6
    15: 1.4,  # Multiplication by 7
    16: 1.4,  # Multiplication by 8
    17: 1.3,  # Multiplication by 9
    18: 1.0,  # Multiplication by 0
    19: 1.1,  # Multiplication by 10
    20: 1.4,  # Multiplication by 11
    21: 1.4,  # Multiplication by 12
    22: 6.0,  # Three Digit Addition
    23: 6.5,  # Three Digit Subtraction
    24: 6.0,  # Two Digit by Single Digit Multiplication (Partial Products)
    25: 10.0, # Two Digit by Two Digit Multiplication (Partial Products)
    26: 1.0,  # Division by 1
    27: 1.2,  # Division by 2
    28: 1.3,  # Division by 3
    29: 1.3,  # Division by 4
    30: 1.2,  # Division by 5
    31: 1.4,  # Division by 6
    32: 1.4,  # Division by 7
    33: 1.4,  # Division by 8
    34: 1.3,  # Division by 9
    35: 1.1,  # Division by 10
    36: 1.5,  # Division by 11
    37: 1.5,  # Division by 0 (Special Case)
    38: 1.1,  # Division by 10 (Repeated)
    39: 3.0,  # Division with Remainders (Single Digit Divisors)
    40: 6.0,  # Division with Remainders (Two Digit Dividends)
    41: 3.5,  # Division with Fractional Answers (Single Digit Divisors)
    42: 7.0,  # Division with Fractional Answers (Two Digit Dividends)
    43: 7.0,  # Three Digit by Two Digit Multiplication (Partial Products)
    44: 12.0, # Division with Fractional Answers (Three Digit Dividends)
    45: 11.0, # Division with Decimal Answers (Single Digit Divisors)
}

CONCEPTS_CONFIG: dict[str, dict[str, Any]] = {
    f"c_concept_{level:03d}": {
        **config,
        "legacy_level": level,
        "speed_multiplier": SPEED_MULTIPLIERS_BY_LEVEL.get(level, 1.0)
    }
    for level, config in LEVELS_CONFIG.items()
}

# Special cases / overrides not representable with the legacy level system.
# Division by 0 (Special Case): allow generating 0 ÷ 0 with answer "undefined".
CONCEPTS_CONFIG["c_concept_037"] = {
    "operation": "division",
    "operand1_range": {"min": 0, "max": 0},
    "operand2_range": {"min": 0, "max": 0},
    "constraints": {"fixed_operand2": 0, "no_remainder": True, "allow_division_by_zero": True},
    "layout_type": "longDivision",
    "answer_format": "integer",
    "legacy_level": 37,
    "speed_multiplier": 1.5,  # Division by 0 (Special Case)
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

