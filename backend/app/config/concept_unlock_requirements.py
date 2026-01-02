"""Unlock requirements for concept IDs.

All concepts (both legacy c_concept_### and descriptive c_add_*, c_sub_*, etc.) 
use this mapping for unlock requirements. Concepts without entries are unlocked by default.
"""

from __future__ import annotations

from typing import Any


ConceptRequirement = dict[str, Any]


CONCEPT_UNLOCK_REQUIREMENTS: dict[str, list[ConceptRequirement]] = {
    # Legacy concepts (c_concept_001 through c_concept_045)
    # Only concepts with explicit requirements are listed here.
    # Concepts without entries are unlocked by default (no requirements).
    # Basic Single Digit Addition (c_concept_001) should not be the starter concept in the new system.
    "c_concept_001": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_10s"}, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_0s"}, "order": 2},
        {"achievement_code": "master-of-basic-addition-bronze", "quantity": 1, "order": 3},
    ],
    # Note: c_concept_002 has been removed (merged into c_concept_001)
    # Basic Single Digit Subtraction (c_concept_003)
    "c_concept_003": [
        {"achievement_code": "master-of-basic-subtraction-bronze", "quantity": 1, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_10s"}, "order": 2},
    ],
    # Single and Two Digit Subtraction (c_concept_006)
    "c_concept_006": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_003"}, "order": 1},
    ],
    # Single and Two Digit Addition (c_concept_005)
    "c_concept_005": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_001"}, "order": 1},
    ],
    # Two Digit Addition (c_concept_007)
    "c_concept_007": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_005"}, "order": 1},
    ],
    # Three Digit Addition (c_concept_022)
    "c_concept_022": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_007"}, "order": 1},
    ],
    # Two Digit Subtraction (c_concept_008)
    "c_concept_008": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_006"}, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_010"}, "order": 2},
    ],
    # Negative Number Subtraction (c_concept_010)
    "c_concept_010": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_003"}, "order": 1},
    ],
    # Three Digit Subtraction (c_concept_023)
    "c_concept_023": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_008"}, "order": 1},
    ],
    # Note: c_concept_011 through c_concept_021, c_concept_024 through c_concept_045 are unlocked by default (no requirements listed)
    # Note: c_concept_004 removed (covered by c_sub_0s), c_concept_009 removed

    # Single Digit Addition (1s): starter concept
    "c_add_1s": [],
    "c_add_2s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 1, "order": 2},
    ],
    "c_add_3s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 1},
    ],
    "c_add_4s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_3s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_5s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_4s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 2, "order": 2},
    ],
    "c_add_6s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_5s"}, "order": 1},
        {"achievement_code": "math-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_7s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_6s"}, "order": 1},
        {"achievement_code": "perfect-streak-bronze", "quantity": 1, "order": 2},
    ],
    "c_add_8s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_7s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 2},
    ],
    "c_add_9s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_8s"}, "order": 1},
        {"achievement_code": "math-master-gold", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_0s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_9s"}, "order": 1},
        {"achievement_code": "speed-demon-silver", "quantity": 1, "order": 2},
    ],
    "c_add_10s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_9s"}, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
        {"achievement_code": "accuracy-ace-bronze", "quantity": 20, "order": 3},
    ],

    # Subtraction fixed subtrahends
    "c_sub_0s": [
        {"achievement_code": "math-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_add_0s"}, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_9s"}, "order": 2},
        {"achievement_code": "speed-demon-silver", "quantity": 2, "order": 3},
    ],
    "c_sub_1s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 1},
    ],
    "c_sub_2s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 1},
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 2},
    ],
    "c_sub_3s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_2s"}, "order": 1},
    ],
    "c_sub_4s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_3s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_5s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_4s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 4, "order": 2},
    ],
    "c_sub_6s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_5s"}, "order": 1},
        {"achievement_code": "math-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_7s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_6s"}, "order": 1},
        {"achievement_code": "perfect-streak-bronze", "quantity": 2, "order": 2},
    ],
    "c_sub_8s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_7s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_2s"}, "order": 2},
    ],
    "c_sub_9s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_8s"}, "order": 1},
        {"achievement_code": "math-master-gold", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_10s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_9s"}, "order": 1},
        {"achievement_code": "math-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_add_10s"}, "order": 2},
    ],

    # Multiplication by 2/3
    "c_mul_2s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_011"}, "order": 1},
        {"achievement_code": "speed-demon-gold", "quantity": 2, "order": 2},
    ],
    "c_mul_3s": [
        {"achievement_code": "math-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_mul_2s"}, "order": 1},
        {"achievement_code": "speed-demon-platinum", "quantity": 1, "order": 2},
    ],
}






