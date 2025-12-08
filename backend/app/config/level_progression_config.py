"""Level progression requirements: which achievements unlock which levels."""

from typing import Any

# Level progression requirements: which achievements unlock which levels
# Updated to use existing achievements (level-master, lightning-fast) with metadata instead of test achievements
# Test achievements have been removed - use existing achievements with level-specific metadata
# Note: Higher tier achievements can substitute for lower tier requirements (4 bronze = 2 silver = 1 gold)
LEVEL_PROGRESSION_CONFIG: dict[int, list[dict[str, Any]]] = {
    2: [
        {"achievement_code": "first-steps", "quantity": 1, "order": 1},
        {"achievement_code": "first-victory", "quantity": 1, "order": 2},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "addition-1digit"}, "quantity": 1, "order": 3},
    ],
    3: [
        {"achievement_code": "question-master-bronze", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "addition-1digit-zeros"}, "quantity": 1, "order": 2},
    ],
    4: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "subtraction-1digit"}, "quantity": 1, "order": 1},
    ],
    5: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "subtraction-1digit-zeros"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-silver", "quantity": 1, "order": 2},
    ],
    6: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "addition-2digit"}, "quantity": 1, "order": 1},
    ],
    7: [
        {"achievement_code": "question-master-gold", "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-silver", "quantity": 5, "order": 2},
        {"achievement_code": "perfect-streak-silver", "quantity": 5, "order": 3},
        {"achievement_code": "level-master-bronze", "metadata_filter": {"level": 5}, "quantity": 2, "order": 4},
    ],
    8: [
        {"achievement_code": "speed-demon-gold", "quantity": 2, "order": 1},
        {"achievement_code": "perfect-streak-gold", "quantity": 2, "order": 2},
        {"achievement_code": "level-master-bronze", "metadata_filter": {"level": 6}, "quantity": 2, "order": 3},
    ],
    9: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "addition-2digit"}, "quantity": 1, "order": 1},
    ],
    10: [
        {"achievement_code": "speed-demon-gold", "quantity": 10, "order": 1},
        {"achievement_code": "perfect-streak-gold", "quantity": 10, "order": 2},
        {"achievement_code": "level-master-silver", "metadata_filter": {"level": 8}, "quantity": 1, "order": 3},
        {"achievement_code": "question-master-platinum", "quantity": 1, "order": 4},
    ],
    11: [
        {"achievement_code": "so-wow-platinum", "quantity": 1, "order": 1},
        {"achievement_code": "question-master-gold", "quantity": 1, "order": 2},
        {"achievement_code": "level-master-silver", "metadata_filter": {"level": 9}, "quantity": 1, "order": 3},
        {"achievement_code": "level-master-silver", "metadata_filter": {"level": 8}, "quantity": 2, "order": 4},
    ],
    12: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "subtraction-2digit"}, "quantity": 1, "order": 1},
    ],
    13: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-2"}, "quantity": 1, "order": 1},
    ],
    14: [
        {"achievement_code": "question-master-diamond", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-3"}, "quantity": 1, "order": 2},
    ],
    15: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-4"}, "quantity": 1, "order": 1},
    ],
    16: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-5"}, "quantity": 1, "order": 1},
    ],
    17: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-6"}, "quantity": 1, "order": 1},
    ],
    18: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-7"}, "quantity": 1, "order": 1},
    ],
    19: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-8"}, "quantity": 1, "order": 1},
    ],
    20: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-9"}, "quantity": 1, "order": 1},
    ],
    21: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-0"}, "quantity": 1, "order": 1},
    ],
    22: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-10"}, "quantity": 1, "order": 1},
    ],
    23: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-11"}, "quantity": 1, "order": 1},
    ],
    24: [
        {"achievement_code": "question-master-master", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-by-12"}, "quantity": 1, "order": 2},
    ],
    25: [
        {"achievement_code": "so-wow-diamond", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "addition-3digit"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-diamond", "metadata_filter": {"test_type": "addition-1digit"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-bronze", "metadata_filter": {"test_type": "addition-2digit"}, "quantity": 1, "order": 4},
    ],
    26: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "subtraction-3digit"}, "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-diamond", "metadata_filter": {"test_type": "subtraction-1digit"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-bronze", "metadata_filter": {"test_type": "subtraction-2digit"}, "quantity": 1, "order": 3},
    ],
    27: [
        {"achievement_code": "question-master-grandmaster", "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-0"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-1"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-2"}, "quantity": 1, "order": 4},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-3"}, "quantity": 1, "order": 5},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-4"}, "quantity": 1, "order": 6},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-5"}, "quantity": 1, "order": 7},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-6"}, "quantity": 1, "order": 8},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-7"}, "quantity": 1, "order": 9},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-8"}, "quantity": 1, "order": 10},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-9"}, "quantity": 1, "order": 11},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-10"}, "quantity": 1, "order": 12},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-11"}, "quantity": 1, "order": 13},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "multiplication-by-12"}, "quantity": 1, "order": 14},
    ],
    28: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-2digit"}, "quantity": 1, "order": 1},
    ],
    29: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-1"}, "quantity": 1, "order": 1},
    ],
    30: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-2"}, "quantity": 1, "order": 1},
    ],
    31: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-3"}, "quantity": 1, "order": 1},
    ],
    32: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-4"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-legendary", "quantity": 1, "order": 2},
    ],
    33: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-5"}, "quantity": 1, "order": 1},
    ],
    34: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-6"}, "quantity": 1, "order": 1},
    ],
    35: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-7"}, "quantity": 1, "order": 1},
    ],
    36: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-8"}, "quantity": 1, "order": 1},
    ],
    37: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-0"}, "quantity": 1, "order": 1},
    ],
    38: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-0"}, "quantity": 1, "order": 1},
    ],
    39: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-10"}, "quantity": 1, "order": 1},
    ],
    40: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-11"}, "quantity": 1, "order": 1},
    ],
    41: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-by-12"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-mythic", "quantity": 1, "order": 2},
    ],
    42: [
        {"achievement_code": "so-wow-master", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-no-remainder-single"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-0"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-1"}, "quantity": 1, "order": 4},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-2"}, "quantity": 1, "order": 5},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-3"}, "quantity": 1, "order": 6},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-4"}, "quantity": 1, "order": 7},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-5"}, "quantity": 1, "order": 8},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-6"}, "quantity": 1, "order": 9},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-7"}, "quantity": 1, "order": 10},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-8"}, "quantity": 1, "order": 11},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-9"}, "quantity": 1, "order": 12},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-10"}, "quantity": 1, "order": 13},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-11"}, "quantity": 1, "order": 14},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"test_type": "division-by-12"}, "quantity": 1, "order": 15},
    ],
    43: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-remainder"}, "quantity": 1, "order": 1},
    ],
    44: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "division-fraction"}, "quantity": 1, "order": 1},
        {"achievement_code": "so-wow-grandmaster", "quantity": 1, "order": 2},
    ],
    45: [
        {"achievement_code": "accuracy-ace-platinum", "metadata_filter": {"test_type": "multiplication-3digit"}, "quantity": 1, "order": 1},
    ],
    46: [
        {"achievement_code": "question-master-divine", "quantity": 1, "order": 1},
    ],
}
