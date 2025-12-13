"""Comprehensive test definitions matching user requirements.

This module defines all new test types with descriptive identifiers,
while maintaining backward compatibility with existing test types.
"""

from typing import Any

# New test definitions with descriptive identifiers
# Format: test_type: (operation, level_requirement, question_count, constraints, display_name)
NEW_TEST_DEFINITIONS: dict[str, tuple[str, int, int, dict[str, Any], str]] = {
    # Addition Tests
    "addition-1digit": ("addition", 1, 50, {"max_digits": 1}, "1 Digit Addition"),
    "addition-1digit-zeros": ("addition", 1, 50, {"max_digits": 1, "allow_zeros": True}, "1 Digit Addition w/ Zeros"),
    "addition-1digit-negative": ("addition", 1, 50, {"max_digits": 1, "allow_negative": True}, "1 Digit Addition w/ Negative Numbers"),
    "addition-2digit": ("addition", 2, 50, {"max_digits": 2}, "2 Digit Addition"),
    "addition-3digit": ("addition", 24, 40, {"max_digits": 3}, "3 Digit Addition"),
    
    # Subtraction Tests
    "subtraction-1digit": ("subtraction", 3, 50, {"max_digits": 1}, "1 Digit Subtraction"),
    "subtraction-1digit-zeros": ("subtraction", 3, 50, {"max_digits": 1, "allow_zeros": True}, "1 Digit Subtraction w/ Zeros"),
    "subtraction-1digit-negative": ("subtraction", 3, 50, {"max_digits": 1, "allow_negative": True}, "1 Digit Subtraction w/ Negative Numbers"),
    "subtraction-2digit": ("subtraction", 4, 50, {"max_digits": 2}, "2 Digit Subtraction"),
    "subtraction-3digit": ("subtraction", 25, 40, {"max_digits": 3}, "3 Digit Subtraction"),
    
    # Mixed Tests
    "basic-math-mixed": ("mixed", 5, 100, {"max_digits": 3, "operations": ["addition", "subtraction"]}, "Basic Math (Mixed)"),
    
    # Multiplication Tests - Multiply by 1-12 (100 questions each)
    "multiplication-by-1": ("multiplication", 7, 100, {"multiplication_table": 1}, "Multiplication by 1"),
    "multiplication-by-2": ("multiplication", 9, 100, {"multiplication_table": 2}, "Multiplication by 2"),
    "multiplication-by-3": ("multiplication", 10, 100, {"multiplication_table": 3}, "Multiplication by 3"),
    "multiplication-by-4": ("multiplication", 11, 100, {"multiplication_table": 4}, "Multiplication by 4"),
    "multiplication-by-5": ("multiplication", 12, 100, {"multiplication_table": 5}, "Multiplication by 5"),
    "multiplication-by-6": ("multiplication", 13, 100, {"multiplication_table": 6}, "Multiplication by 6"),
    "multiplication-by-7": ("multiplication", 14, 100, {"multiplication_table": 7}, "Multiplication by 7"),
    "multiplication-by-8": ("multiplication", 15, 100, {"multiplication_table": 8}, "Multiplication by 8"),
    "multiplication-by-9": ("multiplication", 19, 100, {"multiplication_table": 9}, "Multiplication by 9"),
    "multiplication-by-0": ("multiplication", 20, 100, {"multiplication_table": 0}, "Multiplication by 0"),
    "multiplication-by-10": ("multiplication", 21, 100, {"multiplication_table": 10}, "Multiplication by 10"),
    "multiplication-by-11": ("multiplication", 22, 100, {"multiplication_table": 11}, "Multiplication by 11"),
    "multiplication-by-12": ("multiplication", 23, 100, {"multiplication_table": 12}, "Multiplication by 12"),
    "multiplication-2digit": ("multiplication", 27, 50, {"multiplication_digits": 2}, "Multiplication Double Digit"),
    "multiplication-3digit": ("multiplication", 44, 40, {"multiplication_digits": 3}, "Multiplication 3 Digit"),
    
    # Division Tests - Divide by 1-12 (100 questions each)
    "division-by-1": ("division", 28, 100, {"division_table": 1}, "Division by 1"),
    "division-by-2": ("division", 29, 100, {"division_table": 2}, "Division by 2"),
    "division-by-3": ("division", 30, 100, {"division_table": 3}, "Division by 3"),
    "division-by-4": ("division", 31, 100, {"division_table": 4}, "Division by 4"),
    "division-by-5": ("division", 32, 100, {"division_table": 5}, "Division by 5"),
    "division-by-6": ("division", 33, 100, {"division_table": 6}, "Division by 6"),
    "division-by-7": ("division", 34, 100, {"division_table": 7}, "Division by 7"),
    "division-by-8": ("division", 35, 100, {"division_table": 8}, "Division by 8"),
    "division-by-9": ("division", 36, 100, {"division_table": 9}, "Division by 9"),
    "division-by-0": ("division", 37, 100, {"division_table": 0}, "Division by 0"),
    "division-by-10": ("division", 38, 100, {"division_table": 10}, "Division by 10"),
    "division-by-11": ("division", 39, 100, {"division_table": 11}, "Division by 11"),
    "division-by-12": ("division", 40, 100, {"division_table": 12}, "Division by 12"),
    "division-no-remainder-single": ("division", 41, 50, {"division_digits": 1, "no_remainder": True}, "Division (No Remainder, Single Digit)"),
    "division-remainder": ("division", 42, 50, {"answer_format": "remainder"}, "Division (Remainder Format)"),
    "division-fraction": ("division", 43, 50, {"answer_format": "fraction"}, "Division (Fraction Format)"),
    "division-decimal": ("division", 44, 40, {"answer_format": "decimal"}, "Division (Decimal Format)"),
    "division-long": ("division", 45, 25, {"answer_format": "long_division"}, "Long Division"),
}

