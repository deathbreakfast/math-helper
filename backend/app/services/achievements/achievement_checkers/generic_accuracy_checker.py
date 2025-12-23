"""Generic accuracy achievement checker.

Checks for operation-level specific accuracy achievements (e.g., "addition-basics-bronze").
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response
from ....config.achievements import ACCURACY_ACHIEVEMENTS
from ....utils.tier_utils import ALL_TIERS, get_tier_value
from ....services.achievement_service import AchievementService
from .... import db
from .base_checker import AchievementChecker


class GenericAccuracyChecker(AchievementChecker):
    """Checker for generic accuracy achievements (operation-level specific)."""
    
    def __init__(self, achievement_configs: dict[str, Any] | None = None):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations (optional, will use default if not provided)
        """
        self.achievement_configs = achievement_configs
    
    def _extract_session_context(self, session: PracticeSession) -> dict[str, Any] | None:
        """Extract operation, level, and metrics from session.
        
        Returns a dict with operation, level, and metrics, or None if session is invalid.
        """
        if not session.completed_at or not session.level:
            return None
        
        # Get operation from session's questions
        first_question = (
            Question.query.join(Response)
            .filter(Response.session_id == session.id)
            .first()
        )
        
        if not first_question:
            return None
        
        # Calculate session metrics
        total_questions = session.total_questions
        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0  # Convert to 0-1 range
        total_duration_ms = session.total_duration_ms or 0
        avg_time_per_question = (
            (total_duration_ms / 1000.0 / total_questions)
            if total_questions > 0 and total_duration_ms
            else None
        )
        
        return {
            "operation": first_question.operation,
            "level": session.level,
            "total_questions": total_questions,
            "accuracy": accuracy,
            "avg_time_per_question": avg_time_per_question,
        }
    
    def _meets_requirements(
        self,
        requirements: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """Check if session context meets achievement requirements.
        
        Args:
            requirements: Achievement requirements dict
            context: Session context (operation, level, metrics)
            
        Returns:
            True if all requirements are met, False otherwise
        """
        # Check level and operation match
        if requirements.get("level") != context["level"]:
            return False
        if requirements.get("operation") != context["operation"]:
            return False
        
        # Extract requirement thresholds
        min_accuracy_req = requirements.get("min_accuracy", 0.0)
        min_questions_req = requirements.get("min_questions", 0)
        max_questions_req = requirements.get("max_questions")
        max_speed_req = requirements.get("max_speed")
        
        # Check accuracy requirement
        if context["accuracy"] < min_accuracy_req:
            return False
        
        # Check question count requirements
        total_questions = context["total_questions"]
        if total_questions < min_questions_req:
            return False
        if max_questions_req and total_questions > max_questions_req:
            return False
        
        # Check speed requirement
        if max_speed_req:
            avg_time = context["avg_time_per_question"]
            if avg_time is None or avg_time >= max_speed_req:
                return False
        
        return True
    
    def _check_champion_eligibility(
        self,
        operation: str,
        context: dict[str, Any],
        session: PracticeSession,
    ) -> tuple[str, dict[str, Any]] | None:
        """Check if Champion tier is eligible and should be awarded instead of Divine.
        
        Args:
            operation: Operation name (e.g., "addition")
            context: Session context with metrics
            session: Practice session
            
        Returns:
            Tuple of (champion_code, champion_config) if eligible, None otherwise
        """
        champion_code = f"{operation}-basics-champion"
        
        if champion_code not in ACCURACY_ACHIEVEMENTS:
            return None
        
        champion_config = ACCURACY_ACHIEVEMENTS[champion_code]
        champion_req = champion_config.get("requirements", {})
        
        # Check if Champion requirements are met
        if not self._meets_requirements(champion_req, context):
            return None
        
        # Check server record eligibility
        if AchievementService.checkChampionEligibility(champion_code, session, "champion"):
            return (champion_code, champion_config)
        
        return None
    
    def _find_eligible_tiers(
        self,
        operation: str,
        context: dict[str, Any],
        user_achievement_codes: set[str],
        configs_to_check: dict[str, Any],
    ) -> list[tuple[str, str, dict[str, Any]]]:
        """Find all tiers that meet requirements for this operation and level.
        
        Args:
            operation: Operation name (e.g., "addition")
            context: Session context with metrics
            user_achievement_codes: Set of achievement codes user already has
            configs_to_check: Achievement configs to check
            
        Returns:
            List of (tier, achievement_code, config) tuples for eligible tiers
        """
        eligible_tiers = []
        
        for tier in reversed(ALL_TIERS):  # Check from highest to lowest
            achievement_code = f"{operation}-basics-{tier}"
            
            # Skip if not in config or already earned
            if achievement_code not in configs_to_check:
                continue
            if achievement_code in user_achievement_codes:
                continue
            
            config = configs_to_check[achievement_code]
            requirements = config.get("requirements", {})
            
            # Check if requirements are met
            if self._meets_requirements(requirements, context):
                eligible_tiers.append((tier, achievement_code, config))
        
        return eligible_tiers
    
    def _award_achievement(
        self,
        session: PracticeSession,
        achievement_code: str,
        config: dict[str, Any],
    ) -> Achievement:
        """Create and return an achievement for the session.
        
        Args:
            session: Practice session
            achievement_code: Achievement code
            config: Achievement config
            
        Returns:
            Created Achievement object
        """
        return AchievementService.create_achievement(
            user_id=session.user_id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session.id,
        )
    
    def check(self, session: PracticeSession) -> list[Achievement]:
        """Check session for generic accuracy achievements and award highest tier achieved.
        
        Args:
            session: Completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        if not session.completed_at:
            return []
        
        # Extract session context
        context = self._extract_session_context(session)
        if not context:
            return []
        
        # Get user's existing achievements
        user_achievement_codes = AchievementService.get_achievement_codes(session.user_id)
        
        # Get configs to check
        configs_to_check = self.achievement_configs if self.achievement_configs else ACCURACY_ACHIEVEMENTS
        
        # Find all eligible tiers
        eligible_tiers = self._find_eligible_tiers(
            context["operation"],
            context,
            user_achievement_codes,
            configs_to_check,
        )
        
        if not eligible_tiers:
            return []
        
        # Sort by tier value (highest first) and get the highest
        eligible_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
        highest_tier, achievement_code, config = eligible_tiers[0]
        
        # Check for Champion tier eligibility if this is Divine tier
        if highest_tier == "divine":
            champion_result = self._check_champion_eligibility(
                context["operation"],
                context,
                session,
            )
            if champion_result:
                achievement_code, config = champion_result
        
        # Award the achievement
        achievement = self._award_achievement(session, achievement_code, config)
        
        from ....database import flush_or_commit
        flush_or_commit()
        
        return [achievement]

