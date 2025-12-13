"""Checker for achievement_count_by_category achievements."""

from __future__ import annotations

from typing import Any

from ....models import Achievement, User
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from ....utils.tier_utils import ALL_TIERS, extract_base_code_and_tier, get_tier_value
from .base_checker import AchievementChecker


class AchievementCountChecker(AchievementChecker):
    """Checker for achievement_count_by_category achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award achievement_count_by_category achievements.
        
        Args:
            user: User to check achievements for
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of newly created achievements
        """
        achievement_configs = self.achievement_configs
        new_achievements = []
        user_achievement_codes = set(
            Achievement.query.filter_by(user_id=user.id).with_entities(Achievement.code).all()
        )
        user_achievement_codes = {code[0] for code in user_achievement_codes}
        
        for achievement_code, config in achievement_configs.items():
            req_type = config.get("requirements", {}).get("type")
            if req_type != "achievement_count_by_category":
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            new_achievements.extend(
                self._check_achievement_count_by_category(user, achievement_code, config, requirements, session_id)
            )
        
        return new_achievements
    
    def _check_achievement_count_by_category(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check achievement_count_by_category achievements."""
        category = requirements.get("category")
        min_count = requirements.get("min_count", 0)
        min_tier = requirements.get("min_tier")
        
        # Get all user achievements in this category
        user_achievements = Achievement.query.filter_by(
            user_id=user.id,
            category=category,
        ).all()
        
        # Count achievements that meet the minimum tier requirement
        matching_count = 0
        tier_hierarchy = {tier.lower(): get_tier_value(tier) for tier in ALL_TIERS}
        min_tier_value = tier_hierarchy.get(min_tier.lower(), 1) if min_tier else 0
        
        for ach in user_achievements:
            _, ach_tier = extract_base_code_and_tier(ach.code)
            if not min_tier or not ach_tier:
                # If no tier requirement or achievement has no tier, count it
                matching_count += 1
            else:
                ach_tier_value = tier_hierarchy.get(ach_tier.lower(), 1)
                if ach_tier_value >= min_tier_value:
                    matching_count += 1
        
        debug_print(f"[ACHIEVEMENT DEBUG]   achievement_count_by_category: category={category}, min_tier={min_tier}, required={min_count}, actual={matching_count}")
        
        if matching_count >= min_count:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
            return [_create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
            )]
        else:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_count}, have {matching_count})")
            return []

