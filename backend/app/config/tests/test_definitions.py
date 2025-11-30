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
    "addition-3digit": ("addition", 8, 40, {"max_digits": 3}, "3 Digit Addition"),
    
    # Subtraction Tests
    "subtraction-1digit": ("subtraction", 3, 50, {"max_digits": 1}, "1 Digit Subtraction"),
    "subtraction-1digit-zeros": ("subtraction", 3, 50, {"max_digits": 1, "allow_zeros": True}, "1 Digit Subtraction w/ Zeros"),
    "subtraction-1digit-negative": ("subtraction", 3, 50, {"max_digits": 1, "allow_negative": True}, "1 Digit Subtraction w/ Negative Numbers"),
    "subtraction-2digit": ("subtraction", 4, 50, {"max_digits": 2}, "2 Digit Subtraction"),
    "subtraction-3digit": ("subtraction", 23, 40, {"max_digits": 3}, "3 Digit Subtraction"),
    
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
    "multiplication-by-9": ("multiplication", 16, 100, {"multiplication_table": 9}, "Multiplication by 9"),
    "multiplication-by-10": ("multiplication", 19, 100, {"multiplication_table": 10}, "Multiplication by 10"),
    "multiplication-by-11": ("multiplication", 20, 100, {"multiplication_table": 11}, "Multiplication by 11"),
    "multiplication-by-12": ("multiplication", 21, 100, {"multiplication_table": 12}, "Multiplication by 12"),
    "multiplication-2digit": ("multiplication", 24, 50, {"multiplication_digits": 2}, "Multiplication Double Digit"),
    "multiplication-3digit": ("multiplication", 25, 40, {"multiplication_digits": 3}, "Multiplication 3 Digit"),
    
    # Division Tests - Divide by 1-12 (100 questions each)
    "division-by-1": ("division", 25, 100, {"division_table": 1}, "Division by 1"),
    "division-by-2": ("division", 26, 100, {"division_table": 2}, "Division by 2"),
    "division-by-3": ("division", 27, 100, {"division_table": 3}, "Division by 3"),
    "division-by-4": ("division", 28, 100, {"division_table": 4}, "Division by 4"),
    "division-by-5": ("division", 29, 100, {"division_table": 5}, "Division by 5"),
    "division-by-6": ("division", 30, 100, {"division_table": 6}, "Division by 6"),
    "division-by-7": ("division", 31, 100, {"division_table": 7}, "Division by 7"),
    "division-by-8": ("division", 32, 100, {"division_table": 8}, "Division by 8"),
    "division-by-9": ("division", 33, 100, {"division_table": 9}, "Division by 9"),
    "division-by-10": ("division", 35, 100, {"division_table": 10}, "Division by 10"),
    "division-by-11": ("division", 36, 100, {"division_table": 11}, "Division by 11"),
    "division-by-12": ("division", 37, 100, {"division_table": 12}, "Division by 12"),
    "division-no-remainder-single": ("division", 38, 50, {"division_digits": 1, "no_remainder": True}, "Division (No Remainder, Single Digit)"),
    "division-remainder": ("division", 39, 50, {"answer_format": "remainder"}, "Division (Remainder Format)"),
    "division-fraction": ("division", 40, 50, {"answer_format": "fraction"}, "Division (Fraction Format)"),
    "division-decimal": ("division", 44, 40, {"answer_format": "decimal"}, "Division (Decimal Format)"),
    "division-long": ("division", 45, 25, {"answer_format": "long_division"}, "Long Division"),
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
    
    return {
        "test_type": test_type,
        "operation": operation,
        "level_requirement": level_requirement,
        "question_count": question_count,
        "constraints": constraints,
        "display_name": display_name,
    }


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

