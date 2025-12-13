"""Level master achievement checker.

Awards level-specific achievements for consecutive correct answers at each level.
Each level gets its own achievement with metadata {"level": N}.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, Question, Response, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class LevelMasterChecker(AchievementChecker):
    """Checker for level master achievements (consecutive correct per level)."""
    
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
        
        This checks consecutive correct answers at each level separately.
        Awards separate achievements per level with metadata {"level": N}.
        Only awards the highest qualifying tier per level.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievements.achievement_utils import create_achievement
        
        new_achievements = []
        
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
        
        # Get Level Master achievement configs
        level_master_configs = {
            code: config for code, config in self.achievement_configs.items()
            if code.startswith("level-master-") and not code.startswith("level-master-milestone-")
        }
        
        if not level_master_configs:
            return new_achievements
        
        # Check each level independently
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
            
            # Check if user already has an achievement for this level
            metadata = {"level": target_level}
            metadata_json = json.dumps(metadata, sort_keys=True)
            
            existing_achievements = Achievement.query.filter_by(
                user_id=user.id,
                achievement_metadata=metadata_json
            ).filter(
                Achievement.code.like("level-master-%")
            ).all()
            
            # Find highest existing tier for this level
            highest_existing_tier_value = -1
            for existing in existing_achievements:
                # Extract tier from code (e.g., "level-master-silver" -> "silver")
                code_parts = existing.code.split("-")
                if len(code_parts) >= 3 and code_parts[0] == "level" and code_parts[1] == "master":
                    tier = code_parts[2]
                    tier_value = get_tier_value(tier)
                    highest_existing_tier_value = max(highest_existing_tier_value, tier_value)
            
            # Find all qualifying tiers for this level
            qualifying_tiers = []
            for achievement_code, config in level_master_configs.items():
                requirements = config.get("requirements", {})
                min_consecutive = requirements.get("min_consecutive", 30)
                tier = config.get("tier", "bronze")
                tier_value = get_tier_value(tier)
                
                # Only consider tiers higher than existing, or first tier if none exists
                if max_consecutive >= min_consecutive and tier_value > highest_existing_tier_value:
                    qualifying_tiers.append((tier_value, tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first) and award the highest tier
                qualifying_tiers.sort(reverse=True)
                _, tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                # Note: Champion eligibility requires session context, so skip for now
                if tier == "divine":
                    champion_code = "level-master-champion"
                    champion_config = self.achievement_configs.get(champion_code)
                    if champion_config:
                        champion_req = champion_config.get("requirements", {})
                        if max_consecutive >= champion_req.get("min_consecutive", 15360):
                            # Champion tier can be checked during session completion
                            pass
                
                achievement = create_achievement(
                    user_id=user.id,
                    code=achievement_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                    session_id=session_id,
                    metadata=metadata,
                )
                new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements






