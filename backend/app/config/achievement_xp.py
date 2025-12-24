"""Achievement XP rewards (bonus XP) and XP multipliers.

Source: `MATH_CONCEPTS.md` → "Achievements & EXP Awards Requirements".

Notes:
- Bonus XP corresponds to the EXP arrays in the doc.
- Multipliers are stored as factors (e.g., 1.03, 1.32) but are treated as bonus deltas
  in calculation. The total multiplier is calculated as: 1.0 + sum(deltas) where
  delta = factor - 1.0. See `MATH_CONCEPTS.md` → "XP Multipliers" for details.
"""

from __future__ import annotations

from app.utils.tier_utils import ALL_TIERS

# Standard tier ordering used throughout the app for 11-tier achievements.
TIERS_11 = list(ALL_TIERS)

# 3-tier ordering for achievements like Accuracy Ace.
TIERS_3 = ["bronze", "silver", "gold"]


ACHIEVEMENT_XP_TABLE: dict[str, dict[str, object]] = {
    # 11-tier achievements
    "level-master": {
        "tiers": TIERS_11,
        "bonus_xp": [200, 320, 512, 819, 1311, 2098, 3357, 5371, 8594, 13750, 22000],
        "multiplier": [1.05, 1.1, 1.19, 1.32, 1.49, 1.7, 1.95, 2.24, 2.57, 2.94, 3.35],
    },
    "lightning-fast": {
        "tiers": TIERS_11,
        "bonus_xp": [200, 340, 578, 983, 1671, 2841, 4830, 8211, 13959, 23730, 40341],
        "multiplier": [1.05, 1.1, 1.19, 1.33, 1.51, 1.73, 1.99, 2.3, 2.65, 3.04, 3.48],
    },
    "question-master": {
        "tiers": TIERS_11,
        "bonus_xp": [120, 204, 347, 590, 1002, 1704, 2897, 4924, 8371, 14231, 24192],
        "multiplier": [1.10, 1.16, 1.26, 1.4, 1.58, 1.8, 2.06, 2.36, 2.7, 3.08, 3.5],
    },
    "speed-demon": {
        "tiers": TIERS_11,
        "bonus_xp": [6, 14, 26, 40, 50, 80, 160, 360, 860, 2060, 4860],
        "multiplier": [1.01, 1.02, 1.047, 1.091, 1.152, 1.23, 1.325, 1.437, 1.566, 1.712, 1.875],
    },
    "perfect-streak": {
        "tiers": TIERS_11,
        "bonus_xp": [50, 90, 162, 292, 526, 947, 1705, 3069, 5524, 9943, 17897],
        "multiplier": [1.05, 1.09, 1.19, 1.35, 1.57, 1.85, 2.19, 2.59, 3.05, 3.57, 4.15],
    },
    "week-warrior": {
        "tiers": TIERS_11,
        "bonus_xp": [500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 256000, 512000],
        "multiplier": [1.2, 1.4, 1.75, 2.25, 2.9, 3.7, 4.65, 5.75, 7.0, 8.4, 9.95],
    },
    "so-wow": {
        "tiers": TIERS_11,
        "bonus_xp": [12, 28, 52, 78, 100, 180, 420, 980, 2300, 5400, 12500],
        "multiplier": None,
    },
    # 3-tier achievements
    "accuracy-ace": {
        "tiers": TIERS_3,
        "bonus_xp": [10, 25, 50],
        "multiplier": [1.01, 1.02, 1.03],
    },
    # 1-tier (unique) achievements
    "first-steps": {
        "tiers": ["bronze"],
        "bonus_xp": [50],
        "multiplier": [1.01],
    },
    "first-victory": {
        "tiers": ["silver"],
        "bonus_xp": [100],
        "multiplier": [1.02],
    },
    # Present in doc but currently used as legacy/rare; no multipliers.
    "level-grandmaster": {
        "tiers": TIERS_11,
        "bonus_xp": [2200, 3520, 5632, 9009, 14421, 23078, 36927, 59081, 94534, 151250, 242000],
        "multiplier": None,
    },
    "human-calculator": {
        "tiers": TIERS_11,
        "bonus_xp": [2200, 3740, 6358, 10813, 18381, 31251, 53130, 90321, 153549, 261030, 443751],
        "multiplier": None,
    },
    "master-of-times-tables": {
        "tiers": TIERS_11,
        "bonus_xp": [4800, 7920, 13080, 21624, 35784, 59268, 98244, 162984, 270636, 449760, 748092],
        "multiplier": None,
    },
    "master-of-division-tables": {
        "tiers": TIERS_11,
        "bonus_xp": [5200, 8580, 14170, 23426, 38766, 64207, 106431, 176566, 293189, 487240, 810433],
        "multiplier": None,
    },
    "master-of-basic-addition": {
        "tiers": TIERS_11,
        "bonus_xp": [4000, 6600, 10900, 18020, 29820, 49390, 81870, 135820, 225530, 374800, 623410],
        "multiplier": None,
    },
    "master-of-basic-subtraction": {
        "tiers": TIERS_11,
        "bonus_xp": [4400, 7260, 11990, 19822, 32802, 54329, 90057, 149402, 248083, 412280, 685751],
        "multiplier": None,
    },
}

