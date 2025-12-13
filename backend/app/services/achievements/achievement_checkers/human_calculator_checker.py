"""Human Calculator achievement checker.

Checks if user has achieved Lightning Fast (Bronze or Silver) at ALL levels.
Similar to Level Grandmaster, but for speed achievements.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, Question, User, db
from ....services.achievement_service import AchievementService
from ....config.levels_config import LEVELS_CONFIG
from .base_checker import AchievementChecker


class HumanCalculatorChecker(AchievementChecker):
    """Checker for Human Calculator achievement."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
    
    def check(self, user: User, tier: str = "bronze") -> list[Achievement]:
        """Check and award Human Calculator milestone achievement.
        
        Requires having Lightning Fast (Bronze or Silver) achievement at ALL levels.
        
        Args:
            user: The user to check
            tier: The tier to check for ("bronze" or "silver")
        
        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs
        
        # Get all levels from config (1-45)
        all_levels = sorted(LEVELS_CONFIG.keys())
        
        if not all_levels:
            return new_achievements
        
        milestone_code = f"human-calculator-{tier}" if tier != "bronze" else "human-calculator"
        
        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements
        
        # Check if user has Lightning Fast (Bronze or Silver) at ALL levels
        all_levels_qualified = True
        required_achievement_code = f"lightning-fast-{tier}"
        
        for target_level in all_levels:
            # Check if user has lightning-fast achievement for this level
            # Lightning-fast achievements are stored with metadata {"level": N}
            level_achievements = Achievement.query.filter_by(
                user_id=user.id,
                code=required_achievement_code
            ).all()
            
            level_qualified = False
            for achievement in level_achievements:
                if achievement.achievement_metadata:
                    try:
                        metadata = json.loads(achievement.achievement_metadata)
                        if metadata.get("level") == target_level:
                            level_qualified = True
                            break
                    except (json.JSONDecodeError, KeyError):
                        pass
            
            # If bronze tier, also check if user has silver (higher tier qualifies)
            if not level_qualified and tier == "bronze":
                silver_achievements = Achievement.query.filter_by(
                    user_id=user.id,
                    code="lightning-fast-silver"
                ).all()
                for achievement in silver_achievements:
                    if achievement.achievement_metadata:
                        try:
                            metadata = json.loads(achievement.achievement_metadata)
                            if metadata.get("level") == target_level:
                                level_qualified = True
                                break
                        except (json.JSONDecodeError, KeyError):
                            pass
            
            if not level_qualified:
                all_levels_qualified = False
                break
        
        if all_levels_qualified:
            config = achievement_configs.get(milestone_code) or achievement_configs.get("human-calculator")
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
            db.session.commit()
        
        return new_achievements





