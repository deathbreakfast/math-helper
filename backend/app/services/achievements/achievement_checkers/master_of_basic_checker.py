"""Master of Basic Addition/Subtraction achievement checker.

Awards milestone achievements when a user has Level Master at all basic concept buckets.

- Basic addition concepts: c_add_0s..c_add_10s
- Basic subtraction concepts: c_sub_0s..c_sub_10s

This is concept-based (metadata {"concept_id": ...}) and relies on LevelMasterChecker having
already awarded the underlying level-master-* achievements for each concept bucket.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, User, db
from ....services.achievement_service import AchievementService
from ....utils.tier_utils import ALL_TIERS, get_tier_value
from .base_checker import AchievementChecker


class MasterOfBasicChecker(AchievementChecker):
    """Checker for Master of Basic Addition/Subtraction tiered achievements."""

    BASIC_ADDITION_CONCEPT_IDS = [f"c_add_{n}s" for n in range(0, 11)]
    BASIC_SUBTRACTION_CONCEPT_IDS = [f"c_sub_{n}s" for n in range(0, 11)]

    def __init__(self, achievement_configs: dict[str, Any]):
        self.achievement_configs = achievement_configs

    def check(self, user: User) -> list[Achievement]:
        """Check and award Master of Basic Addition/Subtraction achievements.

        Awards at most 1 tier per family (highest achieved), relying on tier substitution elsewhere.
        """
        new_achievements: list[Achievement] = []

        # Preload user's level-master achievements once.
        level_master_achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .filter(Achievement.code.like("level-master-%"))
            .all()
        )

        concept_best_tier_value: dict[str, int] = {}
        for ach in level_master_achievements:
            if not ach.achievement_metadata:
                continue
            try:
                md = json.loads(ach.achievement_metadata)
            except json.JSONDecodeError:
                continue

            cid = md.get("concept_id")
            if not cid:
                continue

            # code looks like "level-master-{tier}"
            parts = ach.code.split("-")
            if len(parts) < 3:
                continue
            tier = parts[2]
            tier_value = get_tier_value(tier)
            concept_best_tier_value[cid] = max(concept_best_tier_value.get(cid, -1), tier_value)

        new_achievements += self._check_family(
            user=user,
            family_base="master-of-basic-addition",
            required_concepts=self.BASIC_ADDITION_CONCEPT_IDS,
            concept_best_tier_value=concept_best_tier_value,
        )
        new_achievements += self._check_family(
            user=user,
            family_base="master-of-basic-subtraction",
            required_concepts=self.BASIC_SUBTRACTION_CONCEPT_IDS,
            concept_best_tier_value=concept_best_tier_value,
        )

        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()

        return new_achievements

    def _check_family(
        self,
        user: User,
        family_base: str,
        required_concepts: list[str],
        concept_best_tier_value: dict[str, int],
    ) -> list[Achievement]:
        """Check a single family and award the highest tier achieved."""
        # Determine the highest tier in ALL_TIERS that the user qualifies for.
        best_award: tuple[int, str, str, dict[str, Any]] | None = None  # (tier_value, tier, code, config)

        for tier in ALL_TIERS:
            code = f"{family_base}-{tier}"
            config = self.achievement_configs.get(code)
            if not config:
                continue

            requirements = config.get("requirements", {}) or {}
            required_tier = str(requirements.get("required_tier", "bronze"))
            required_tier_value = get_tier_value(required_tier)

            # Qualify if every required concept has a level-master tier value >= required tier.
            if all(concept_best_tier_value.get(cid, -1) >= required_tier_value for cid in required_concepts):
                best_award = (get_tier_value(tier), tier, code, config)

        if not best_award:
            return []

        _, _, best_code, best_config = best_award

        # Skip if already earned (no metadata on these).
        user_codes = AchievementService.get_achievement_codes(user.id)
        if best_code in user_codes:
            return []

        ach = AchievementService.create_achievement(
            user_id=user.id,
            code=best_code,
            title=best_config["title"],
            description=best_config["description"],
            icon=best_config["icon"],
            category=best_config["category"],
        )
        return [ach]