# Unlock requirements for each test type
# Format: achievement-based unlocking requirements
# Note: Higher tier achievements can substitute for lower tier requirements (4 bronze = 2 silver = 1 gold)
TEST_UNLOCK_REQUIREMENTS: dict[str, dict[str, Any]] = {
    # Addition Tests
    "addition-1digit": {
        "type": "achievement",
        "achievement_codes": ["level-master-bronze"],
        "metadata_filters": {
            "level-master-bronze": {"level": 1}
        },
        "quantity": 1,
        "expected_level": 1,  # Expected user level annotation
    },
    "addition-1digit-zeros": {
        "type": "achievement",
        "achievement_codes": ["level-master-bronze", "perfect-streak-bronze"],
        "metadata_filters": {
            "level-master-bronze": {"level": 2}
        },
        "quantity": 1,
        "expected_level": 2,
    },
    "addition-1digit-negative": {
        "type": "level",
        "level": 5,
        "min_accuracy": 1.0,
        "operation": "addition",
        "expected_level": 5,
    },
    "addition-2digit": {
        "type": "achievement",
        "achievement_codes": ["speed-demon-silver", "perfect-streak-gold"],
        "quantity": 10,  # Speed demon silver qty 10
        "expected_level": 7,
    },
    "addition-3digit": {
        "type": "achievement",
        "achievement_codes": [
            "level-master-platinum",
            "level-master-platinum",
            "level-master-platinum",
            "level-master-silver"
        ],
        "metadata_filters": {
            "level-master-platinum": {"level": 1},
            "level-master-platinum": {"level": 2},
            "level-master-platinum": {"level": 7},
            "level-master-silver": {"level": 24},
        },
        "quantity": 1,
        "expected_level": 24,
    },
    
    # Subtraction Tests
    "subtraction-1digit": {
        "type": "achievement",
        "achievement_codes": ["level-master-bronze", "question-master-silver"],
        "metadata_filters": {
            "level-master-bronze": {"level": 3}
        },
        "quantity": 1,
        "expected_level": 3,
    },
    "subtraction-1digit-zeros": {
        "type": "achievement",
        "achievement_codes": ["level-master-bronze", "so-wow-gold"],
        "metadata_filters": {
            "level-master-bronze": {"level": 3}
        },
        "quantity": 1,
        "expected_level": 4,
    },
    "subtraction-1digit-negative": {
        "type": "level",
        "level": 6,
        "min_accuracy": 1.0,
        "operation": "subtraction",
        "expected_level": 6,
    },
    "subtraction-2digit": {
        "type": "achievement",
        "achievement_codes": [
            "level-master-bronze",
            "level-master-bronze",
            "level-master-silver",
            "level-master-gold",
            "level-master-silver",
            "level-master-gold"
        ],
        "metadata_filters": {
            "level-master-bronze": {"level": 5},
            "level-master-bronze": {"level": 6},
            "level-master-silver": {"level": 1},
            "level-master-gold": {"level": 2},
            "level-master-silver": {"level": 3},
            "level-master-gold": {"level": 4},
        },
        "quantity": 1,
        "expected_level": 10,
    },
    "subtraction-3digit": {
        "type": "achievement",
        "achievement_codes": [
            "level-master-platinum",
            "level-master-platinum",
            "level-master-platinum",
            "level-master-silver"
        ],
        "metadata_filters": {
            "level-master-platinum": {"level": 8},
            "level-master-platinum": {"level": 9},
            "level-master-platinum": {"level": 10},
            "level-master-silver": {"level": 25},
        },
        "quantity": 1,
        "expected_level": 25,
    },
    
    # Mixed Tests
    "basic-math-mixed": {
        "type": "level",
        "level": 7,
        "min_accuracy": 1.0,
        "operation": "addition",
    },
    
    # Multiplication Tests
    "multiplication-by-1": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond"],
        "metadata_filters": {
            "level-master-gold": {"level": 11},
            "lightning-fast-diamond": {"level": 1},
        },
        "quantity": 1,
        "expected_level": 11,
    },
    "multiplication-by-2": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 12},
            "lightning-fast-gold": {"level": 12},
            "level-master-gold": {"level": 1},
        },
        "quantity": 1,
        "expected_level": 12,
    },
    "multiplication-by-3": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 13},
            "lightning-fast-gold": {"level": 13},
            "level-master-gold": {"level": 7},
        },
        "quantity": 1,
        "expected_level": 13,
    },
    "multiplication-by-4": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 14},
            "lightning-fast-gold": {"level": 14},
            "level-master-gold": {"level": 12},
        },
        "quantity": 1,
        "expected_level": 14,
    },
    "multiplication-by-5": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-platinum", "accuracy-ace-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 15},
            "lightning-fast-platinum": {"level": 15},
        },
        "quantity": 20,  # Accuracy Ace gold qty 20
        "expected_level": 15,
    },
    "multiplication-by-6": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "perfect-streak-platinum"],
        "metadata_filters": {
            "level-master-silver": {"level": 16},
            "lightning-fast-gold": {"level": 16},
        },
        "quantity": 1,
        "expected_level": 16,
    },
    "multiplication-by-7": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "speed-demon-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 17},
            "lightning-fast-gold": {"level": 17},
        },
        "quantity": 20,  # Speed demon gold qty 20
        "expected_level": 17,
    },
    "multiplication-by-8": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "lightning-fast-platinum"],
        "metadata_filters": {
            "level-master-silver": {"level": 18},
            "lightning-fast-gold": {"level": 18},
            "lightning-fast-platinum": {"level": 1},
        },
        "quantity": 1,
        "expected_level": 18,
    },
    "multiplication-by-9": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 19},
            "lightning-fast-gold": {"level": 19},
        },
        "quantity": 1,
        "expected_level": 19,
    },
    "multiplication-by-0": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond", "lightning-fast-diamond"],
        "metadata_filters": {
            "level-master-gold": {"level": 20},
            "lightning-fast-diamond": {"level": 2},
            "lightning-fast-diamond": {"level": 20},
        },
        "quantity": 1,
        "expected_level": 20,
    },
    "multiplication-by-10": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond"],
        "metadata_filters": {
            "level-master-gold": {"level": 21},
            "lightning-fast-diamond": {"level": 21},
        },
        "quantity": 1,
        "expected_level": 21,
    },
    "multiplication-by-11": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "speed-demon-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 22},
            "lightning-fast-gold": {"level": 22},
        },
        "quantity": 40,  # Speed demon gold qty 40
        "expected_level": 22,
    },
    "multiplication-by-12": {
        "type": "achievement",
        "achievement_codes": [
            "level-master-silver",
            "lightning-fast-gold",
            "perfect-streak-platinum",
            "perfect-streak-gold"
        ],
        "metadata_filters": {
            "level-master-silver": {"level": 23},
            "lightning-fast-gold": {"level": 23},
        },
        "quantities": {
            "level-master-silver": 1,
            "lightning-fast-gold": 1,
            "perfect-streak-platinum": 2,
            "perfect-streak-gold": 6,
        },
        "expected_level": 23,
    },
    "multiplication-2digit": {
        "type": "achievement",
        "achievement_codes": [
            "level-master-diamond",
            "level-master-diamond",
            "lightning-fast-master",
            "master-of-times-tables-gold",
            "level-master-silver"
        ],
        "metadata_filters": {
            "level-master-diamond": {"level": 1},
            "level-master-diamond": {"level": 2},
            "lightning-fast-master": {"level": 1},
            "level-master-silver": {"level": 27},
        },
        "quantity": 1,
        "expected_level": 27,
    },
    "multiplication-3digit": {
        "type": "achievement",
        "achievement_codes": [
            "master-of-times-tables-platinum",
            "level-master-gold",
            "level-master-master",
            "level-master-diamond",
            "level-master-diamond",
            "level-master-silver"
        ],
        "metadata_filters": {
            "level-master-gold": {"level": 27},
            "level-master-master": {"level": 1},
            "level-master-diamond": {"level": 5},
            "level-master-diamond": {"level": 7},
            "level-master-silver": {"level": 44},
        },
        "quantity": 1,
        "expected_level": 44,
    },
    
    # Division Tests
    "division-by-1": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond", "speed-demon-platinum"],
        "metadata_filters": {
            "level-master-gold": {"level": 28},
            "lightning-fast-diamond": {"level": 28},
        },
        "quantity": 20,  # Speed demon platinum qty 20
        "expected_level": 28,
    },
    "division-by-2": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 29},
            "lightning-fast-gold": {"level": 29},
            "level-master-gold": {"level": 3},
        },
        "quantity": 1,
        "expected_level": 29,
    },
    "division-by-3": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 30},
            "lightning-fast-gold": {"level": 30},
            "level-master-gold": {"level": 8},
        },
        "quantity": 1,
        "expected_level": 30,
    },
    "division-by-4": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 31},
            "lightning-fast-gold": {"level": 31},
            "level-master-gold": {"level": 9},
        },
        "quantity": 1,
        "expected_level": 31,
    },
    "division-by-5": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "level-master-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 32},
            "lightning-fast-gold": {"level": 32},
            "level-master-gold": {"level": 10},
        },
        "quantity": 1,
        "expected_level": 32,
    },
    "division-by-6": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "lightning-fast-platinum"],
        "metadata_filters": {
            "level-master-silver": {"level": 33},
            "lightning-fast-gold": {"level": 33},
            "lightning-fast-platinum": {"level": 3},
        },
        "quantity": 1,
        "expected_level": 33,
    },
    "division-by-7": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "lightning-fast-platinum"],
        "metadata_filters": {
            "level-master-silver": {"level": 34},
            "lightning-fast-gold": {"level": 34},
            "lightning-fast-platinum": {"level": 4},
        },
        "quantity": 1,
        "expected_level": 34,
    },
    "division-by-8": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "lightning-fast-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 35},
            "lightning-fast-gold": {"level": 35},
            "lightning-fast-gold": {"level": 7},
        },
        "quantity": 1,
        "expected_level": 35,
    },
    "division-by-9": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold", "speed-demon-platinum"],
        "metadata_filters": {
            "level-master-silver": {"level": 36},
            "lightning-fast-gold": {"level": 36},
        },
        "quantity": 40,  # Speed demon platinum qty 40
        "expected_level": 36,
    },
    "division-by-0": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond", "level-master-gold"],
        "metadata_filters": {
            "level-master-gold": {"level": 37},
            "lightning-fast-diamond": {"level": 37},
            "level-master-gold": {"level": 4},
        },
        "quantity": 1,
        "expected_level": 37,
    },
    "division-by-10": {
        "type": "achievement",
        "achievement_codes": ["level-master-gold", "lightning-fast-diamond"],
        "metadata_filters": {
            "level-master-gold": {"level": 38},
            "lightning-fast-diamond": {"level": 38},
        },
        "quantity": 1,
        "expected_level": 38,
    },
    "division-by-11": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 39},
            "lightning-fast-gold": {"level": 39},
        },
        "quantity": 1,
        "expected_level": 39,
    },
    "division-by-12": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver", "lightning-fast-gold"],
        "metadata_filters": {
            "level-master-silver": {"level": 40},
            "lightning-fast-gold": {"level": 40},
        },
        "quantity": 1,
        "expected_level": 40,
    },
    "division-no-remainder-single": {
        "type": "achievement",
        "achievement_codes": ["master-of-division-tables-gold", "level-master-silver"],
        "metadata_filters": {
            "level-master-silver": {"level": 41},
        },
        "quantity": 1,
        "expected_level": 41,
    },
    "division-remainder": {
        "type": "achievement",
        "achievement_codes": ["level-master-silver"],
        "metadata_filters": {
            "level-master-silver": {"level": 42},  # Level TBD per spec
        },
        "quantity": 1,
        "expected_level": 42,
    },
    "division-fraction": {
        "type": "achievement",
        "achievement_codes": ["master-of-division-tables-platinum", "level-master-silver"],
        "metadata_filters": {
            "level-master-silver": {"level": 43},  # Level TBD per spec
        },
        "quantity": 1,
        "expected_level": 43,
    },
    "division-decimal": {
        "type": "level",
        "min_accuracy": 1.0,
        "operation": "division",
    },
    "division-long": {
        "type": "level",
        "min_accuracy": 1.0,
        "operation": "division",
    },
}


