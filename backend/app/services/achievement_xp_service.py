"""Achievement XP reward lookup (bonus XP + additive multipliers)."""

from __future__ import annotations

from dataclasses import dataclass

from ..config.achievement_xp import ACHIEVEMENT_XP_TABLE
from ..utils.tier_utils import extract_base_code_and_tier


@dataclass(frozen=True)
class AchievementXPReward:
    base_code: str
    tier: str | None
    bonus_xp: int
    multiplier: float


class AchievementXPService:
    @staticmethod
    def reward_for_achievement_code(code: str) -> AchievementXPReward:
        """Return XP reward info for an achievement code.

        If the achievement has no configured reward, returns (bonus=0, multiplier=0).
        """
        base, tier = extract_base_code_and_tier(code)

        entry = ACHIEVEMENT_XP_TABLE.get(base)
        if not entry:
            # Some achievements are non-tiered but still appear as full codes (e.g., first-steps).
            entry = ACHIEVEMENT_XP_TABLE.get(code)
            if not entry:
                return AchievementXPReward(base_code=base, tier=tier, bonus_xp=0, multiplier=0.0)
            base = code
            tier = None

        tiers = list(entry.get("tiers") or [])
        bonus_arr = list(entry.get("bonus_xp") or [])
        mult_arr = entry.get("multiplier")
        mult_arr_list = list(mult_arr) if isinstance(mult_arr, list) else None

        idx = 0
        if tier and tiers:
            try:
                idx = tiers.index(tier)
            except ValueError:
                idx = 0
        elif tiers and len(tiers) == 1:
            tier = tiers[0]

        bonus = int(bonus_arr[idx]) if idx < len(bonus_arr) else 0
        multiplier = float(mult_arr_list[idx]) if mult_arr_list and idx < len(mult_arr_list) else 0.0

        return AchievementXPReward(base_code=base, tier=tier, bonus_xp=bonus, multiplier=multiplier)

