"""Level master achievement checker.

Awards achievements for consecutive correct answers at any level.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, Question, Response, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class LevelMasterChecker(AchievementChecker):
    """Checker for level master achievements (consecutive correct at any level)."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award level master achievements.
        
        This checks consecutive correct answers at each level separately, ignoring incorrect
        answers at other levels. The achievement is awarded based on the maximum consecutive
        correct achieved at any level.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievement_service import AchievementService
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
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
        
        # Track maximum consecutive correct at any level
        max_consecutive_any_level = 0
        
        # Check each level
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
                continue
            
            # Calculate maximum consecutive correct count for this level
            max_consecutive = 0
            current_consecutive = 0
            
            for response in level_responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            # Track maximum across all levels
            max_consecutive_any_level = max(max_consecutive_any_level, max_consecutive)
        
        # Check Level Master achievements (single achievement with tiers)
        level_master_achievements = []
        for achievement_code, config in self.achievement_configs.items():
            if achievement_code.startswith("level-master-") and not achievement_code.startswith("level-master-milestone-"):
                if achievement_code not in user_achievement_codes:
                    level_master_achievements.append((achievement_code, config))
        
        if level_master_achievements:
            # Find highest qualifying tier
            qualifying_tiers = []
            for achievement_code, config in level_master_achievements:
                requirements = config.get("requirements", {})
                min_consecutive = requirements.get("min_consecutive", 30)
                if max_consecutive_any_level >= min_consecutive:
                    tier = config.get("tier", "bronze")
                    qualifying_tiers.append((tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first) and award the highest tier
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                # Note: Champion eligibility requires session context, so skip for now
                if highest_tier == "divine":
                    champion_code = "level-master-champion"
                    champion_config = self.achievement_configs.get(champion_code)
                    if champion_config and champion_code not in user_achievement_codes:
                        # Champion tier can be checked during session completion
                        pass
                
                achievement = AchievementService.create_achievement(
                    user_id=user.id,
                    code=achievement_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                    session_id=session_id,
                )
                new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements


