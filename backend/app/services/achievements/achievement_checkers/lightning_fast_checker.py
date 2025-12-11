"""Lightning fast achievement checker.

Awards level-specific speed achievements based on average speed at a specific level.
These are awarded per level with metadata {"level": N}.
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class LightningFastChecker(AchievementChecker):
    """Checker for lightning-fast achievements (level-specific speed)."""
    
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
        """Check and award lightning-fast achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Required session ID to check
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievement_service import AchievementService
        
        new_achievements = []
        
        if not session_id:
            return new_achievements
        
        # Get session
        session = PracticeSession.query.get(session_id)
        if not session or not session.completed_at or not session.level:
            return new_achievements
        
        # Get lightning-fast achievements from config
        lightning_fast_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if code.startswith("lightning-fast-")
        ]
        
        if not lightning_fast_achievements:
            return new_achievements
        
        # Get user's existing achievements
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        # Calculate average speed for this level from user's responses
        # Get all responses for this level
        level_responses = (
            Response.query.filter_by(user_id=user.id, is_correct=True)
            .join(Question)
            .filter(Question.required_level == session.level)
            .all()
        )
        
        if not level_responses:
            return new_achievements
        
        # Calculate average time per question for this level
        total_duration = sum(r.duration_ms or 0 for r in level_responses)
        total_questions = len(level_responses)
        avg_speed_seconds = (total_duration / 1000.0 / total_questions) if total_questions > 0 else None
        
        if not avg_speed_seconds:
            return new_achievements
        
        # Find all qualifying tiers for this level
        qualifying_tiers = []
        for achievement_code, config in lightning_fast_achievements:
            if achievement_code in user_achievement_codes:
                # Check if user already has this achievement for this level
                existing = Achievement.query.filter_by(
                    user_id=user.id,
                    code=achievement_code
                ).first()
                
                if existing:
                    # Check metadata to see if it's for this level
                    if existing.achievement_metadata:
                        try:
                            metadata = json.loads(existing.achievement_metadata)
                            if metadata.get("level") == session.level:
                                continue  # Already have this tier for this level
                        except (json.JSONDecodeError, KeyError):
                            pass
            
            requirements = config.get("requirements", {})
            max_speed = requirements.get("max_speed_seconds", 999)
            min_questions = requirements.get("min_questions", 50)
            
            if avg_speed_seconds <= max_speed and total_questions >= min_questions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if qualifying_tiers:
            # Sort by tier value (highest first) and award the highest tier
            qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = qualifying_tiers[0]
            
            # Check for Champion tier if this is Divine
            # Note: Champion eligibility requires session context, so skip for now
            if highest_tier == "divine":
                champion_code = "lightning-fast-champion"
                champion_config = self.achievement_configs.get(champion_code)
                if champion_config:
                    champion_req = champion_config.get("requirements", {})
                    if avg_speed_seconds <= champion_req.get("max_speed_seconds", 0.5):
                        # Champion tier can be checked during session completion
                        pass
            
            # Create metadata for this level
            metadata = {"level": session.level}
            metadata_json = json.dumps(metadata, sort_keys=True)
            
            achievement = AchievementService.create_achievement(
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


