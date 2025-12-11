"""Base abstract class for achievement checkers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ....models import Achievement, User


class AchievementChecker(ABC):
    """Abstract base class for achievement checkers.
    
    All achievement checkers must inherit from this class and implement
    the check method to determine which achievements should be awarded.
    """
    
    @abstractmethod
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and return achievements that should be awarded.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics
            session_id: Optional session ID to link achievements to a specific session
        
        Returns:
            List of newly created Achievement objects that should be awarded
        """
        pass

