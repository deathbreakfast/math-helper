"""Basic milestone achievement checker.

Handles non-tier-based milestone achievements like first-steps, first-victory,
and operation_accuracy achievements.
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, User
from .base_checker import AchievementChecker
from ..achievement_utils import create_achievement, debug_print
from ..achievement_queries.achievement_query_service import AchievementQueryService


class BasicMilestoneChecker(AchievementChecker):
    """Checker for basic milestone achievements (question_count, operation_accuracy)."""
    
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
        """Check and award basic milestone achievements.
        
        Args:
            user: The user to check achievements for
            metrics: User metrics dictionary
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        if not metrics:
            return new_achievements
        
        user_achievement_codes = AchievementQueryService.get_achievement_codes(user.id)
        
        total_answers = metrics.get("questions_answered", 0)
        stats = metrics.get("operation_stats", {})
        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0
        
        # Process basic milestone achievements (non-tier-based)
        for achievement_code, config in self.achievement_configs.items():
            if achievement_code in user_achievement_codes:
                continue
            
            # Skip tier-based milestone achievements (handled by MilestoneChecker)
            if (achievement_code.startswith("question-master-") or
                achievement_code.startswith("speed-demon-") or
                achievement_code.startswith("week-warrior-")):
                continue
            
            requirements = config.get("requirements", {})
            req_type = requirements.get("type")
            meets_requirements = False
            
            # Check question_count achievements (basic milestones like first-steps, first-victory)
            if req_type == "question_count":
                min_questions = requirements.get("min_questions", 0)
                meets_requirements = total_answers >= min_questions
            
            # Check operation_accuracy achievements
            elif req_type == "operation_accuracy":
                min_accuracy = requirements.get("min_accuracy", 0.0)
                meets_requirements = max_accuracy >= (min_accuracy * 100)  # Convert to percentage
            
            # Skip other types (handled by other checkers)
            else:
                continue
            
            if meets_requirements:
                debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} ({req_type})")
                print(f"[ACHIEVEMENT INFO] Awarding '{config['title']}' ({achievement_code}) to user {user.id} - {config['description']}")
                achievement = create_achievement(
                    user_id=user.id,
                    code=achievement_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                    session_id=session_id,
                )
                new_achievements.append(achievement)
            else:
                debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding {achievement_code} ({req_type})")
        
        return new_achievements

