"""Unlock requirements for descriptive concept IDs.

Legacy concepts `c_concept_###` currently use level progression configs as their unlock source.
Descriptive concepts (e.g. `c_add_1s`) are unlocked via this mapping.
"""

from __future__ import annotations

from typing import Any


ConceptRequirement = dict[str, Any]


CONCEPT_UNLOCK_REQUIREMENTS: dict[str, list[ConceptRequirement]] = {
    # Legacy concept overrides (from MATH_CONCEPTS.md)
    # Basic Single Digit Addition (c_concept_001) should not be the starter concept in the new system.
    "c_concept_001": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_9s"}, "order": 1},
        {"achievement_code": "master-of-basic-addition-bronze", "quantity": 1, "order": 2},
    ],

    # Single Digit Addition (1s): starter concept
    "c_add_1s": [],
    "c_add_2s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 1, "order": 2},
    ],
    "c_add_3s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 1},
    ],
    "c_add_4s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_3s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_5s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_4s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 2, "order": 2},
    ],
    "c_add_6s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_5s"}, "order": 1},
        {"achievement_code": "level-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_7s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_6s"}, "order": 1},
        {"achievement_code": "perfect-streak-bronze", "quantity": 1, "order": 2},
    ],
    "c_add_8s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_7s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 2},
    ],
    "c_add_9s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_8s"}, "order": 1},
        {"achievement_code": "level-master-gold", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
    ],
    "c_add_0s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_002"}, "order": 1},
        {"achievement_code": "speed-demon-silver", "quantity": 1, "order": 2},
    ],
    "c_add_10s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_0s"}, "order": 1},
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_1s"}, "order": 2},
        {"achievement_code": "accuracy-ace-bronze", "quantity": 20, "order": 3},
    ],

    # Subtraction fixed subtrahends
    "c_sub_0s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_004"}, "order": 1},
        {"achievement_code": "speed-demon-silver", "quantity": 2, "order": 2},
    ],
    "c_sub_1s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 1},
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_0s"}, "order": 2},
    ],
    "c_sub_2s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 1},
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_add_2s"}, "order": 2},
    ],
    "c_sub_3s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_2s"}, "order": 1},
    ],
    "c_sub_4s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_3s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_5s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_4s"}, "order": 1},
        {"achievement_code": "speed-demon-bronze", "quantity": 4, "order": 2},
    ],
    "c_sub_6s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_5s"}, "order": 1},
        {"achievement_code": "level-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_7s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_6s"}, "order": 1},
        {"achievement_code": "perfect-streak-bronze", "quantity": 2, "order": 2},
    ],
    "c_sub_8s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_7s"}, "order": 1},
        {"achievement_code": "lightning-fast-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_2s"}, "order": 2},
    ],
    "c_sub_9s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_8s"}, "order": 1},
        {"achievement_code": "level-master-gold", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_1s"}, "order": 2},
    ],
    "c_sub_10s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_sub_9s"}, "order": 1},
        {"achievement_code": "level-master-silver", "quantity": 1, "metadata_filter": {"concept_id": "c_add_10s"}, "order": 2},
    ],

    # Multiplication by 2/3
    "c_mul_2s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_concept_011"}, "order": 1},
        {"achievement_code": "speed-demon-gold", "quantity": 2, "order": 2},
    ],
    "c_mul_3s": [
        {"achievement_code": "level-master-bronze", "quantity": 1, "metadata_filter": {"concept_id": "c_mul_2s"}, "order": 1},
        {"achievement_code": "speed-demon-platinum", "quantity": 1, "order": 2},
    ],
}





