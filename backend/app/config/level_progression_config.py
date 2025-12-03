"""Level progression requirements: which achievements unlock which levels."""

from typing import Any

# Level progression requirements: which achievements unlock which levels
# Updated to use test achievements instead of {operation}-basics achievements
# {operation}-basics achievements are legacy and removed - use test achievements instead
LEVEL_PROGRESSION_CONFIG: dict[int, list[dict[str, Any]]] = {
    2: [
        {"achievement_code": "addition-1digit-bronze", "quantity": 1, "order": 1}  # Level 2 - addition test
    ],
    3: [
        {"achievement_code": "addition-1digit-bronze", "quantity": 1, "order": 1}  # Level 3 - addition test
    ],
    4: [
        {"achievement_code": "subtraction-1digit-bronze", "quantity": 1, "order": 1}  # Level 4 - subtraction test
    ],
    5: [
        {"achievement_code": "perfect-streak-bronze", "quantity": 1, "order": 1},  # 3 consecutive perfect sessions
        {"achievement_code": "addition-1digit-bronze", "quantity": 1, "order": 2},  # Test achievement
    ],
    6: [
        {"achievement_code": "subtraction-1digit-bronze", "quantity": 1, "order": 1}  # Level 6 - subtraction test
    ],
    7: [
        {"achievement_code": "addition-2digit-bronze", "quantity": 1, "order": 1}  # Level 7 - addition test
    ],
    8: [
        {"achievement_code": "subtraction-2digit-bronze", "quantity": 1, "order": 1}  # Level 8 - subtraction test
    ],
    9: [
        {"achievement_code": "multiplication-by-1-bronze", "quantity": 1, "order": 1}  # Level 9 - multiplication test
    ],
    10: [
        {"achievement_code": "multiplication-by-2-silver", "quantity": 1, "order": 1}  # Level 10 - multiplication test
    ],
    11: [
        {"achievement_code": "multiplication-by-3-silver", "quantity": 1, "order": 1}  # Level 11 - multiplication test
    ],
    12: [
        {"achievement_code": "multiplication-by-4-silver", "quantity": 1, "order": 1}  # Level 12 - multiplication test
    ],
    13: [
        {"achievement_code": "multiplication-by-5-silver", "quantity": 1, "order": 1}  # Level 13 - multiplication test
    ],
    14: [
        {"achievement_code": "multiplication-by-6-silver", "quantity": 1, "order": 1}  # Level 14 - multiplication test
    ],
    15: [
        {"achievement_code": "multiplication-by-7-silver", "quantity": 1, "order": 1}  # Level 15 - multiplication test
    ],
    16: [
        {"achievement_code": "multiplication-by-8-silver", "quantity": 1, "order": 1}  # Level 16 - multiplication test
    ],
    17: [
        {"achievement_code": "multiplication-by-9-silver", "quantity": 1, "order": 1}  # Level 17 - multiplication test
    ],
    18: [
        {"achievement_code": "multiplication-by-2-silver", "quantity": 1, "order": 1}  # Level 18 - multiplication test (proxy for ×0)
    ],
    19: [
        {"achievement_code": "multiplication-by-10-silver", "quantity": 1, "order": 1}  # Level 19 - multiplication test
    ],
    20: [
        {"achievement_code": "multiplication-by-11-silver", "quantity": 1, "order": 1}  # Level 20 - multiplication test
    ],
    21: [
        {"achievement_code": "multiplication-by-12-silver", "quantity": 1, "order": 1}  # Level 21 - multiplication test
    ],
    22: [
        {"achievement_code": "addition-3digit-bronze", "quantity": 1, "order": 1}  # Level 22 - addition test
    ],
    23: [
        {"achievement_code": "subtraction-3digit-bronze", "quantity": 1, "order": 1}  # Level 23 - subtraction test
    ],
    24: [
        {"achievement_code": "multiplication-2digit-bronze", "quantity": 1, "order": 1}  # Level 24 - multiplication test
    ],
    25: [
        {"achievement_code": "multiplication-2digit-bronze", "quantity": 1, "order": 1}  # Level 25 - multiplication test
    ],
    26: [
        {"achievement_code": "multiplication-2digit-gold", "quantity": 1, "order": 1},  # Level 26 - mastery tier
        {"achievement_code": "addition-2digit-gold", "quantity": 1, "order": 2},  # Mastery tier
        {"achievement_code": "subtraction-2digit-gold", "quantity": 1, "order": 3},  # Mastery tier
    ],
    27: [
        {"achievement_code": "division-by-2-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    28: [
        {"achievement_code": "division-by-3-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    29: [
        {"achievement_code": "division-by-4-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    30: [
        {"achievement_code": "division-by-5-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    31: [
        {"achievement_code": "division-by-6-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    32: [
        {"achievement_code": "division-by-7-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    33: [
        {"achievement_code": "division-by-8-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    34: [
        {"achievement_code": "division-by-9-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    35: [
        {"achievement_code": "division-by-10-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    36: [
        {"achievement_code": "division-by-11-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    37: [
        {"achievement_code": "division-by-12-silver", "quantity": 1, "order": 1}  # Test achievement
    ],
    38: [
        {"achievement_code": "division-2digit-bronze", "quantity": 1, "order": 1}  # Level 38 - division test
    ],
    39: [
        {"achievement_code": "division-2digit-bronze", "quantity": 1, "order": 1}  # Level 39 - division test
    ],
    40: [
        {"achievement_code": "division-2digit-bronze", "quantity": 1, "order": 1}  # Level 40 - division test
    ],
    41: [
        {"achievement_code": "division-2digit-bronze", "quantity": 1, "order": 1}  # Level 41 - division test
    ],
    42: [
        {"achievement_code": "multiplication-3digit-bronze", "quantity": 1, "order": 1}  # Level 42 - multiplication test
    ],
    43: [
        {"achievement_code": "division-3digit-bronze", "quantity": 1, "order": 1}  # Level 43 - division test
    ],
    44: [
        {"achievement_code": "division-3digit-bronze", "quantity": 1, "order": 1}  # Level 44 - division test
    ],
    45: [
        {"achievement_code": "division-3digit-bronze", "quantity": 1, "order": 1}  # Level 45 - division test
    ],
}
