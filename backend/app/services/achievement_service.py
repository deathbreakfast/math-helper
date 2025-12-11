"""Achievement service for rules engine and achievement assignment."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from sqlalchemy import func

from ..database import log_query, transaction
from ..models import Achievement, PracticeSession, Question, Response, User, db
from ..services.level_config_service import LevelConfigService
from .analytics_service import AnalyticsService

# Import utility functions
from .achievements.achievement_utils import (
    get_achievement_configs as _get_achievement_configs,
    clear_achievement_configs_cache as _clear_achievement_configs_cache,
    debug_print as _debug_print,
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
        user_responses: list[Response],
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
        if earned_at is None:
            earned_at = datetime.utcnow()

        # Serialize metadata to JSON string if provided
        metadata_json = json.dumps(metadata) if metadata else None

        # Check if already exists - need to check both code and metadata
        # For achievements without metadata, check by code only
        # For achievements with metadata, check by code and metadata
        if metadata_json:
            existing = Achievement.query.filter_by(
                user_id=user_id, code=code, achievement_metadata=metadata_json
            ).first()
        else:
            existing = Achievement.query.filter_by(
                user_id=user_id, code=code
            ).filter(
                (Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == "")
            ).first()
        
        if existing:
            # If we have a session_id and the existing achievement doesn't have one (or has a different one),
            # update it to link to this session. This ensures achievements earned in this session are properly linked.
            if session_id and existing.session_id != session_id:
                existing.session_id = session_id
                db.session.add(existing)
                db.session.commit()
            return existing

        with transaction():
            achievement = Achievement(
                user_id=user_id,
                code=code,
                title=title,
                description=description,
                icon=icon,
                category=category,
                earned_at=earned_at,
                session_id=session_id,
                achievement_metadata=metadata_json,
            )
            db.session.add(achievement)
            db.session.flush()

        return achievement

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
    def check_consecutive_correct_achievements(user: User, test_type: str | None = None) -> list[Achievement]:
        """Check and award '30 correct in a row' achievements for test types.
        
        This checks the user's recent responses to see if they have 30 consecutive
        correct answers for a specific test type, and awards the mastery achievement.
        
        Args:
            user: The user to check
            test_type: Optional test type to check (e.g., "multiplication-by-1")
        
        Returns:
            List of newly created achievements
        """
        from .achievements.achievement_checkers.consecutive_checker import ConsecutiveChecker
        
        achievement_configs = _get_achievement_configs()
        checker = ConsecutiveChecker(achievement_configs)
        
        return checker.check(user, test_type=test_type)

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
        
        achievement_configs = _get_achievement_configs()
        milestone_checker = MilestoneChecker(achievement_configs)
        
        # Use MilestoneChecker to handle milestone achievements
        milestone_achievements = milestone_checker.check(user, metrics, session_id)
        
        # Process other achievements (non-tier-based milestones like first-steps, first-victory)
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        total_answers = metrics.get("questions_answered", 0)
        stats = metrics.get("operation_stats", {})
        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0
        
        # Process other achievements (non-tier-based milestones)
        for achievement_code, config in achievement_configs.items():
            if achievement_code in user_achievement_codes:
                continue
            
            # Skip milestone achievements (handled by MilestoneChecker)
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
            
            # Skip other types (handled by check_level_specific_achievements)
            else:
                continue
            
            if meets_requirements:
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} ({req_type})")
                print(f"[ACHIEVEMENT INFO] Awarding '{config['title']}' ({achievement_code}) to user {user.id} - {config['description']}")
                achievement = AchievementService.create_achievement(
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
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding {achievement_code} ({req_type})")
        
        # Combine milestone achievements with other achievements
        all_new_achievements = milestone_achievements + new_achievements
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
        
        # Use LevelAchievementChecker to handle fast_session, fast_questions, and perfect_streak
        level_achievements = level_checker.check(user, session_id=session_id)
        
        # Process other achievements using OtherAchievementsChecker
        from .achievements.achievement_checkers.other_achievements_checker import OtherAchievementsChecker
        
        other_checker = OtherAchievementsChecker(achievement_configs)
        new_achievements = other_checker.check(user, session_id=session_id)
            
            # Check operation_count achievements
        # Combine level achievements with other achievements
        all_new_achievements = level_achievements + new_achievements
        
        if all_new_achievements:
            db.session.commit()
        
        return all_new_achievements

    @staticmethod
    @log_query
    def validate_and_cleanup_tier_achievements(user_id: int) -> int:
        """Validate tiered test achievements and remove ones that don't meet requirements.
        
        This is a cleanup function to remove incorrectly awarded achievements from before
        the validation was properly implemented.
        
        Args:
            user_id: The user ID to validate achievements for
            
        Returns:
            Number of achievements removed
        """
        from .achievements.achievement_validators.tier_validator import TierValidator
        
        validator = TierValidator()
        return validator.validate(user_id)

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
    def count_achievements_by_test_type_with_filters(
        user_id: int,
        test_type: str,
        level: int | None = None,
        min_accuracy: float | None = None,
        operation: str | None = None,
    ) -> int:
        """Count achievements for a test type with filters for level, accuracy, and operation.
        
        This counts all achievements that match the test type pattern (e.g., "addition-1digit-bronze",
        "addition-1digit-silver", etc.) with the specified filters.
        
        Args:
            user_id: User ID
            test_type: Test type identifier (e.g., "addition-1digit")
            level: Optional level filter (session level must match)
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            
        Returns:
            Number of achievements matching all filters
        """
        from .achievements.achievement_queries.achievement_query_service import AchievementQueryService
        
        return AchievementQueryService.count_achievements_by_test_type_with_filters(
            user_id=user_id,
            test_type=test_type,
            level=level,
            min_accuracy=min_accuracy,
            operation=operation,
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