def get_test_definition(test_type: str) -> dict[str, Any] | None:
    """Get test definition for a specific test type.
    
    Args:
        test_type: The test type identifier (e.g., "addition-1digit")
        
    Returns:
        Dictionary with test definition or None if not found
    """
    if test_type not in NEW_TEST_DEFINITIONS:
        return None
    
    operation, level_requirement, question_count, constraints, display_name = NEW_TEST_DEFINITIONS[test_type]
    
    result = {
        "test_type": test_type,
        "operation": operation,
        "level_requirement": level_requirement,  # Deprecated: kept for backward compatibility
        "question_count": question_count,
        "constraints": constraints,
        "display_name": display_name,
    }
    
    # Add unlock_requirements if available
    if test_type in TEST_UNLOCK_REQUIREMENTS:
        result["unlock_requirements"] = TEST_UNLOCK_REQUIREMENTS[test_type]
    
    return result


def get_all_test_definitions() -> list[dict[str, Any]]:
    """Get all new test definitions.
    
    Returns:
        List of test definition dictionaries
    """
    return [
        get_test_definition(test_type)
        for test_type in NEW_TEST_DEFINITIONS.keys()
    ]


def get_test_definitions_by_level(level: int) -> list[dict[str, Any]]:
    """Get all test definitions available at a specific level.
    
    Args:
        level: The user's current level
        
    Returns:
        List of test definition dictionaries available at this level
    """
    return [
        get_test_definition(test_type)
        for test_type, (_, req_level, _, _, _) in NEW_TEST_DEFINITIONS.items()
        if req_level <= level
    ]

