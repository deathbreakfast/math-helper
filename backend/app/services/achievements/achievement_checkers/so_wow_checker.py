"""So, Wow! achievement checker.

Awards "So, Wow! (Tier)" achievements when a user earns their first achievement of a tier.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement
from .base_checker import AchievementChecker


class SoWowChecker(AchievementChecker):
    """Checker for So, Wow! achievements (first achievement of a tier)."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
    
    def check(
        self,
        user,
        newly_awarded_achievements: list[Achievement],
        session_id: int | None = None,
    ) -> list[Achievement]:
        """Check and award So, Wow! achievements when user earns their first achievement of a tier.
        
        Args:
            user: The user to check
            newly_awarded_achievements: List of achievements just awarded in this session
            session_id: Optional session ID to link achievements
            
        Returns:
            List of newly created So, Wow! achievements
        """
        from ....config.achievements import MILESTONE_ACHIEVEMENTS
        from ....utils.tier_utils import extract_base_code_and_tier
        from ....services.achievement_service import AchievementService
        from .... import db
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs or MILESTONE_ACHIEVEMENTS
        
        # Track which tiers we've already checked (to avoid duplicates)
        tiers_checked = set()
        
        # Get all existing achievements to check tiers (EXCLUDE newly awarded ones)
        newly_awarded_codes = {ach.code for ach in newly_awarded_achievements}
        all_user_achievements = Achievement.query.filter_by(user_id=user.id).all()
        
        # Build a set of tiers the user already has achievements for (BEFORE new ones)
        existing_tiers = set()
        for ach in all_user_achievements:
            # Skip newly awarded achievements when checking existing tiers
            if ach.code in newly_awarded_codes:
                continue
            _, tier = extract_base_code_and_tier(ach.code)
            if tier:
                existing_tiers.add(tier.lower())
        
        # Check each newly awarded achievement
        for new_ach in newly_awarded_achievements:
            _, tier = extract_base_code_and_tier(new_ach.code)
            if not tier:
                continue  # Skip non-tiered achievements
            
            tier_lower = tier.lower()
            
            # Skip if we've already checked this tier
            if tier_lower in tiers_checked:
                continue
            
            # Skip if user already has achievements of this tier (before this session)
            if tier_lower in existing_tiers:
                continue
            
            # This is the first achievement of this tier! Award "So, Wow! (Tier)"
            so_wow_code = f"so-wow-{tier_lower}"
            
            # Skip if already earned
            if so_wow_code in user_achievement_codes:
                tiers_checked.add(tier_lower)
                continue
            
            config = achievement_configs.get(so_wow_code)
            if not config:
                continue
            
            achievement = AchievementService.create_achievement(
                user_id=user.id,
                code=so_wow_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
            )
            new_achievements.append(achievement)
            tiers_checked.add(tier_lower)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

