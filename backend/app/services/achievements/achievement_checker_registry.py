"""Registry for achievement checkers using strategy pattern.

This registry allows achievement checkers to be registered and discovered
dynamically, making it easier to add new achievement types without modifying
existing code.
"""

from __future__ import annotations

from typing import Any

from ..models import Achievement, User
from .achievement_checkers.base_checker import AchievementChecker


class AchievementCheckerRegistry:
    """Registry for managing achievement checkers.
    
    This registry uses the strategy pattern to allow different achievement
    types to be handled by specialized checkers. New checkers can be registered
    without modifying existing code.
    """
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize the registry with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
        self._checkers: list[AchievementChecker] = []
        self._checkers_by_type: dict[str, AchievementChecker] = {}
    
    def register(self, checker: AchievementChecker, requirement_types: list[str] | None = None) -> None:
        """Register an achievement checker.
        
        Args:
            checker: The checker instance to register
            requirement_types: Optional list of requirement types this checker handles
                               (e.g., ["operation_count", "level_accuracy"])
        """
        self._checkers.append(checker)
        if requirement_types:
            for req_type in requirement_types:
                self._checkers_by_type[req_type] = checker
    
    def get_checker_for_type(self, requirement_type: str) -> AchievementChecker | None:
        """Get a checker registered for a specific requirement type.
        
        Args:
            requirement_type: The requirement type (e.g., "operation_count")
            
        Returns:
            The checker instance, or None if not found
        """
        return self._checkers_by_type.get(requirement_type)
    
    def check_all(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Run all registered checkers and return combined results.
        
        Args:
            user: User to check achievements for
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of all newly created achievements
        """
        all_achievements = []
        for checker in self._checkers:
            achievements = checker.check(user, session_id=session_id)
            all_achievements.extend(achievements)
        return all_achievements
    
    def check_by_type(
        self,
        user: User,
        requirement_type: str,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Run a specific checker by requirement type.
        
        Args:
            user: User to check achievements for
            requirement_type: The requirement type to check
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of newly created achievements
        """
        checker = self.get_checker_for_type(requirement_type)
        if checker:
            return checker.check(user, session_id=session_id)
        return []

