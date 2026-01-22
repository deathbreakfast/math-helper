"""Math Grandmaster achievement checker.

Checks if user has Math Master (tier or higher) achievement for ALL concepts.
Similar to Human Calculator, but for accuracy achievements.
"""

from __future__ import annotations

import json
from typing import Any

from ....config.concepts_config import CONCEPTS_CONFIG
from ....models import Achievement, User
from ....services.achievement_service import AchievementService
from ....utils.tier_utils import extract_base_code_and_tier, get_tier_value
from .base_checker import AchievementChecker


class MathGrandmasterChecker(AchievementChecker):
    """Checker for Math Grandmaster achievement."""

    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.

        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs

    def check(self, user: User, tier: str = "bronze") -> list[Achievement]:
        """Check and award Math Grandmaster milestone achievement.

        Requires having Math Master (tier or higher) achievement for ALL concepts.
        Checks existing Math Master achievements with concept_id metadata.

        Args:
            user: The user to check
            tier: Required tier to check for (e.g., "bronze", "silver", etc.)

        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs

        milestone_code = f"math-grandmaster-{tier}"

        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements

        concept_ids = list(CONCEPTS_CONFIG.keys())
        if not concept_ids:
            return new_achievements

        required_tier_value = get_tier_value(tier)

        concept_best_tiers: dict[str, int] = {concept_id: 0 for concept_id in concept_ids}

        math_master_achievements = Achievement.query.filter(
            Achievement.user_id == user.id,
            Achievement.code.like("math-master-%")
        ).all()

        for achievement in math_master_achievements:
            if not achievement.achievement_metadata:
                continue
            try:
                metadata = json.loads(achievement.achievement_metadata)
            except (json.JSONDecodeError, TypeError):
                continue

            concept_id = metadata.get("concept_id")
            if not concept_id:
                continue

            base_code, achievement_tier = extract_base_code_and_tier(achievement.code)
            if base_code != "math-master" or not achievement_tier:
                continue

            tier_value = get_tier_value(achievement_tier)
            if tier_value > concept_best_tiers.get(concept_id, 0):
                concept_best_tiers[concept_id] = tier_value

        for concept_id in concept_ids:
            if concept_best_tiers.get(concept_id, 0) < required_tier_value:
                return new_achievements

        config = achievement_configs.get(milestone_code)
        if config:
            achievement = AchievementService.create_achievement(
                user_id=user.id,
                code=milestone_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
            )
            new_achievements.append(achievement)

        if new_achievements:
            from ....database import flush_or_commit

            flush_or_commit()

        return new_achievements
