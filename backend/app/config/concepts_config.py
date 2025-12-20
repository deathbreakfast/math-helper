"""Concept configuration keyed by concept_id.

This is the backend source of truth for question generation per concept.

For now, legacy concepts `c_concept_###` map 1:1 to the existing `LEVELS_CONFIG`
entries (levels 1-45). This keeps behavior stable while enabling the system to
support descriptive concept IDs (e.g. `c_add_1s`) without depending on levels.
"""

from __future__ import annotations

from typing import Any

from .levels_config import LEVELS_CONFIG


CONCEPTS_CONFIG: dict[str, dict[str, Any]] = {
    f"c_concept_{level:03d}": {**config, "legacy_level": level}
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
        "c_add_1s": {**_addition_fixed_addend(1, 2)},
        "c_add_2s": {**_addition_fixed_addend(2, 3)},
        "c_add_3s": {**_addition_fixed_addend(3, 4)},
        "c_add_4s": {**_addition_fixed_addend(4, 5)},
        "c_add_5s": {**_addition_fixed_addend(5, 6)},
        "c_add_6s": {**_addition_fixed_addend(6, 7)},
        "c_add_7s": {**_addition_fixed_addend(7, 8)},
        "c_add_8s": {**_addition_fixed_addend(8, 9)},
        "c_add_9s": {**_addition_fixed_addend(9, 10)},
        "c_add_10s": {**_addition_fixed_addend(10, 11)},
        # Single Digit Addition (0s): operand2 fixed 0, operand1 1-9
        "c_add_0s": {
            "operation": "addition",
            "operand1_range": {"min": 1, "max": 9},
            "operand2_range": {"min": 0, "max": 0},
            "constraints": {"fixed_operand2": 0, "answer_min": 1},
            "layout_type": "vertical",
            "answer_format": "integer",
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
        "c_mul_2s": {**_multiplication_table(2)},
        "c_mul_3s": {**_multiplication_table(3)},
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
        },
        "c_sub_1s": {**_subtraction_fixed_subtrahend(1, 2, 11)},
        "c_sub_2s": {**_subtraction_fixed_subtrahend(2, 3, 12)},
        "c_sub_3s": {**_subtraction_fixed_subtrahend(3, 4, 13)},
        "c_sub_4s": {**_subtraction_fixed_subtrahend(4, 5, 14)},
        "c_sub_5s": {**_subtraction_fixed_subtrahend(5, 6, 15)},
        "c_sub_6s": {**_subtraction_fixed_subtrahend(6, 7, 16)},
        "c_sub_7s": {**_subtraction_fixed_subtrahend(7, 8, 17)},
        "c_sub_8s": {**_subtraction_fixed_subtrahend(8, 9, 18)},
        "c_sub_9s": {**_subtraction_fixed_subtrahend(9, 10, 19)},
        "c_sub_10s": {**_subtraction_fixed_subtrahend(10, 11, 20)},
    }
)

