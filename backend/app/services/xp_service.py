"""XP and level calculation helpers (Diablo 2 curve)."""

from __future__ import annotations

from bisect import bisect_right

from ..config.xp_table import MAX_LEVEL, XP_TOTAL_FOR_LEVEL

_LEVELS_ASC = sorted(XP_TOTAL_FOR_LEVEL.keys())
_TOTALS_ASC = [XP_TOTAL_FOR_LEVEL[lvl] for lvl in _LEVELS_ASC]


class XPService:
    @staticmethod
    def total_xp_for_level(level: int) -> int:
        if level < 1:
            return 0
        if level > MAX_LEVEL:
            level = MAX_LEVEL
        return XP_TOTAL_FOR_LEVEL[level]

    @staticmethod
    def level_for_total_xp(total_xp: int) -> int:
        """Return the level for a given total XP (clamped to [1, MAX_LEVEL])."""
        total_xp = max(0, int(total_xp))
        # Find insertion point to the right, then step back one to get the largest <= total_xp
        idx = bisect_right(_TOTALS_ASC, total_xp) - 1
        if idx < 0:
            return 1
        level = _LEVELS_ASC[idx]
        return min(MAX_LEVEL, max(1, level))

    @staticmethod
    def progress_for_total_xp(total_xp: int) -> dict[str, int | None]:
        """Return XP progress info for UI."""
        level = XPService.level_for_total_xp(total_xp)
        current_total = XPService.total_xp_for_level(level)
        next_total = XPService.total_xp_for_level(level + 1) if level < MAX_LEVEL else None

        xp_into_level = int(total_xp) - current_total
        xp_to_next = (next_total - int(total_xp)) if next_total is not None else None

        return {
            "level": level,
            "total_xp": int(total_xp),
            "current_level_total_xp": current_total,
            "next_level_total_xp": next_total,
            "xp_into_level": max(0, xp_into_level),
            "xp_to_next_level": max(0, xp_to_next) if xp_to_next is not None else None,
        }

