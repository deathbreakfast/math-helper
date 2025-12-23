"""Achievement service for rules engine and achievement assignment."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..database import log_query
from ..models import Achievement, PracticeSession, User

# Import utility functions
from .achievements.achievement_utils import (
    get_achievement_configs as _get_achievement_configs,
)


class AchievementService:
    """Service for achievement-related operations."""

    @staticmethod
    @log_query
    def ensure_achievements(user: User, metrics: dict[str, Any] | None = None, session_id: int | None = None) -> list[Achievement]:
        """Ensure required achievements exist for a user based on their metrics.
        
        Optimized to skip expensive checking if user has no new activity since last check.
        
        Args:
            user: User to check achievements for
            metrics: Optional pre-computed user metrics
            session_id: Optional session ID to link achievements to a specific session
        
        Returns:
            List of all achievements for the user
        """
        from .achievements.achievement_orchestrator import AchievementOrchestrator
        
        achievement_configs = _get_achievement_configs()
        orchestrator = AchievementOrchestrator(achievement_configs)
        
        return orchestrator.ensure_achievements(user, metrics=metrics, session_id=session_id)

    @staticmethod
    def _ensure_achievements_with_data(
        user: User,
        metrics: dict[str, Any],
        existing_achievements: list[Achievement],
        user_responses: list,
        user_sessions: list[PracticeSession]
    ) -> list[Achievement]:
        """Internal helper to ensure achievements using pre-loaded data.
        
        This is optimized for batch processing where responses and sessions
        are already loaded in memory.
        
        Args:
            user: User object
            metrics: Pre-computed metrics for the user
            existing_achievements: Pre-loaded achievements for the user
            user_responses: Pre-loaded responses for the user
            user_sessions: Pre-loaded sessions for the user
            
        Returns:
            List of all achievements for the user
        """
        from .achievements.achievement_orchestrator import AchievementOrchestrator
        
        achievement_configs = _get_achievement_configs()
        orchestrator = AchievementOrchestrator(achievement_configs)
        
        return orchestrator.ensure_achievements_with_data(
            user, metrics, existing_achievements, user_responses, user_sessions
        )

    @staticmethod
    @log_query
    def ensure_achievements_batch(
        users: list[User], 
        all_metrics: dict[int, dict[str, Any]]
    ) -> dict[int, list[Achievement]]:
        """Ensure achievements for multiple users in batch.
        
        This batches the achievement queries but still processes each user individually
        to maintain the complex achievement checking logic.
        
        Args:
            users: List of User objects
            all_metrics: Dictionary mapping user_id to metrics dict
            
        Returns:
            Dictionary mapping user_id to list of achievements
        """
        from .achievements.achievement_orchestrator import AchievementOrchestrator
        
        achievement_configs = _get_achievement_configs()
        orchestrator = AchievementOrchestrator(achievement_configs)
        
        return orchestrator.ensure_achievements_batch(users, all_metrics)

    @staticmethod
    @log_query
    def get_user_achievements(user_id: int, limit: int | None = None) -> list[Achievement]:
        """Get all achievements for a user."""
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.get_user_achievements(user_id, limit=limit)

    @staticmethod
    @log_query
    def get_achievements_by_session(session_id: int) -> list[Achievement]:
        """Get all achievements for a specific session using indexed session_id field.
        
        Args:
            session_id: The session ID to query achievements for
        
        Returns:
            List of achievements linked to the session, ordered by earned_at DESC
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.get_achievements_by_session(session_id)

    @staticmethod
    @log_query
    def get_achievements_by_code(user_id: int, achievement_code: str) -> list[Achievement]:
        """Get all achievements for a user by achievement code (including metadata variants).
        
        Args:
            user_id: The user ID to query achievements for
            achievement_code: The achievement code to filter by
        
        Returns:
            List of achievements with the given code for the user, ordered by earned_at DESC
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.get_achievements_by_code(user_id, achievement_code)

    @staticmethod
    @log_query
    def get_achievements_by_category(
        user_id: int | None = None, category: str | None = None, limit: int = 50, include_user_name: bool = False
    ) -> list[Achievement]:
        """Get achievements filtered by user and/or category.
        
        Args:
            user_id: Optional user ID to filter achievements
            category: Optional category to filter achievements
            limit: Maximum number of achievements to return
            include_user_name: If True, join with User table to include user name (for all-users queries)
        
        Returns:
            List of Achievement objects, ordered by earned_at DESC (most recent first)
            Uses indexed earned_at column for optimal performance
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.get_achievements_by_category(
            user_id=user_id,
            category=category,
            limit=limit,
            include_user_name=include_user_name
        )

    @staticmethod
    @log_query
    def create_achievement(
        user_id: int,
        code: str,
        title: str,
        description: str,
        icon: str,
        category: str,
        earned_at: datetime | None = None,
        session_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Achievement:
        """Manually create an achievement for a user.
        
        Args:
            user_id: User ID
            code: Achievement code
            title: Achievement title
            description: Achievement description
            icon: Achievement icon
            category: Achievement category
            earned_at: When achievement was earned (defaults to now)
            session_id: Optional session ID to link achievement
            metadata: Optional metadata dict (will be stored as JSON string)
        """
        from .achievements.achievement_utils import create_achievement as _create_achievement
        
        return _create_achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            earned_at=earned_at,
            session_id=session_id,
            metadata=metadata,
        )

    @staticmethod
    @log_query
    def get_achievement_codes(user_id: int) -> set[str]:
        """Get set of achievement codes earned by a user."""
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.get_achievement_codes(user_id)

    @staticmethod
    def serialize_achievement(achievement: Achievement, user_name: str | None = None) -> dict[str, Any]:
        """Serialize an achievement to a dictionary.
        
        Args:
            achievement: The achievement object to serialize
            user_name: Optional user name to include in serialization
        """
        from .achievements.achievement_utils import serialize_achievement as _serialize_achievement
        
        return _serialize_achievement(achievement, user_name=user_name)

    @staticmethod
    @log_query
    def check_all_achievements(user: User, metrics: dict[str, Any], session_id: int | None = None) -> list[Achievement]:
        """Check and award all achievements from config (including milestone, speed, streak, accuracy).
        
        Args:
            user: User to check achievements for
            metrics: User metrics dictionary
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.milestone_checker import MilestoneChecker
        from .achievements.achievement_checkers.basic_milestone_checker import BasicMilestoneChecker
        from .achievements.achievement_checkers.session_achievements_checker import SessionAchievementsChecker
        
        achievement_configs = _get_achievement_configs()
        milestone_checker = MilestoneChecker(achievement_configs)
        basic_milestone_checker = BasicMilestoneChecker(achievement_configs)
        session_achievements_checker = SessionAchievementsChecker(achievement_configs)
        
        # Use MilestoneChecker to handle tier-based milestone achievements
        milestone_achievements = milestone_checker.check(user, metrics, session_id)
        
        # Use BasicMilestoneChecker to handle non-tier-based milestones (question_count, operation_accuracy)
        basic_milestone_achievements = basic_milestone_checker.check(user, metrics, session_id)
        
        # Use SessionAchievementsChecker to handle session-based achievements (completed_session_count, etc.)
        session_achievements = session_achievements_checker.check(user, metrics, session_id)
        
        # Combine all achievements
        all_new_achievements = milestone_achievements + basic_milestone_achievements + session_achievements
        return all_new_achievements

    @staticmethod
    @log_query
    def check_level_specific_achievements(user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award level-specific achievements based on configuration.
        
        Args:
            user: User to check achievements for
            session_id: Optional session ID to link achievements to a specific session
        
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.level_checker import LevelAchievementChecker
        
        achievement_configs = _get_achievement_configs()
        level_checker = LevelAchievementChecker(achievement_configs)
        
        # Use LevelAchievementChecker to handle perfect_streak
        level_achievements = level_checker.check(user, session_id=session_id)
        
        # Process other achievements using specialized checkers (composition pattern)
        from .achievements.achievement_checkers import (
            OperationCountChecker,
            LevelAccuracyChecker,
            LevelCorrectCountChecker,
            SessionAchievementsChecker,
            AchievementCountChecker,
        )
        
        # Use composition: each checker handles specific achievement types
        other_checkers = [
            OperationCountChecker(achievement_configs),
            LevelAccuracyChecker(achievement_configs),
            LevelCorrectCountChecker(achievement_configs),
            SessionAchievementsChecker(achievement_configs),
            AchievementCountChecker(achievement_configs),
        ]
        
        new_achievements = []
        for checker in other_checkers:
            achievements = checker.check(user, session_id=session_id)
            new_achievements.extend(achievements)
        
        # Combine level achievements with other achievements
        all_new_achievements = level_achievements + new_achievements
        
        if all_new_achievements:
            from ..database import flush_or_commit
            flush_or_commit()
        
        return all_new_achievements

    @staticmethod
    @log_query
    # Test achievement methods removed - test achievements are no longer used

    @staticmethod
    @log_query
    def count_achievements_by_code(user_id: int, achievement_code: str) -> int:
        """Count how many times a user has earned a specific achievement code.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count
            
        Returns:
            Number of times the achievement was earned
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.count_achievements_by_code(user_id, achievement_code)

    @staticmethod
    @log_query
    def count_achievements_by_code_with_filters(
        user_id: int,
        achievement_code: str,
        level: int | None = None,
        min_accuracy: float | None = None,
        operation: str | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> int:
        """Count achievements with filters for level, accuracy, operation, and metadata.
        
        Supports tier substitution: higher tier achievements can substitute for lower tier requirements.
        Conversion: 4 bronze = 2 silver = 1 gold, etc.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count (must be tiered code like "addition-basics-bronze")
            level: Optional level filter (session level must match) - DEPRECATED, use metadata_filter instead
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            metadata_filter: Optional metadata filter dict (e.g., {"level": 1}) - filters achievements by metadata
            
        Returns:
            Number of achievements matching all filters (with tier substitution applied)
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.count_achievements_by_code_with_filters(
            user_id=user_id,
            achievement_code=achievement_code,
            level=level,
            min_accuracy=min_accuracy,
            operation=operation,
            metadata_filter=metadata_filter,
        )

    @staticmethod
    @log_query
    def check_level_master_achievements(user: User) -> list[Achievement]:
        """Check and award Level Master achievements (consecutive correct at any level).
        
        This checks consecutive correct answers at each level separately, ignoring incorrect
        answers at other levels. For example, if a user gets level 1 questions correct
        but misses a level 2 question in between, the level 1 consecutive count continues.
        
        The achievement is awarded based on the maximum consecutive correct achieved at any level.
        We also track per-level to determine if user has achieved bronze at all levels (for Level Grandmaster).
        
        Args:
            user: The user to check
        
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.level_master_checker import LevelMasterChecker
        
        achievement_configs = _get_achievement_configs()
        checker = LevelMasterChecker(achievement_configs)
        
        return checker.check(user)

    @staticmethod
    @log_query
    def check_lightning_fast_achievements(user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award Lightning Fast (level-specific speed) achievements.
        
        Awards lightning-fast achievements per level with metadata when user achieves
        required speed at a specific level.
        
        Args:
            user: The user to check
            session_id: Optional session ID to link achievements
            
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.lightning_fast_checker import LightningFastChecker
        
        achievement_configs = _get_achievement_configs()
        checker = LightningFastChecker(achievement_configs)
        
        return checker.check(user, session_id=session_id)

    @staticmethod
    @log_query
    def check_accuracy_ace_achievements(session: PracticeSession) -> list[Achievement]:
        """Check and award Accuracy Ace achievements based on session accuracy.
        
        Awards accuracy-ace achievements when a session meets the accuracy threshold
        and minimum question count. Awards the highest qualifying tier.
        
        Args:
            session: Completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.accuracy_ace_checker import AccuracyAceChecker
        
        achievement_configs = _get_achievement_configs()
        checker = AccuracyAceChecker(achievement_configs)
        
        return checker.check(session)

    @staticmethod
    @log_query
    def check_so_wow_achievements(user: User, newly_awarded_achievements: list[Achievement], session_id: int | None = None) -> list[Achievement]:
        """Check and award So, Wow! achievements when user earns their first achievement of a tier.
        
        Awards "So, Wow! (Tier)" when a user earns their first bronze+ achievement of that tier.
        Supports multiple tiers being awarded in one session.
        
        Args:
            user: The user to check
            newly_awarded_achievements: List of achievements just awarded in this session
            session_id: Optional session ID to link achievements
            
        Returns:
            List of newly created So, Wow! achievements
        """
        from .achievements.achievement_checkers.so_wow_checker import SoWowChecker
        
        achievement_configs = _get_achievement_configs()
        checker = SoWowChecker(achievement_configs)
        
        return checker.check(user, newly_awarded_achievements, session_id=session_id)

    @staticmethod
    @log_query
    def check_level_grandmaster_achievement(user: User) -> list[Achievement]:
        """Check and award Level Grandmaster milestone achievement.
        
        Requires having Level Master (Bronze) achievement and having achieved
        30 consecutive correct at ALL levels in the system.
        Previously named "Master Of All", renamed to "Level Grandmaster".
        
        Args:
            user: The user to check
        
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.level_grandmaster_checker import LevelGrandmasterChecker
        
        achievement_configs = _get_achievement_configs()
        checker = LevelGrandmasterChecker(achievement_configs)
        
        return checker.check(user)

    @staticmethod
    @log_query
    def checkChampionEligibility(
        achievement_code: str, session: PracticeSession, tier: str
    ) -> bool:
        """Check if a session qualifies for Champion tier and award if eligible.
        
        Args:
            achievement_code: Achievement code (e.g., "addition-basics-champion")
            session: PracticeSession that achieved the requirements
            tier: Tier name (should be "champion")
            
        Returns:
            True if Champion tier was awarded, False otherwise
        """
        from .achievements.achievement_validators.champion_validator import ChampionValidator
        
        validator = ChampionValidator()
        return validator.check_eligibility(achievement_code, session, tier)

    @staticmethod
    @log_query
    def check_generic_accuracy_achievements(session: PracticeSession) -> list[Achievement]:
        """Check session for generic accuracy achievements and award highest tier achieved.
        
        Args:
            session: Completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.generic_accuracy_checker import GenericAccuracyChecker
        
        achievement_configs = _get_achievement_configs()
        checker = GenericAccuracyChecker(achievement_configs)
        
        return checker.check(session)

    # Test achievement methods removed - test achievements are no longer used

