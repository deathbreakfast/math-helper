"""Accuracy ace achievement checker.

Awards session-based accuracy achievements for high accuracy in a session.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class AccuracyAceChecker(AchievementChecker):
    """Checker for accuracy-ace achievements (session-based accuracy)."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
    
    def check(
        self,
        session: PracticeSession,
        user: User | None = None,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award accuracy-ace achievements.
        
        Args:
            session: PracticeSession to check (required)
            user: Optional user object (will be fetched from session if not provided)
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID (not used if session provided)
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievement_service import AchievementService
        
        new_achievements = []
        
        if not session or not session.completed_at or session.is_test:
            return new_achievements
        
        # Get user from session if not provided
        if not user:
            user = session.user if hasattr(session, 'user') else None
            if not user:
                # Fetch user from database
                from ....models import User as UserModel
                user = db.session.get(UserModel, session.user_id)
                if not user:
                    return new_achievements
        
        # Get accuracy-ace achievements from config
        accuracy_ace_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if code.startswith("accuracy-ace-")
        ]
        
        if not accuracy_ace_achievements:
            return new_achievements
        
        # Get user's existing achievements
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        # Get session metrics
        total_questions = session.total_questions
        if total_questions < 10:  # Minimum questions requirement
            return new_achievements
        
        # Accuracy is stored as percentage (0-100)
        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0  # Convert to 0-1 range
        
        # Find all qualifying tiers
        qualifying_tiers = []
        for achievement_code, config in accuracy_ace_achievements:
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            min_accuracy = requirements.get("min_accuracy", 0.80)
            min_questions = requirements.get("min_questions", 10)
            
            if accuracy >= min_accuracy and total_questions >= min_questions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if qualifying_tiers:
            # Sort by tier value (highest first) and award the highest tier
            qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = qualifying_tiers[0]
            
            # Check for Champion tier if this is Divine
            # Note: Champion eligibility requires session context, so skip for now
            if highest_tier == "divine":
                champion_code = "accuracy-ace-champion"
                champion_config = self.achievement_configs.get(champion_code)
                if champion_config:
                    champion_req = champion_config.get("requirements", {})
                    if accuracy >= champion_req.get("min_accuracy", 1.0):
                        # Champion tier can be checked during session completion
                        pass
            
            achievement = AchievementService.create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session.id,
            )
            new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements


