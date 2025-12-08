"""Declarative configuration for all 45 math levels with problem generation rules."""

from typing import Any

# Level configurations: All 45 levels with problem generation rules
LEVELS_CONFIG: dict[int, dict[str, Any]] = {
    1: {
        "operation": "addition",
        "operand1_range": {"min": 1, "max": 9},
        "operand2_range": {"min": 1, "max": 9},
        "constraints": {
            "exclude_zeros": True,
            "answer_min": 2
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    2: {
        "operation": "addition",
        "operand1_range": {"min": 0, "max": 10},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {
            "exclude_zeros": True,
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    3: {
        "operation": "subtraction",
        "operand1_range": {"min": 1, "max": 10},
        "operand2_range": {"min": 1, "max": 10},
        "constraints": {
            "exclude_zeros": True,
            "answer_min": 1
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    4: {
        "operation": "subtraction",
        "operand1_range": {"min": 0, "max": 10},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {
            "exclude_zeros": False,
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    5: {
        "operation": "addition",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    6: {
        "operation": "subtraction",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    7: {
        "operation": "addition",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    8: {
        "operation": "subtraction",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    9: {
        "operation": "subtraction",
        "operand1_range": {"min": 0, "max": 1},
        "operand2_range": {"min": 1, "max": 10},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    10: {
        "operation": "subtraction",
        "operand1_range": {"min": -99, "max": 0},
        "operand2_range": {"min": 0, "max": 99},
        "constraints": {
            "answer_min": -100
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    11: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 1, "max": 1},
        "constraints": {
            "fixed_operand2": 1
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    12: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 4, "max": 4},
        "constraints": {
            "fixed_operand2": 4
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    13: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 5, "max": 5},
        "constraints": {
            "fixed_operand2": 5
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    14: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 6, "max": 6},
        "constraints": {
            "fixed_operand2": 6
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    15: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 7, "max": 7},
        "constraints": {
            "fixed_operand2": 7
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    16: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 8, "max": 8},
        "constraints": {
            "fixed_operand2": 8
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    17: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 9, "max": 9},
        "constraints": {
            "fixed_operand2": 9
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    18: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {
            "fixed_operand2": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    19: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {
            "fixed_operand2": 10
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    20: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 11, "max": 11},
        "constraints": {
            "fixed_operand2": 11
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    21: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 12, "max": 12},
        "constraints": {
            "fixed_operand2": 12
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    22: {
        "operation": "addition",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    23: {
        "operation": "subtraction",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    24: {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "easy",
        "answer_format": "integer",
    },
    25: {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "normal",
        "answer_format": "integer",
    },
    26: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 1, "max": 1},
        "constraints": {
            "fixed_operand2": 1,
            "no_remainder": True
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    27: {
        "operation": "division",
        "operand1_range": {"min": 2, "max": 24},
        "operand2_range": {"min": 2, "max": 2},
        "constraints": {
            "fixed_operand2": 2,
            "no_remainder": True,
            "multiple_of": 2
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    28: {
        "operation": "division",
        "operand1_range": {"min": 3, "max": 36},
        "operand2_range": {"min": 3, "max": 3},
        "constraints": {
            "fixed_operand2": 3,
            "no_remainder": True,
            "multiple_of": 3
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    29: {
        "operation": "division",
        "operand1_range": {"min": 4, "max": 48},
        "operand2_range": {"min": 4, "max": 4},
        "constraints": {
            "fixed_operand2": 4,
            "no_remainder": True,
            "multiple_of": 4
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    30: {
        "operation": "division",
        "operand1_range": {"min": 5, "max": 60},
        "operand2_range": {"min": 5, "max": 5},
        "constraints": {
            "fixed_operand2": 5,
            "no_remainder": True,
            "multiple_of": 5
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    31: {
        "operation": "division",
        "operand1_range": {"min": 6, "max": 72},
        "operand2_range": {"min": 6, "max": 6},
        "constraints": {
            "fixed_operand2": 6,
            "no_remainder": True,
            "multiple_of": 6
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    32: {
        "operation": "division",
        "operand1_range": {"min": 7, "max": 84},
        "operand2_range": {"min": 7, "max": 7},
        "constraints": {
            "fixed_operand2": 7,
            "no_remainder": True,
            "multiple_of": 7
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    33: {
        "operation": "division",
        "operand1_range": {"min": 8, "max": 96},
        "operand2_range": {"min": 8, "max": 8},
        "constraints": {
            "fixed_operand2": 8,
            "no_remainder": True,
            "multiple_of": 8
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    34: {
        "operation": "division",
        "operand1_range": {"min": 9, "max": 108},
        "operand2_range": {"min": 9, "max": 9},
        "constraints": {
            "fixed_operand2": 9,
            "no_remainder": True,
            "multiple_of": 9
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    35: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 120},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {
            "fixed_operand2": 10,
            "no_remainder": True,
            "multiple_of": 10
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    36: {
        "operation": "division",
        "operand1_range": {"min": 11, "max": 132},
        "operand2_range": {"min": 11, "max": 11},
        "constraints": {
            "fixed_operand2": 11,
            "no_remainder": True,
            "multiple_of": 11
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    37: {
        "operation": "division",
        "operand1_range": {"min": 0, "max": 0},
        "operand2_range": {"min": 0, "max": 0},
        "constraints": {
            "fixed_operand2": 0,
            "no_remainder": True
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    38: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 120},
        "operand2_range": {"min": 10, "max": 10},
        "constraints": {
            "fixed_operand2": 10,
            "no_remainder": True,
            "multiple_of": 10
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    39: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
    },
    40: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
    },
    41: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    42: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    43: {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "normal",
        "answer_format": "integer",
    },
    44: {
        "operation": "division",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    45: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "decimal",
    },
    46: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "decimal",
    },
}
