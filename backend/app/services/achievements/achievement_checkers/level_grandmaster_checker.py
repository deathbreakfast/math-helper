"""Level Grandmaster achievement checker.

Checks if user has achieved 30 consecutive correct at ALL levels.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, Question, Response, User
from ....services.achievement_service import AchievementService
from .... import db
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
        
        Requires having Level Master (Bronze) achievement and having achieved
        30 consecutive correct at ALL levels in the system.
        
        Args:
            user: The user to check
        
        Returns:
            List of newly created achievements
        """
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = self.achievement_configs
        
        # Check if user has Level Master (Bronze) achievement
        if "level-master-bronze" not in user_achievement_codes:
            return new_achievements
        
        # Get all distinct levels from questions
        all_levels = [
            row[0] for row in
            db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]
        
        if not all_levels:
            return new_achievements
        
        milestone_code = "level-grandmaster"
        
        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements
        
        # Check if user has achieved 30 consecutive correct at ALL levels
        all_levels_qualified = True
        for target_level in all_levels:
            # Get all responses for this level, ordered chronologically
            level_responses = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(Question.required_level == target_level)
                .order_by(Response.answered_at.asc())
                .all()
            )
            
            if not level_responses:
                all_levels_qualified = False
                break
            
            # Calculate maximum consecutive correct count for this level
            max_consecutive = 0
            current_consecutive = 0
            
            for response in level_responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            # Check if this level has achieved bronze threshold (30 consecutive)
            if max_consecutive < 30:
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
            db.session.commit()
        
        return new_achievements

