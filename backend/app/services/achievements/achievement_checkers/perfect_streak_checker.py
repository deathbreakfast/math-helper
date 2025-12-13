"""Perfect streak achievement checker.

Awards achievements for consecutive perfect sessions (100% accuracy).
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, User, db
from .base_checker import AchievementChecker


class PerfectStreakChecker(AchievementChecker):
    """Checker for perfect streak achievements."""
    
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
        """Check and award perfect streak achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        # Get user's existing achievement codes
        user_achievement_codes = {
            a.code for a in Achievement.query.filter_by(user_id=user.id).all()
        }
        
        # Get perfect_streak achievements from config
        perfect_streak_achievements = [
            (code, config) for code, config in self.achievement_configs.items()
            if code.startswith("perfect-streak-")
        ]
        
        if not perfect_streak_achievements:
            return new_achievements
        
        # Get all completed sessions ordered by completion time (most recent first)
        all_sessions = (
            PracticeSession.query.filter_by(user_id=user.id)
            .filter(PracticeSession.completed_at.isnot(None))
            .order_by(PracticeSession.completed_at.desc())
            .all()
        )
        
        # Count consecutive perfect sessions (100% accuracy)
        # Note: Sessions are ordered by completed_at DESC (most recent first)
        # So we count from the most recent backwards
        consecutive_perfect = 0
        for session in all_sessions:
            # Check if session has exactly 100.0 accuracy (stored as percentage)
            if session.accuracy == 100.0:
                consecutive_perfect += 1
            else:
                break  # Break on first non-perfect session
        
        # Find all qualifying tiers
        # Note: We don't check for existing achievements here - create_achievement() handles constraints
        qualifying_tiers = []
        for achievement_code, config in perfect_streak_achievements:
            requirements = config.get("requirements", {})
            min_sessions = requirements.get("min_sessions", 0)
            if consecutive_perfect >= min_sessions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if qualifying_tiers:
            # Sort by tier value (highest first)
            from ....utils.tier_utils import get_tier_value
            qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = qualifying_tiers[0]
            
            # Check for Champion tier if this is Divine
            # Note: Champion eligibility check is handled at orchestrator level to avoid circular imports
            if highest_tier == "divine":
                champion_code = "perfect-streak-champion"
                champion_config = self.achievement_configs.get(champion_code)
                if champion_config:
                    champion_req = champion_config.get("requirements", {})
                    if consecutive_perfect >= champion_req.get("min_sessions", 0):
                        # Champion eligibility will be checked by orchestrator
                        # For now, award divine tier
                        pass
            
            achievement = self._create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
            )
            new_achievements.append(achievement)
        
        return new_achievements
    
    def _create_achievement(
        self,
        user_id: int,
        code: str,
        title: str,
        description: str,
        icon: str,
        category: str,
        session_id: int | None = None
    ) -> Achievement:
        """Create an achievement using AchievementService for constraint handling."""
        from ....services.achievement_service import AchievementService
        
        # Use AchievementService.create_achievement to maintain consistency and handle constraints
        return AchievementService.create_achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            session_id=session_id,
        )

