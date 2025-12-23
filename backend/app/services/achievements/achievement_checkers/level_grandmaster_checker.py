"""Level Grandmaster achievement checker.

Checks if user has Level Master (Bronze or higher) achievement at ALL levels.
Similar to Human Calculator, but for accuracy achievements.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, User, db
from ....services.achievement_service import AchievementService
from ....config.levels_config import LEVELS_CONFIG
from .base_checker import AchievementChecker


class LevelGrandmasterChecker(AchievementChecker):
    """Checker for Level Grandmaster achievement."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
    
    def check(self, user: User) -> list[Achievement]:
        """Check and award Level Grandmaster milestone achievement.
        
        Requires having Level Master (Bronze or higher) achievement at ALL levels.
        Checks for existing Level Master achievements with metadata, not recalculating counts.
        
        Args:
            user: The user to check
        
        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs
        
        milestone_code = "level-grandmaster"
        
        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements
        
        # Get all levels from config (1-45)
        all_levels = sorted(LEVELS_CONFIG.keys())
        
        if not all_levels:
            return new_achievements
        
        # Check if user has Level Master (Bronze or higher) at ALL levels
        all_levels_qualified = True
        required_achievement_code = "level-master-bronze"
        
        for target_level in all_levels:
            # Check if user has level-master-bronze achievement for this level
            # Level-master achievements are stored with metadata {"level": N}
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
            
            # If bronze not found, check for silver (higher tier qualifies)
            if not level_qualified:
                silver_achievements = Achievement.query.filter_by(
                    user_id=user.id,
                    code="level-master-silver"
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
            
            # If still not found, check for gold (higher tier qualifies)
            if not level_qualified:
                gold_achievements = Achievement.query.filter_by(
                    user_id=user.id,
                    code="level-master-gold"
                ).all()
                for achievement in gold_achievements:
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

