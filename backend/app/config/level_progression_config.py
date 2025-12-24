"""Level progression requirements: which achievements unlock which levels."""

from typing import Any

# Level progression requirements: which achievements unlock which levels
# Updated to use existing achievements (level-master, lightning-fast) with metadata instead of test achievements
# Test achievements have been removed - use existing achievements with concept-specific metadata
# Note: Higher tier achievements can substitute for lower tier requirements (4 bronze = 2 silver = 1 gold)
# 
# All requirements use concept_id in metadata_filter (e.g., {"concept_id": "c_concept_001"}).
# Legacy test_type and level filters have been migrated to concept_id format.
LEVEL_PROGRESSION_CONFIG: dict[int, list[dict[str, Any]]] = {
    2: [
        {"achievement_code": "first-steps", "quantity": 1, "order": 1},
        {"achievement_code": "first-victory", "quantity": 1, "order": 2},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_001"}, "quantity": 1, "order": 3},
    ],
    3: [
        {"achievement_code": "question-master-bronze", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_001"}, "quantity": 1, "order": 2},
    ],
    4: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_003"}, "quantity": 1, "order": 1},
    ],
    5: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_003"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-silver", "quantity": 1, "order": 2},
    ],
    6: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_002"}, "quantity": 1, "order": 1},
    ],
    7: [
        {"achievement_code": "question-master-gold", "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-silver", "quantity": 5, "order": 2},
        {"achievement_code": "perfect-streak-silver", "quantity": 5, "order": 3},
        {"achievement_code": "level-master-bronze", "metadata_filter": {"concept_id": "c_concept_005"}, "quantity": 2, "order": 4},
    ],
    8: [
        {"achievement_code": "speed-demon-gold", "quantity": 2, "order": 1},
        {"achievement_code": "perfect-streak-gold", "quantity": 2, "order": 2},
        {"achievement_code": "level-master-bronze", "metadata_filter": {"concept_id": "c_concept_006"}, "quantity": 2, "order": 3},
    ],
    9: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_002"}, "quantity": 1, "order": 1},
    ],
    10: [
        {"achievement_code": "speed-demon-gold", "quantity": 10, "order": 1},
        {"achievement_code": "perfect-streak-gold", "quantity": 10, "order": 2},
        {"achievement_code": "level-master-silver", "metadata_filter": {"concept_id": "c_concept_008"}, "quantity": 1, "order": 3},
        {"achievement_code": "question-master-platinum", "quantity": 1, "order": 4},
    ],
    11: [
        {"achievement_code": "so-wow-platinum", "quantity": 1, "order": 1},
        {"achievement_code": "question-master-gold", "quantity": 1, "order": 2},
        {"achievement_code": "level-master-silver", "metadata_filter": {"concept_id": "c_concept_009"}, "quantity": 1, "order": 3},
        {"achievement_code": "level-master-silver", "metadata_filter": {"concept_id": "c_concept_008"}, "quantity": 2, "order": 4},
    ],
    12: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_004"}, "quantity": 1, "order": 1},
    ],
    13: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_009"}, "quantity": 1, "order": 1},
    ],
    14: [
        {"achievement_code": "question-master-diamond", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_010"}, "quantity": 1, "order": 2},
    ],
    15: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_011"}, "quantity": 1, "order": 1},
    ],
    16: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_012"}, "quantity": 1, "order": 1},
    ],
    17: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_013"}, "quantity": 1, "order": 1},
    ],
    18: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_014"}, "quantity": 1, "order": 1},
    ],
    19: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_015"}, "quantity": 1, "order": 1},
    ],
    20: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_016"}, "quantity": 1, "order": 1},
    ],
    21: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_018"}, "quantity": 1, "order": 1},
    ],
    22: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_019"}, "quantity": 1, "order": 1},
    ],
    23: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_020"}, "quantity": 1, "order": 1},
    ],
    24: [
        {"achievement_code": "question-master-master", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_021"}, "quantity": 1, "order": 2},
    ],
    25: [
        {"achievement_code": "so-wow-diamond", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_008"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-diamond", "metadata_filter": {"concept_id": "c_concept_001"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-bronze", "metadata_filter": {"concept_id": "c_concept_002"}, "quantity": 1, "order": 4},
    ],
    26: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_023"}, "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-diamond", "metadata_filter": {"concept_id": "c_concept_003"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-bronze", "metadata_filter": {"concept_id": "c_concept_004"}, "quantity": 1, "order": 3},
    ],
    27: [
        {"achievement_code": "question-master-grandmaster", "quantity": 1, "order": 1},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_018"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_007"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_009"}, "quantity": 1, "order": 4},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_010"}, "quantity": 1, "order": 5},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_011"}, "quantity": 1, "order": 6},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_012"}, "quantity": 1, "order": 7},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_013"}, "quantity": 1, "order": 8},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_014"}, "quantity": 1, "order": 9},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_015"}, "quantity": 1, "order": 10},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_016"}, "quantity": 1, "order": 11},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_019"}, "quantity": 1, "order": 12},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_020"}, "quantity": 1, "order": 13},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_021"}, "quantity": 1, "order": 14},
    ],
    28: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_024"}, "quantity": 1, "order": 1},
    ],
    29: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_025"}, "quantity": 1, "order": 1},
    ],
    30: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_026"}, "quantity": 1, "order": 1},
    ],
    31: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_027"}, "quantity": 1, "order": 1},
    ],
    32: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_028"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-legendary", "quantity": 1, "order": 2},
    ],
    33: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_029"}, "quantity": 1, "order": 1},
    ],
    34: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_030"}, "quantity": 1, "order": 1},
    ],
    35: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_031"}, "quantity": 1, "order": 1},
    ],
    36: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_032"}, "quantity": 1, "order": 1},
    ],
    37: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_034"}, "quantity": 1, "order": 1},
    ],
    38: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_034"}, "quantity": 1, "order": 1},
    ],
    39: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_035"}, "quantity": 1, "order": 1},
    ],
    40: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_036"}, "quantity": 1, "order": 1},
    ],
    41: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_037"}, "quantity": 1, "order": 1},
        {"achievement_code": "question-master-mythic", "quantity": 1, "order": 2},
    ],
    42: [
        {"achievement_code": "so-wow-master", "quantity": 1, "order": 1},
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_038"}, "quantity": 1, "order": 2},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_034"}, "quantity": 1, "order": 3},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_025"}, "quantity": 1, "order": 4},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_026"}, "quantity": 1, "order": 5},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_027"}, "quantity": 1, "order": 6},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_028"}, "quantity": 1, "order": 7},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_029"}, "quantity": 1, "order": 8},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_030"}, "quantity": 1, "order": 9},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_031"}, "quantity": 1, "order": 10},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_032"}, "quantity": 1, "order": 11},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_033"}, "quantity": 1, "order": 12},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_035"}, "quantity": 1, "order": 13},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_036"}, "quantity": 1, "order": 14},
        {"achievement_code": "speed-demon-gold", "metadata_filter": {"concept_id": "c_concept_037"}, "quantity": 1, "order": 15},
    ],
    43: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_039"}, "quantity": 1, "order": 1},
    ],
    44: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_040"}, "quantity": 1, "order": 1},
        {"achievement_code": "so-wow-grandmaster", "quantity": 1, "order": 2},
    ],
    45: [
        {"achievement_code": "accuracy-ace-gold", "metadata_filter": {"concept_id": "c_concept_025"}, "quantity": 1, "order": 1},
    ],
    46: [
        {"achievement_code": "question-master-divine", "quantity": 1, "order": 1},
    ],
}
