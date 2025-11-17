"""Declarative configuration for all 45 math levels, achievements, and progression requirements."""

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
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 0, "max": 9},
        "constraints": {
            "exclude_zeros": False,
            "answer_min": 2
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    3: {
        "operation": "subtraction",
        "operand1_range": {"min": 1, "max": 9},
        "operand2_range": {"min": 1, "max": 9},
        "constraints": {
            "exclude_zeros": True,
            "answer_min": 1
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    4: {
        "operation": "subtraction",
        "operand1_range": {"min": 0, "max": 9},
        "operand2_range": {"min": 0, "max": 9},
        "constraints": {
            "exclude_zeros": False,
            "answer_min": 0
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    5: {
        "operation": "addition",
        "operand1_range": {"min": 1, "max": 9},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    6: {
        "operation": "subtraction",
        "operand1_range": {"min": 1, "max": 9},
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
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 1, "max": 1},
        "constraints": {
            "fixed_operand2": 1
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    10: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 2, "max": 2},
        "constraints": {
            "fixed_operand2": 2
        },
        "layout_type": "vertical",
        "answer_format": "integer",
    },
    11: {
        "operation": "multiplication",
        "operand1_range": {"min": 1, "max": 12},
        "operand2_range": {"min": 3, "max": 3},
        "constraints": {
            "fixed_operand2": 3
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
        "operand1_range": {"min": 12, "max": 144},
        "operand2_range": {"min": 12, "max": 12},
        "constraints": {
            "fixed_operand2": 12,
            "no_remainder": True,
            "multiple_of": 12
        },
        "layout_type": "longDivision",
        "answer_format": "integer",
    },
    38: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
    },
    39: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "remainder",
    },
    40: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    41: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    42: {
        "operation": "multiplication",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 100, "max": 999},
        "constraints": {},
        "layout_type": "partialProducts",
        "partial_products_mode": "normal",
        "answer_format": "integer",
    },
    43: {
        "operation": "division",
        "operand1_range": {"min": 100, "max": 999},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "fraction",
    },
    44: {
        "operation": "division",
        "operand1_range": {"min": 1, "max": 99},
        "operand2_range": {"min": 2, "max": 9},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "decimal",
    },
    45: {
        "operation": "division",
        "operand1_range": {"min": 10, "max": 99},
        "operand2_range": {"min": 10, "max": 99},
        "constraints": {},
        "layout_type": "longDivision",
        "answer_format": "decimal",
    },
}

# Achievement definitions with requirements
ACHIEVEMENTS_CONFIG: dict[str, dict[str, Any]] = {
    "first-steps": {
        "title": "First Steps",
        "description": "Complete 10 addition problems",
        "icon": "👣",
        "category": "milestone",
        "requirements": {
            "type": "operation_count",
            "operation": "addition",
            "count": 10,
            "level": 1
        }
    },
    "addition-basics": {
        "title": "Addition Basics",
        "description": "Complete Level 1 with 80%+ accuracy",
        "icon": "⭐",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 1,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "subtraction-intro": {
        "title": "Subtraction Intro",
        "description": "Complete 10 subtraction problems",
        "icon": "➖",
        "category": "milestone",
        "requirements": {
            "type": "operation_count",
            "operation": "subtraction",
            "count": 10,
            "level": 3
        }
    },
    "subtraction-basics": {
        "title": "Subtraction Basics",
        "description": "Complete Level 3 with 80%+ accuracy",
        "icon": "⭐",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 3,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "mixed-addition": {
        "title": "Mixed Addition",
        "description": "Complete Level 2 with 20 correct answers",
        "icon": "➕",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 2,
            "min_correct": 20
        }
    },
    "mixed-subtraction": {
        "title": "Mixed Subtraction",
        "description": "Complete Level 4 with 20 correct answers",
        "icon": "➖",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 4,
            "min_correct": 20
        }
    },
    "double-addition": {
        "title": "Double Addition",
        "description": "Complete Level 5 with 80%+ accuracy",
        "icon": "➕",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 5,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "double-subtraction": {
        "title": "Double Subtraction",
        "description": "Complete Level 6 with 80%+ accuracy",
        "icon": "➖",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 6,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "multiply-by-one": {
        "title": "Multiply by One",
        "description": "Complete Level 7 with 30 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 7,
            "min_correct": 30
        }
    },
    "multiply-by-two": {
        "title": "Multiply by Two",
        "description": "Complete Level 9 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_1",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-three": {
        "title": "Multiply by Three",
        "description": "Complete Level 10 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_2",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-four": {
        "title": "Multiply by Four",
        "description": "Complete Level 11 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_3",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-five": {
        "title": "Multiply by Five",
        "description": "Complete Level 12 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_4",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-six": {
        "title": "Multiply by Six",
        "description": "Complete Level 13 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_5",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-seven": {
        "title": "Multiply by Seven",
        "description": "Complete Level 14 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_6",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-eight": {
        "title": "Multiply by Eight",
        "description": "Complete Level 15 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_7",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-nine": {
        "title": "Multiply by Nine",
        "description": "Complete Level 16 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_8",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-zero": {
        "title": "Multiply by Zero",
        "description": "Complete Level 17 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_9",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-ten": {
        "title": "Multiply by Ten",
        "description": "Complete Level 18 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_10",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-eleven": {
        "title": "Multiply by Eleven",
        "description": "Complete Level 19 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_11",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiply-by-twelve": {
        "title": "Multiply by Twelve",
        "description": "Complete Level 20 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "triple-addition": {
        "title": "Triple Addition",
        "description": "Complete Level 8 with 50 correct answers",
        "icon": "➕",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 8,
            "min_correct": 50
        }
    },
    "triple-subtraction": {
        "title": "Triple Subtraction",
        "description": "Complete Level 22 with 80%+ accuracy",
        "icon": "➖",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 22,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "multiplication-easy": {
        "title": "Multiplication Easy",
        "description": "Complete Level 21 test (20 questions, 90%+)",
        "icon": "✖️",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "multiplication_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "multiplication-work": {
        "title": "Multiplication Work",
        "description": "Complete Level 24 with 30 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 24,
            "min_correct": 30
        }
    },
    "divide-by-one": {
        "title": "Divide by One",
        "description": "Complete Level 25 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 25,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "divide-by-two": {
        "title": "Divide by Two",
        "description": "Complete Level 26 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_2",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-three": {
        "title": "Divide by Three",
        "description": "Complete Level 27 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_3",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-four": {
        "title": "Divide by Four",
        "description": "Complete Level 28 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_4",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-five": {
        "title": "Divide by Five",
        "description": "Complete Level 29 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_5",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-six": {
        "title": "Divide by Six",
        "description": "Complete Level 30 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_6",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-seven": {
        "title": "Divide by Seven",
        "description": "Complete Level 31 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_7",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-eight": {
        "title": "Divide by Eight",
        "description": "Complete Level 32 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_8",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-nine": {
        "title": "Divide by Nine",
        "description": "Complete Level 33 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_9",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-ten": {
        "title": "Divide by Ten",
        "description": "Complete Level 34 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_10",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-eleven": {
        "title": "Divide by Eleven",
        "description": "Complete Level 35 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_11",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "divide-by-twelve": {
        "title": "Divide by Twelve",
        "description": "Complete Level 36 test (20 questions, 90%+)",
        "icon": "➗",
        "category": "test-mastery",
        "requirements": {
            "type": "test_completion",
            "test_type": "division_12",
            "min_accuracy": 0.90,
            "question_count": 20
        }
    },
    "division-remainder": {
        "title": "Division Remainder",
        "description": "Complete Level 37 with 30 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 37,
            "min_correct": 30
        }
    },
    "division-double-remainder": {
        "title": "Division Double Remainder",
        "description": "Complete Level 38 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 38,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-fraction": {
        "title": "Division Fraction",
        "description": "Complete Level 38 with 20 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 38,
            "min_correct": 20
        }
    },
    "division-double-fraction": {
        "title": "Division Double Fraction",
        "description": "Complete Level 40 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 40,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "multiplication-triple": {
        "title": "Multiplication Triple",
        "description": "Complete Level 25 with 50 correct answers",
        "icon": "✖️",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 25,
            "min_correct": 50
        }
    },
    "division-triple-fraction": {
        "title": "Division Triple Fraction",
        "description": "Complete Level 41 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 41,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
    "division-decimal": {
        "title": "Division Decimal",
        "description": "Complete Level 40 with 20 correct answers",
        "icon": "➗",
        "category": "progression",
        "requirements": {
            "type": "level_correct_count",
            "level": 40,
            "min_correct": 20
        }
    },
    "division-double-decimal": {
        "title": "Division Double Decimal",
        "description": "Complete Level 44 with 80%+ accuracy",
        "icon": "➗",
        "category": "accuracy",
        "requirements": {
            "type": "level_accuracy",
            "level": 44,
            "min_accuracy": 0.80,
            "min_questions": 10
        }
    },
}

# Level progression requirements: which achievements unlock which levels
LEVEL_PROGRESSION_CONFIG: dict[int, list[dict[str, Any]]] = {
    2: [
        {"achievement_code": "addition-basics", "order": 1}
    ],
    3: [
        {"achievement_code": "subtraction-intro", "order": 1}
    ],
    4: [
        {"achievement_code": "subtraction-basics", "order": 1}
    ],
    5: [
        {"achievement_code": "mixed-addition", "order": 1}
    ],
    6: [
        {"achievement_code": "mixed-subtraction", "order": 1}
    ],
    7: [
        {"achievement_code": "double-addition", "order": 1}
    ],
    8: [
        {"achievement_code": "double-subtraction", "order": 1}
    ],
    9: [
        {"achievement_code": "multiply-by-one", "order": 1}
    ],
    10: [
        {"achievement_code": "multiply-by-two", "order": 1}
    ],
    11: [
        {"achievement_code": "multiply-by-three", "order": 1}
    ],
    12: [
        {"achievement_code": "multiply-by-four", "order": 1}
    ],
    13: [
        {"achievement_code": "multiply-by-five", "order": 1}
    ],
    14: [
        {"achievement_code": "multiply-by-six", "order": 1}
    ],
    15: [
        {"achievement_code": "multiply-by-seven", "order": 1}
    ],
    16: [
        {"achievement_code": "multiply-by-eight", "order": 1}
    ],
    17: [
        {"achievement_code": "multiply-by-nine", "order": 1}
    ],
    18: [
        {"achievement_code": "multiply-by-zero", "order": 1}
    ],
    19: [
        {"achievement_code": "multiply-by-ten", "order": 1}
    ],
    20: [
        {"achievement_code": "multiply-by-eleven", "order": 1}
    ],
    21: [
        {"achievement_code": "multiply-by-twelve", "order": 1}
    ],
    22: [
        {"achievement_code": "triple-addition", "order": 1}
    ],
    23: [
        {"achievement_code": "triple-subtraction", "order": 1}
    ],
    24: [
        {"achievement_code": "multiplication-easy", "order": 1}
    ],
    25: [
        {"achievement_code": "multiplication-work", "order": 1}
    ],
    26: [
        {"achievement_code": "divide-by-one", "order": 1}
    ],
    27: [
        {"achievement_code": "divide-by-two", "order": 1}
    ],
    28: [
        {"achievement_code": "divide-by-three", "order": 1}
    ],
    29: [
        {"achievement_code": "divide-by-four", "order": 1}
    ],
    30: [
        {"achievement_code": "divide-by-five", "order": 1}
    ],
    31: [
        {"achievement_code": "divide-by-six", "order": 1}
    ],
    32: [
        {"achievement_code": "divide-by-seven", "order": 1}
    ],
    33: [
        {"achievement_code": "divide-by-eight", "order": 1}
    ],
    34: [
        {"achievement_code": "divide-by-nine", "order": 1}
    ],
    35: [
        {"achievement_code": "divide-by-ten", "order": 1}
    ],
    36: [
        {"achievement_code": "divide-by-eleven", "order": 1}
    ],
    37: [
        {"achievement_code": "divide-by-twelve", "order": 1}
    ],
    38: [
        {"achievement_code": "division-remainder", "order": 1}
    ],
    39: [
        {"achievement_code": "division-double-remainder", "order": 1}
    ],
    40: [
        {"achievement_code": "division-fraction", "order": 1}
    ],
    41: [
        {"achievement_code": "division-double-fraction", "order": 1}
    ],
    42: [
        {"achievement_code": "multiplication-triple", "order": 1}
    ],
    43: [
        {"achievement_code": "division-triple-fraction", "order": 1}
    ],
    44: [
        {"achievement_code": "division-decimal", "order": 1}
    ],
    45: [
        {"achievement_code": "division-double-decimal", "order": 1}
    ],
}

