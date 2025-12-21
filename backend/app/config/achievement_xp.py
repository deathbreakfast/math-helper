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
        "bonus_xp": [832, 1850, 4040, 8229, 16380, 31583, 59940, 111888, 206804, 377400, 821400],
        "multiplier": [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5],
    },
    "lightning-fast": {
        "tiers": TIERS_11,
        "bonus_xp": [357, 810, 2065, 4794, 10753, 23258, 48890, 100291, 204274, 407202, 1000000],
        "multiplier": [1.4, 1.8, 2.3, 2.9, 3.6, 4.4, 5.3, 6.3, 7.4, 8.6, 9.9],
    },
    "question-master": {
        "tiers": TIERS_11,
        "bonus_xp": [160, 800, 1600, 4000, 8000, 16000, 40000, 80000, 160000, 400000, 800000],
        "multiplier": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    },
    "speed-demon": {
        "tiers": TIERS_11,
        "bonus_xp": [6, 14, 26, 40, 50, 80, 160, 360, 860, 2060, 4860],
        "multiplier": [1.01, 1.02, 1.04, 1.08, 1.16, 1.32, 1.64, 2.28, 3.56, 6.12, 11.24],
    },
    "perfect-streak": {
        "tiers": TIERS_11,
        "bonus_xp": [1554, 3330, 7148, 14915, 31036, 63166, 127073, 251748, 493661, 954600, 1098900],
        "multiplier": [1.4, 1.8, 2.3, 2.9, 3.6, 4.4, 5.3, 6.3, 7.4, 8.6, 9.9],
    },
    "week-warrior": {
        "tiers": TIERS_11,
        "bonus_xp": [466, 1269, 3082, 8159, 20202, 37296, 93240, 236338, 586117, 1063519, 1205321],
        "multiplier": [1.2, 1.4, 1.7, 2.1, 2.6, 3.2, 4.0, 5.0, 6.2, 7.5, 8.5],
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
        "bonus_xp": [15540, 25900, 43512, 72002, 120694, 200984, 335664, 559440, 933954, 1554000, 1554000],
        "multiplier": None,
    },
    "human-calculator": {
        "tiers": TIERS_11,
        "bonus_xp": [4641, 10530, 26845, 62322, 139789, 302354, 635570, 1303783, 2655562, 5293626, 13000000],
        "multiplier": None,
    },
    "master-of-times-tables": {
        "tiers": TIERS_11,
        "bonus_xp": [12210, 22040, 42567, 81266, 157593, 304519, 587597, 1127241, 2171657, 4142814, 8805170],
        "multiplier": None,
    },
    "master-of-division-tables": {
        "tiers": TIERS_11,
        "bonus_xp": [13431, 24244, 46823, 89393, 173352, 334971, 646356, 1239965, 2388823, 4557095, 9685687],
        "multiplier": None,
    },
    "master-of-basic-addition": {
        "tiers": TIERS_11,
        "bonus_xp": [10091, 18215, 35179, 67162, 130242, 251669, 485617, 931612, 1794758, 3423813, 7277000],
        "multiplier": None,
    },
    "master-of-basic-subtraction": {
        "tiers": TIERS_11,
        "bonus_xp": [11100, 20037, 38697, 73878, 143266, 276836, 534179, 1024773, 1974234, 3766194, 8004700],
        "multiplier": None,
    },
}

