"""Concept XP values (XP per correct answer).

For now this includes:
- Legacy `c_concept_###` concepts (1-45)
- A first set of descriptive concept IDs (e.g. `c_add_1s`) defined in `MATH_CONCEPTS.md`
"""

from __future__ import annotations

# XP per correct answer for legacy concepts (levels 1-45 mapped to concept IDs).
CONCEPT_XP_PER_CORRECT: dict[str, int] = {
    "c_concept_001": 97,
    "c_concept_002": 42,
    "c_concept_003": 177,
    "c_concept_004": 117,
    "c_concept_005": 102,
    "c_concept_006": 182,
    "c_concept_007": 107,
    "c_concept_008": 187,
    "c_concept_009": 197,
    "c_concept_010": 202,
    "c_concept_011": 212,
    "c_concept_012": 227,
    "c_concept_013": 222,
    "c_concept_014": 242,
    "c_concept_015": 247,
    "c_concept_016": 252,
    "c_concept_017": 257,
    "c_concept_018": 207,
    "c_concept_019": 217,
    "c_concept_020": 232,
    "c_concept_021": 237,
    "c_concept_022": 112,
    "c_concept_023": 192,
    "c_concept_024": 262,
    "c_concept_025": 267,
    "c_concept_026": 277,
    "c_concept_027": 282,
    "c_concept_028": 297,
    "c_concept_029": 302,
    "c_concept_030": 307,
    "c_concept_031": 312,
    "c_concept_032": 317,
    "c_concept_033": 322,
    "c_concept_034": 327,
    "c_concept_035": 287,
    "c_concept_036": 332,
    "c_concept_037": 337,
    "c_concept_038": 292,
    "c_concept_039": 342,
    "c_concept_040": 347,
    "c_concept_041": 352,
    "c_concept_042": 357,
    "c_concept_043": 272,
    "c_concept_044": 362,
    "c_concept_045": 367,

    # Descriptive concept IDs (starting with addition fixed addends)
    "c_add_0s": 47,
    "c_add_1s": 37,
    "c_add_2s": 57,
    "c_add_3s": 62,
    "c_add_4s": 67,
    "c_add_5s": 72,
    "c_add_6s": 77,
    "c_add_7s": 82,
    "c_add_8s": 87,
    "c_add_9s": 92,
    "c_add_10s": 52,
}

