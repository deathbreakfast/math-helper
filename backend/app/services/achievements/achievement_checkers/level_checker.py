"""Level-specific achievement checker orchestrator.

Coordinates perfect_streak checker.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, User
from .base_checker import AchievementChecker
from .perfect_streak_checker import PerfectStreakChecker


class LevelAchievementChecker(AchievementChecker):
    """Orchestrator for level-specific achievement checkers."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
        self.perfect_streak_checker = PerfectStreakChecker(achievement_configs)
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award level-specific achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        # Run level-specific checkers
        achievements = self.perfect_streak_checker.check(user, metrics, session_id)
        new_achievements.extend(achievements)
        
        return new_achievements


