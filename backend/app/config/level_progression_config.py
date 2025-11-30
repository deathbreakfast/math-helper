"""Level progression requirements: which achievements unlock which levels."""

from typing import Any

# Level progression requirements: which achievements unlock which levels
LEVEL_PROGRESSION_CONFIG: dict[int, list[dict[str, Any]]] = {
    2: [
        {"achievement_code": "addition-basics", "order": 1}
    ],
    3: [
        {"achievement_code": "level-2-mastery", "order": 1}
    ],
    4: [
        {"achievement_code": "subtraction-basics", "order": 1}
    ],
    5: [
        {"achievement_code": "perfect-sessions-2", "order": 1},
        {"achievement_code": "basic-math-test", "order": 2},
        {"achievement_code": "level-5-mastery", "order": 3}
    ],
    6: [
        {"achievement_code": "level-6-mastery", "order": 1}
    ],
    7: [
        {"achievement_code": "level-7-mastery", "order": 1}
    ],
    8: [
        {"achievement_code": "level-8-mastery", "order": 1}
    ],
    9: [
        {"achievement_code": "level-9-mastery", "order": 1}
    ],
    10: [
        {"achievement_code": "level-10-mastery", "order": 1},
        {"achievement_code": "multiply-by-two-test-a", "order": 2}
    ],
    11: [
        {"achievement_code": "level-11-mastery", "order": 1},
        {"achievement_code": "multiply-by-three-test-a", "order": 2}
    ],
    12: [
        {"achievement_code": "level-12-mastery", "order": 1},
        {"achievement_code": "multiply-by-four-test-a", "order": 2}
    ],
    13: [
        {"achievement_code": "level-13-mastery", "order": 1},
        {"achievement_code": "multiply-by-five-test-a", "order": 2}
    ],
    14: [
        {"achievement_code": "level-14-mastery", "order": 1},
        {"achievement_code": "multiply-by-six-test-a", "order": 2}
    ],
    15: [
        {"achievement_code": "level-15-mastery", "order": 1},
        {"achievement_code": "multiply-by-seven-test-a", "order": 2}
    ],
    16: [
        {"achievement_code": "level-16-mastery", "order": 1},
        {"achievement_code": "multiply-by-eight-test-a", "order": 2}
    ],
    17: [
        {"achievement_code": "level-17-mastery", "order": 1},
        {"achievement_code": "multiply-by-nine-test-a", "order": 2}
    ],
    18: [
        {"achievement_code": "level-18-mastery", "order": 1},
        {"achievement_code": "multiply-by-zero-test-a", "order": 2}
    ],
    19: [
        {"achievement_code": "level-19-mastery", "order": 1},
        {"achievement_code": "multiply-by-ten-test-a", "order": 2}
    ],
    20: [
        {"achievement_code": "level-20-mastery", "order": 1},
        {"achievement_code": "multiply-by-eleven-test-a", "order": 2}
    ],
    21: [
        {"achievement_code": "level-21-mastery", "order": 1},
        {"achievement_code": "multiply-by-twelve-test-a", "order": 2}
    ],
    22: [
        {"achievement_code": "level-22-mastery", "order": 1}
    ],
    23: [
        {"achievement_code": "level-23-mastery", "order": 1}
    ],
    24: [
        {"achievement_code": "level-24-mastery", "order": 1}
    ],
    25: [
        {"achievement_code": "level-25-mastery", "order": 1}
    ],
    26: [
        {"achievement_code": "level-25-mastery", "order": 1},
        {"achievement_code": "multiplication-mastery", "order": 2},
        {"achievement_code": "addition-mastery", "order": 3},
        {"achievement_code": "subtraction-mastery", "order": 4},
        {"achievement_code": "addition-subtraction-advanced-mastery", "order": 5}
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

