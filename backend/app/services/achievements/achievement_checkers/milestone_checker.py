"""Milestone achievement checker.

Awards achievements for question-master, speed-demon, and week-warrior milestones.
These are tiered achievements based on lifetime metrics.
"""

from __future__ import annotations

from typing import Any

from ....config.concepts_config import get_concept_speed_multiplier
from ....models import Achievement, PracticeSession, User, db
from .base_checker import AchievementChecker


class MilestoneChecker(AchievementChecker):
    """Checker for milestone achievements (question-master, speed-demon, week-warrior)."""
    
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
        """Check and award milestone achievements.
        
        Args:
            user: The user to check achievements for
            metrics: Pre-computed user metrics (must include questions_answered, average_speed_seconds, operation_stats)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        if not metrics:
            return new_achievements
        
        # Extract metrics
        total_answers = metrics.get("questions_answered", 0)
        stats = metrics.get("operation_stats", {})
        current_streak = stats.get("currentStreak", 0)
        
        # For Speed Demon, use session-based speed if session_id is provided
        # This ensures we award based on this session's performance, not lifetime average
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        if session_id:
            session = db.session.get(PracticeSession, session_id)
            if session and session.total_duration_ms and session.total_questions and session.total_questions > 0:
                # Calculate session average speed
                session_avg_speed = (session.total_duration_ms / 1000.0) / session.total_questions
                # Use session speed instead of lifetime average for Speed Demon
                avg_speed = session_avg_speed
        
        # Group milestone achievements by type
        # Note: We don't check for existing achievements here - create_achievement() handles constraints
        question_master_achievements = []
        speed_demon_achievements = []
        week_warrior_achievements = []
        
        for achievement_code, config in self.achievement_configs.items():
            if achievement_code.startswith("question-master-"):
                question_master_achievements.append((achievement_code, config))
            elif achievement_code.startswith("speed-demon-"):
                speed_demon_achievements.append((achievement_code, config))
            elif achievement_code.startswith("week-warrior-"):
                week_warrior_achievements.append((achievement_code, config))
        
        # Process question_master achievements (award highest tier only)
        if question_master_achievements:
            achievement = self._check_question_master(
                user, question_master_achievements, total_answers, metrics, session_id
            )
            if achievement:
                new_achievements.append(achievement)
        
        # Process speed_demon achievements (award highest tier only)
        # Use session speed if available, otherwise fall back to lifetime average
        if speed_demon_achievements and avg_speed > 0:
            achievement = self._check_speed_demon(
                user, speed_demon_achievements, avg_speed, total_answers, session_id
            )
            if achievement:
                new_achievements.append(achievement)
        
        # Process week_warrior achievements (award highest tier only)
        if week_warrior_achievements:
            achievement = self._check_week_warrior(
                user, week_warrior_achievements, current_streak, metrics, session_id
            )
            if achievement:
                new_achievements.append(achievement)
        
        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()
        
        return new_achievements
    
    def _check_question_master(
        self,
        user: User,
        question_master_achievements: list[tuple[str, dict[str, Any]]],
        total_answers: int,
        metrics: dict[str, Any],
        session_id: int | None = None
    ) -> Achievement | None:
        """Check and award question-master achievements.
        
        Args:
            user: The user to check
            question_master_achievements: List of (code, config) tuples
            total_answers: Total questions answered
            metrics: User metrics dict
            session_id: Optional session ID
        
        Returns:
            Achievement if awarded, None otherwise
        """
        from ....utils.tier_utils import get_tier_value
        
        qualifying_tiers = []
        for achievement_code, config in question_master_achievements:
            requirements = config.get("requirements", {})
            min_questions = requirements.get("min_questions", 0)
            if total_answers >= min_questions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if not qualifying_tiers:
            return None
        
        # Sort by tier value (highest first)
        qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
        highest_tier, achievement_code, config = qualifying_tiers[0]
        
        # Check for Champion tier if this is Divine
        # Note: Champion eligibility requires session context, so for milestone achievements
        # based on lifetime metrics, we skip champion checks here. Champion tier for milestones
        # would need to be checked at session completion time with proper session context.
        if highest_tier == "divine":
            champion_code = "question-master-champion"
            champion_config = self.achievement_configs.get(champion_code)
            if champion_config:
                champion_req = champion_config.get("requirements", {})
                if total_answers >= champion_req.get("min_questions", 0):
                    # Champion eligibility check requires session context
                    # For milestone achievements, this would be checked at session completion
                    # For now, award divine tier
                    pass
        
        return self._create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
        )
    
    def _check_speed_demon(
        self,
        user: User,
        speed_demon_achievements: list[tuple[str, dict[str, Any]]],
        avg_speed: float,
        total_answers: int,
        session_id: int | None = None
    ) -> Achievement | None:
        """Check and award speed-demon achievements.
        
        Args:
            user: The user to check
            speed_demon_achievements: List of (code, config) tuples
            avg_speed: Average speed in seconds
            total_answers: Total questions answered
            session_id: Optional session ID
        
        Returns:
            Achievement if awarded, None otherwise
        """
        from ....utils.tier_utils import get_tier_value
        
        # Get speed multiplier from session's concept_id if available
        speed_multiplier = 1.0
        if session_id:
            session = db.session.get(PracticeSession, session_id)
            if session and session.concept_id:
                speed_multiplier = get_concept_speed_multiplier(session.concept_id)
        
        qualifying_tiers = []
        for achievement_code, config in speed_demon_achievements:
            requirements = config.get("requirements", {})
            max_speed = requirements.get("max_speed_seconds", 999)
            # Apply speed multiplier to threshold
            adjusted_max_speed = max_speed * speed_multiplier
            min_questions = requirements.get("min_questions", 0)
            if avg_speed <= adjusted_max_speed and total_answers >= min_questions:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if not qualifying_tiers:
            return None
        
        # Sort by tier value (highest first)
        qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
        highest_tier, achievement_code, config = qualifying_tiers[0]
        
        # Check for Champion tier if this is Divine
        # Note: Champion check for speed-demon requires session context, so skip for now
        # This is consistent with the original implementation
        if highest_tier == "divine":
            champion_code = "speed-demon-champion"
            champion_config = self.achievement_configs.get(champion_code)
            if champion_config:
                champion_req = champion_config.get("requirements", {})
                champion_max_speed = champion_req.get("max_speed_seconds", 0.5)
                # Apply speed multiplier to champion threshold
                adjusted_champion_max_speed = champion_max_speed * speed_multiplier
                if avg_speed <= adjusted_champion_max_speed:
                    # Champion check would need session context, skip for now
                    pass
        
        return self._create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
        )
    
    def _check_week_warrior(
        self,
        user: User,
        week_warrior_achievements: list[tuple[str, dict[str, Any]]],
        current_streak: int,
        metrics: dict[str, Any],
        session_id: int | None = None
    ) -> Achievement | None:
        """Check and award week-warrior achievements.
        
        Args:
            user: The user to check
            week_warrior_achievements: List of (code, config) tuples
            current_streak: Current consecutive days streak
            metrics: User metrics dict
            session_id: Optional session ID
        
        Returns:
            Achievement if awarded, None otherwise
        """
        from ....utils.tier_utils import get_tier_value
        
        qualifying_tiers = []
        for achievement_code, config in week_warrior_achievements:
            requirements = config.get("requirements", {})
            min_streak = requirements.get("min_streak_days", 0)
            if current_streak >= min_streak:
                tier = config.get("tier", "bronze")
                qualifying_tiers.append((tier, achievement_code, config))
        
        if not qualifying_tiers:
            return None
        
        # Sort by tier value (highest first)
        qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
        highest_tier, achievement_code, config = qualifying_tiers[0]
        
        # Check for Champion tier if this is Divine
        # Note: Champion eligibility requires session context, so for milestone achievements
        # based on lifetime metrics, we skip champion checks here. Champion tier for milestones
        # would need to be checked at session completion time with proper session context.
        if highest_tier == "divine":
            champion_code = "week-warrior-champion"
            champion_config = self.achievement_configs.get(champion_code)
            if champion_config:
                champion_req = champion_config.get("requirements", {})
                if current_streak >= champion_req.get("min_streak_days", 0):
                    # Champion eligibility check requires session context
                    # For milestone achievements, this would be checked at session completion
                    # For now, award divine tier
                    pass
        
        return self._create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
        )
    
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
        """Create an achievement (helper method).
        
        This is a simplified version - in the full refactor, this would use
        a shared achievement creation service.
        """
        from datetime import datetime
        from ....services.achievement_service import AchievementService
        
        # Use AchievementService.create_achievement to maintain consistency
        return AchievementService.create_achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            session_id=session_id,
        )

