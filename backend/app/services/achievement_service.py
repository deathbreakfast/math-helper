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

# Debug logging configuration
DEBUG_ACHIEVEMENTS = os.getenv("DEBUG_ACHIEVEMENTS", "false").lower() == "true"
DEBUG_LOG_FILE = os.getenv("DEBUG_ACHIEVEMENTS_LOG", "achievements_debug.log")

# Cache for achievement configs (rarely changes, so cache indefinitely)
_achievement_configs_cache: dict[str, Any] | None = None


def _get_achievement_configs() -> dict[str, Any]:
    """Get achievement configs with caching."""
    global _achievement_configs_cache
    if _achievement_configs_cache is None:
        _achievement_configs_cache = LevelConfigService.get_all_achievement_configs()
    return _achievement_configs_cache


def _clear_achievement_configs_cache() -> None:
    """Clear the achievement configs cache (for testing or config updates)."""
    global _achievement_configs_cache
    _achievement_configs_cache = None

def _debug_print(*args, **kwargs):
    """Print debug info to console and/or file based on configuration."""
    if not DEBUG_ACHIEVEMENTS:
        return
    
    message = " ".join(str(arg) for arg in args)
    
    # Print to console
    print(message, **kwargs)
    
    # Write to file
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception:
        pass  # Silently fail if file write fails


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
        # Get current achievements first to check if we can skip
        current_achievements = Achievement.query.filter_by(user_id=user.id).all()
        
        # Optimization: Skip expensive achievement checking if user has no new activity
        # Check if user has any responses at all
        last_response = (
            Response.query.filter_by(user_id=user.id)
            .order_by(Response.answered_at.desc())
            .first()
        )
        
        if last_response:
            # Get the most recent achievement timestamp
            most_recent_achievement = (
                Achievement.query.filter_by(user_id=user.id)
                .order_by(Achievement.earned_at.desc())
                .first()
            )
            
            # If user has achievements and last response is older than most recent achievement,
            # and user's updated_at hasn't changed, we can skip checking
            if most_recent_achievement:
                # Check if last response is before the most recent achievement
                # (meaning no new activity since last achievement was awarded)
                if last_response.answered_at <= most_recent_achievement.earned_at:
                    # Also check if user's updated_at hasn't changed (no level ups, etc.)
                    # This is a simple optimization - if nothing changed, skip expensive checks
                    # Note: We still return achievements, just skip the expensive checking
                    _debug_print(f"[ACHIEVEMENT DEBUG] Skipping achievement check for user {user.id} - no new activity since last achievement")
                    return current_achievements
        
        if metrics is None:
            metrics = AnalyticsService.compute_user_metrics(user.id)

        # DEBUG: Print user info and metrics
        _debug_print("\n" + "="*80)
        _debug_print(f"[ACHIEVEMENT DEBUG] ensure_achievements called for User ID: {user.id}, Name: {user.display_name}, Level: {user.level}")
        _debug_print(f"[ACHIEVEMENT DEBUG] Metrics: {metrics}")
        
        current_codes = [a.code for a in current_achievements]
        _debug_print(f"[ACHIEVEMENT DEBUG] Current achievements ({len(current_achievements)}): {current_codes}")
        _debug_print("="*80 + "\n")

        total_answers = metrics.get("questions_answered", 0)
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        stats = metrics.get("operation_stats", {})
        current_streak = stats.get("currentStreak", 0)
        earned_at = metrics.get("last_activity_at") or user.created_at or datetime.utcnow()

        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0

        # Check all achievements from config (including milestone, speed, streak, accuracy)
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking all achievements from config...")
        print(f"[ACHIEVEMENT INFO] User {user.id} metrics: {total_answers} questions, {avg_speed:.2f}s avg speed, {max_accuracy}% max accuracy, {current_streak} day streak")
        all_achievements = AchievementService.check_all_achievements(user, metrics, session_id=session_id)
        if all_achievements:
            # Extract codes and titles immediately before commit to avoid detached object issues
            all_achievement_codes = [a.code for a in all_achievements]
            all_achievement_titles = [a.title for a in all_achievements]
            _debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(all_achievements)} achievement(s) from config: {all_achievement_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(all_achievements)} general achievement(s): {all_achievement_titles}")
            db.session.commit()
        
        # Check level-specific achievements (operation_count, level_accuracy, level_correct_count, test_completion)
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking level-specific achievements...")
        level_achievements = AchievementService.check_level_specific_achievements(user, session_id=session_id)
        if level_achievements:
            # Extract codes and titles immediately before commit to avoid detached object issues
            level_achievement_codes = [a.code for a in level_achievements]
            level_achievement_titles = [a.title for a in level_achievements]
            _debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(level_achievements)} level-specific achievement(s): {level_achievement_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(level_achievements)} level-specific achievement(s): {level_achievement_titles}")
            db.session.commit()
        else:
            _debug_print(f"[ACHIEVEMENT DEBUG] No new level-specific achievements awarded")
        
        # Check Level Master achievements (consecutive correct at any level)
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking Level Master achievements...")
        level_master_achievements = AchievementService.check_level_master_achievements(user)
        if level_master_achievements:
            level_master_codes = [a.code for a in level_master_achievements]
            level_master_titles = [a.title for a in level_master_achievements]
            _debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(level_master_achievements)} Level Master achievement(s): {level_master_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(level_master_achievements)} Level Master achievement(s): {level_master_titles}")
            db.session.commit()
        
        # Check Level Grandmaster milestone achievement (Level Master Bronze on all levels)
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking Level Grandmaster achievement...")
        level_grandmaster_achievements = AchievementService.check_level_grandmaster_achievement(user)
        if level_grandmaster_achievements:
            level_grandmaster_codes = [a.code for a in level_grandmaster_achievements]
            level_grandmaster_titles = [a.title for a in level_grandmaster_achievements]
            _debug_print(f"[ACHIEVEMENT DEBUG] Awarded {len(level_grandmaster_achievements)} Level Grandmaster achievement(s): {level_grandmaster_codes}")
            print(f"[ACHIEVEMENT INFO] Awarded {len(level_grandmaster_achievements)} Level Grandmaster achievement(s): {level_grandmaster_titles}")
            db.session.commit()

        achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .order_by(Achievement.earned_at.desc())
            .all()
        )
        return achievements

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
        current_codes = [a.code for a in existing_achievements]
        
        total_answers = metrics.get("questions_answered", 0)
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        stats = metrics.get("operation_stats", {})
        current_streak = stats.get("currentStreak", 0)
        earned_at = metrics.get("last_activity_at") or user.created_at or datetime.utcnow()

        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0

        # Check all achievements from config (including milestone, speed, streak, accuracy)
        all_achievements = AchievementService.check_all_achievements(user, metrics)
        if all_achievements:
            db.session.commit()
        
        # Check level-specific achievements using pre-loaded data
        # Note: We still call the original method but it will benefit from composite indexes
        # For full optimization, we'd need to refactor check_level_specific_achievements
        # to accept pre-loaded data, but that's a larger refactoring
        level_achievements = AchievementService.check_level_specific_achievements(user)
        if level_achievements:
            db.session.commit()

        # Refresh achievements list
        achievements = (
            Achievement.query.filter_by(user_id=user.id)
            .order_by(Achievement.earned_at.desc())
            .all()
        )
        return achievements

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
        if not users:
            return {}
        
        user_ids = [user.id for user in users]
        
        # Batch load all achievements for all users at once
        all_achievements = (
            Achievement.query
            .filter(Achievement.user_id.in_(user_ids))
            .order_by(Achievement.user_id, Achievement.earned_at.desc())
            .all()
        )
        
        # Group achievements by user_id for quick lookup
        achievements_by_user: dict[int, list[Achievement]] = {}
        for achievement in all_achievements:
            if achievement.user_id not in achievements_by_user:
                achievements_by_user[achievement.user_id] = []
            achievements_by_user[achievement.user_id].append(achievement)
        
        # Batch load responses and sessions for all users to reduce queries
        # Group responses by user_id for quick lookup
        all_responses = (
            Response.query
            .filter(Response.user_id.in_(user_ids))
            .join(Question)
            .all()
        )
        responses_by_user: dict[int, list[Response]] = {}
        for response in all_responses:
            if response.user_id not in responses_by_user:
                responses_by_user[response.user_id] = []
            responses_by_user[response.user_id].append(response)
        
        # Batch load sessions for all users
        all_sessions = (
            PracticeSession.query
            .filter(PracticeSession.user_id.in_(user_ids))
            .all()
        )
        sessions_by_user: dict[int, list[PracticeSession]] = {}
        for session in all_sessions:
            if session.user_id not in sessions_by_user:
                sessions_by_user[session.user_id] = []
            sessions_by_user[session.user_id].append(session)
        
        # Process each user to ensure achievements are up to date
        # Use batch-loaded data to reduce database queries
        result: dict[int, list[Achievement]] = {}
        for user in users:
            metrics = all_metrics.get(user.id, {})
            user_responses = responses_by_user.get(user.id, [])
            user_sessions = sessions_by_user.get(user.id, [])
            
            # Check and award new achievements using batch-loaded data
            achievements = AchievementService._ensure_achievements_with_data(
                user, metrics, achievements_by_user.get(user.id, []), user_responses, user_sessions
            )
            result[user.id] = achievements
        
        return result

    @staticmethod
    @log_query
    def get_user_achievements(user_id: int, limit: int | None = None) -> list[Achievement]:
        """Get all achievements for a user."""
        # Validate and cleanup any incorrectly awarded tier achievements
        AchievementService.validate_and_cleanup_tier_achievements(user_id)
        
        query = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.earned_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    @log_query
    def get_achievements_by_session(session_id: int) -> list[Achievement]:
        """Get all achievements for a specific session using indexed session_id field.
        
        Args:
            session_id: The session ID to query achievements for
        
        Returns:
            List of achievements linked to the session, ordered by earned_at DESC
        """
        # Use indexed session_id field for optimal performance
        achievements = Achievement.query.filter_by(session_id=session_id).order_by(Achievement.earned_at.desc()).all()
        return achievements

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
        achievements = Achievement.query.filter_by(
            user_id=user_id,
            code=achievement_code
        ).order_by(Achievement.earned_at.desc()).all()
        return achievements

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
        # Validate and cleanup any incorrectly awarded tier achievements
        if user_id:
            AchievementService.validate_and_cleanup_tier_achievements(user_id)
        
        # Use JOIN with User table if we need user names (for all-users queries)
        # Use joinedload to eager load user relationship in a single query (avoids N+1)
        if include_user_name and not user_id:
            from sqlalchemy.orm import joinedload
            query = Achievement.query.options(joinedload(Achievement.user))
        else:
            query = Achievement.query

        if user_id:
            query = query.filter_by(user_id=user_id)

        if category:
            query = query.filter_by(category=category)

        # Order by indexed earned_at column for optimal performance
        # LIMIT is applied at SQL level, not in Python
        return query.order_by(Achievement.earned_at.desc()).limit(limit).all()

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
        achievements = Achievement.query.filter_by(user_id=user_id).all()
        return {a.code for a in achievements}

    @staticmethod
    def serialize_achievement(achievement: Achievement, user_name: str | None = None) -> dict[str, Any]:
        """Serialize an achievement to a dictionary.
        
        Args:
            achievement: The achievement object to serialize
            user_name: Optional user name to include in serialization
        """
        result = {
            "id": str(achievement.id),
            "code": achievement.code,
            "userId": achievement.user_id,
            "title": achievement.title,
            "description": achievement.description,
            "icon": achievement.icon,
            "category": achievement.category,
            "earnedAt": achievement.earned_at.isoformat(),
            "sessionId": achievement.session_id if achievement.session_id else None,
        }
        if achievement.achievement_metadata:
            try:
                result["metadata"] = json.loads(achievement.achievement_metadata)
            except (json.JSONDecodeError, TypeError):
                result["metadata"] = None
        if user_name:
            result["userName"] = user_name
        return result

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
        from ..models import Response, Question
        from ..services.session_engine_service import SessionEngineService
        
        new_achievements = []
        
        # If test_type is provided, check only that type
        test_types_to_check = [test_type] if test_type else []
        
        _debug_print(f"\n[ACHIEVEMENT DEBUG] check_consecutive_correct_achievements: User {user.id}, test_type={test_type}")
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking {len(test_types_to_check)} test types: {test_types_to_check}")
        
        for check_test_type in test_types_to_check:
            if not check_test_type:
                continue
                
            achievement_code = f"{check_test_type}_mastery"
            
            # Check if already earned
            existing = Achievement.query.filter_by(user_id=user.id, code=achievement_code).first()
            if existing:
                _debug_print(f"[ACHIEVEMENT DEBUG] Skipping {achievement_code} - already earned")
                continue
            
            _debug_print(f"[ACHIEVEMENT DEBUG] Checking {achievement_code}...")
            
            # Get test type configuration to determine level and operation
            operation = None
            required_level = None
            
            if check_test_type in SessionEngineService.TEST_TYPES:
                operation, required_level, _, _ = SessionEngineService.TEST_TYPES[check_test_type]
            else:
                # Unknown test type, skip
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Unknown test type: {check_test_type}")
                continue
            
            _debug_print(f"[ACHIEVEMENT DEBUG]   test_type={check_test_type}, operation={operation}, level={required_level}")
            
            # First, check if user has ANY responses for this test type (level + operation)
            # If they've never done questions for this type, skip it
            has_attempted = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(
                    Question.required_level == required_level,
                    Question.operation == operation
                )
                .first()
            )
            
            if not has_attempted:
                # User has never attempted this test type, skip
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ User has never attempted {operation} at level {required_level}, skipping")
                continue
            
            _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ User has attempted {operation} at level {required_level}")
            
            # Get recent responses for this specific test type (level + operation)
            # ordered by answered_at descending
            recent_responses = (
                Response.query.filter_by(user_id=user.id, is_correct=True)
                .join(Question)
                .filter(
                    Question.required_level == required_level,
                    Question.operation == operation
                )
                .order_by(Response.answered_at.desc())
                .limit(30)
                .all()
            )
            
            # Check if we have at least 30 consecutive correct answers for this test type
            if len(recent_responses) >= 30:
                # Verify they are consecutive (no gaps/incorrect answers in between)
                # Get the 30 most recent responses for this test type (including incorrect ones)
                all_recent = (
                    Response.query.filter_by(user_id=user.id)
                    .join(Question)
                    .filter(
                        Question.required_level == required_level,
                        Question.operation == operation
                    )
                    .order_by(Response.answered_at.desc())
                    .limit(30)
                    .all()
                )
                
                # Check if all 30 most recent for this test type are correct
                all_correct = all(r.is_correct for r in all_recent) if all_recent else False
                _debug_print(f"[ACHIEVEMENT DEBUG]   recent_responses={len(recent_responses)}, all_recent={len(all_recent)}, all_correct={all_correct}")
                
                if len(all_recent) == 30 and all_correct:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (30 consecutive correct for {operation} level {required_level})")
                    # Award achievement
                    with transaction():
                        achievement = Achievement(
                            user=user,
                            code=achievement_code,
                            title=f"{check_test_type.replace('_', ' ').title()} Mastery",
                            description="Answered 30 questions correctly in a row.",
                            icon="🏆",
                            category="mastery",
                            earned_at=datetime.utcnow(),
                        )
                        db.session.add(achievement)
                        new_achievements.append(achievement)
                else:
                    incorrect_count = sum(1 for r in all_recent if not r.is_correct) if all_recent else 0
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need 30 consecutive, have {len(all_recent)} total, {incorrect_count} incorrect)")
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = _get_achievement_configs()
        
        total_answers = metrics.get("questions_answered", 0)
        avg_speed = metrics.get("average_speed_seconds", 0.0)
        stats = metrics.get("operation_stats", {})
        current_streak = stats.get("currentStreak", 0)
        
        accuracy_candidates = [
            stats.get("additionAccuracy", 0),
            stats.get("subtractionAccuracy", 0),
            stats.get("multiplicationAccuracy", 0),
            stats.get("divisionAccuracy", 0),
        ]
        max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0
        
        # Group milestone achievements by type for tier-based awarding
        from ..utils.tier_utils import ALL_TIERS, get_tier_value
        
        question_master_achievements = []
        speed_demon_achievements = []
        week_warrior_achievements = []
        other_achievements = []
        
        for achievement_code, config in achievement_configs.items():
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            req_type = requirements.get("type")
            
            # Group tier-based milestone achievements
            if achievement_code.startswith("question-master-"):
                question_master_achievements.append((achievement_code, config))
            elif achievement_code.startswith("speed-demon-"):
                speed_demon_achievements.append((achievement_code, config))
            elif achievement_code.startswith("week-warrior-"):
                week_warrior_achievements.append((achievement_code, config))
            else:
                other_achievements.append((achievement_code, config))
        
        # Process question_master achievements (award highest tier only)
        if question_master_achievements:
            qualifying_tiers = []
            for achievement_code, config in question_master_achievements:
                requirements = config.get("requirements", {})
                min_questions = requirements.get("min_questions", 0)
                if total_answers >= min_questions:
                    tier = config.get("tier", "bronze")
                    qualifying_tiers.append((tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first)
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                if highest_tier == "divine":
                    champion_code = "question-master-champion"
                    champion_config = achievement_configs.get(champion_code)
                    if champion_config:
                        champion_req = champion_config.get("requirements", {})
                        if total_answers >= champion_req.get("min_questions", 0):
                            # Check server record
                            if AchievementService.checkChampionEligibility(champion_code, None, "champion", user, metrics):
                                achievement_code = champion_code
                                config = champion_config
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (question_master)")
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
        
        # Process speed_demon achievements (award highest tier only)
        if speed_demon_achievements and avg_speed > 0:
            qualifying_tiers = []
            for achievement_code, config in speed_demon_achievements:
                requirements = config.get("requirements", {})
                max_speed = requirements.get("max_speed_seconds", 999)
                min_questions = requirements.get("min_questions", 0)
                if avg_speed <= max_speed and total_answers >= min_questions:
                    tier = config.get("tier", "bronze")
                    qualifying_tiers.append((tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first)
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                if highest_tier == "divine":
                    champion_code = "speed-demon-champion"
                    champion_config = achievement_configs.get(champion_code)
                    if champion_config:
                        champion_req = champion_config.get("requirements", {})
                        if avg_speed <= champion_req.get("max_speed_seconds", 0.5):
                            # Check server record (would need session for this)
                            # For now, skip champion check for speed demon in global check
                            pass
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (speed_demon)")
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
        
        # Process week_warrior achievements (award highest tier only)
        if week_warrior_achievements:
            qualifying_tiers = []
            for achievement_code, config in week_warrior_achievements:
                requirements = config.get("requirements", {})
                min_streak = requirements.get("min_streak_days", 0)
                if current_streak >= min_streak:
                    tier = config.get("tier", "bronze")
                    qualifying_tiers.append((tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first)
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                if highest_tier == "divine":
                    champion_code = "week-warrior-champion"
                    champion_config = achievement_configs.get(champion_code)
                    if champion_config:
                        champion_req = champion_config.get("requirements", {})
                        if current_streak >= champion_req.get("min_streak_days", 0):
                            # Check server record
                            if AchievementService.checkChampionEligibility(champion_code, None, "champion", user, metrics):
                                achievement_code = champion_code
                                config = champion_config
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (week_warrior)")
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
        
        # Process other achievements (non-tier-based milestones and others)
        for achievement_code, config in other_achievements:
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
        
        return new_achievements

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
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        # Get all achievement configs (cached)
        achievement_configs = _get_achievement_configs()
        
        _debug_print(f"[ACHIEVEMENT DEBUG] check_level_specific_achievements: User {user.id} (level {user.level})")
        _debug_print(f"[ACHIEVEMENT DEBUG] Checking {len(achievement_configs)} achievement configs")
        _debug_print(f"[ACHIEVEMENT DEBUG] User already has {len(user_achievement_codes)} achievements: {sorted(user_achievement_codes)}")
        
        # Collect fast_session, fast_questions, and perfect_streak achievements separately to handle tier logic
        fast_session_achievements = []
        fast_questions_achievements = []
        perfect_streak_achievements = []
        other_achievements = []
        
        for achievement_code, config in achievement_configs.items():
            req_type = config.get("requirements", {}).get("type")
            if req_type == "fast_session":
                fast_session_achievements.append((achievement_code, config))
            elif req_type == "fast_questions":
                fast_questions_achievements.append((achievement_code, config))
            elif achievement_code.startswith("perfect-streak-"):
                perfect_streak_achievements.append((achievement_code, config))
            else:
                other_achievements.append((achievement_code, config))
        
        # Process fast_session achievements with tier logic (only award highest tier)
        if session_id and fast_session_achievements:
            current_session = PracticeSession.query.get(session_id)
            if current_session:
                db.session.refresh(current_session)
                
                if current_session.completed_at and current_session.total_questions >= 10:
                    total_duration_ms = current_session.total_duration_ms or 0
                    avg_time = (total_duration_ms / 1000.0 / current_session.total_questions) if current_session.total_questions > 0 else None
                    
                    if avg_time:
                        # Find all qualifying tiers
                        qualifying_tiers = []
                        for achievement_code, config in fast_session_achievements:
                            max_avg_time = config.get("requirements", {}).get("max_avg_time", 5.0)
                            min_questions = config.get("requirements", {}).get("min_questions", 10)
                            
                            if current_session.total_questions >= min_questions and avg_time < max_avg_time:
                                qualifying_tiers.append((achievement_code, config, max_avg_time))
                        
                        # Award only the highest tier (lowest max_avg_time = best performance)
                        if qualifying_tiers:
                            # Sort by max_avg_time ascending (lowest = best)
                            qualifying_tiers.sort(key=lambda x: x[2])
                            highest_tier_code, highest_tier_config, _ = qualifying_tiers[0]
                            
                            achievement = AchievementService.create_achievement(
                                user_id=user.id,
                                code=highest_tier_code,
                                title=highest_tier_config["title"],
                                description=highest_tier_config["description"],
                                icon=highest_tier_config["icon"],
                                category=highest_tier_config["category"],
                                session_id=session_id,
                            )
                            new_achievements.append(achievement)
                            print(f"[ACHIEVEMENT INFO] Awarding '{highest_tier_config['title']}' ({highest_tier_code}) to user {user.id} for session {session_id} - avg time: {avg_time:.2f}s")
        
        # Process fast_questions achievements with tier logic (only award highest tier)
        if session_id and fast_questions_achievements:
            # Build query - filter by session_id
            recent_responses_query = Response.query.filter_by(user_id=user.id, session_id=session_id)
            
            # Find all qualifying tiers
            qualifying_tiers = []
            for achievement_code, config in fast_questions_achievements:
                max_avg_time = config.get("requirements", {}).get("max_avg_time", 4.0)
                consecutive_count = config.get("requirements", {}).get("consecutive_count", 10)
                
                # Get most recent responses (limit to highest consecutive_count needed)
                max_consecutive = max(cfg.get("requirements", {}).get("consecutive_count", 10) for _, cfg in fast_questions_achievements)
                recent_responses = (
                    recent_responses_query
                    .order_by(Response.answered_at.desc())
                    .limit(max_consecutive)
                    .all()
                )
                
                # Require EXACT count match
                if len(recent_responses) >= consecutive_count:
                    # Take exactly the required number
                    responses_for_tier = recent_responses[:consecutive_count]
                    total_time = sum(r.duration_ms or 0 for r in responses_for_tier)
                    avg_time = (total_time / 1000.0 / len(responses_for_tier)) if responses_for_tier else None
                    
                    if avg_time and avg_time < max_avg_time:
                        qualifying_tiers.append((achievement_code, config, consecutive_count))
            
            # Award only the highest tier (highest consecutive_count = best performance)
            if qualifying_tiers:
                # Sort by consecutive_count descending (highest = best)
                qualifying_tiers.sort(key=lambda x: x[2], reverse=True)
                highest_tier_code, highest_tier_config, highest_count = qualifying_tiers[0]
                
                # Get responses for the highest tier
                recent_responses = (
                    recent_responses_query
                    .order_by(Response.answered_at.desc())
                    .limit(highest_count)
                    .all()
                )
                if len(recent_responses) == highest_count:
                    achievement = AchievementService.create_achievement(
                        user_id=user.id,
                        code=highest_tier_code,
                        title=highest_tier_config["title"],
                        description=highest_tier_config["description"],
                        icon=highest_tier_config["icon"],
                        category=highest_tier_config["category"],
                        session_id=session_id,
                    )
                    new_achievements.append(achievement)
        
        # Process perfect_streak achievements with tier logic (only award highest tier)
        if perfect_streak_achievements:
            # Get all completed sessions ordered by completion time
            all_sessions = (
                PracticeSession.query.filter_by(user_id=user.id)
                .filter(PracticeSession.completed_at.isnot(None))
                .order_by(PracticeSession.completed_at.desc())
                .all()
            )
            
            # Count consecutive perfect sessions (100% accuracy)
            consecutive_perfect = 0
            for session in all_sessions:
                if session.accuracy == 100.0:
                    consecutive_perfect += 1
                else:
                    break  # Break on first non-perfect session
            
            # Find all qualifying tiers
            qualifying_tiers = []
            for achievement_code, config in perfect_streak_achievements:
                if achievement_code in user_achievement_codes:
                    continue
                
                requirements = config.get("requirements", {})
                min_sessions = requirements.get("min_sessions", 0)
                if consecutive_perfect >= min_sessions:
                    tier = config.get("tier", "bronze")
                    qualifying_tiers.append((tier, achievement_code, config))
            
            if qualifying_tiers:
                # Sort by tier value (highest first)
                from ..utils.tier_utils import get_tier_value
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config = qualifying_tiers[0]
                
                # Check for Champion tier if this is Divine
                if highest_tier == "divine":
                    champion_code = "perfect-streak-champion"
                    champion_config = achievement_configs.get(champion_code)
                    if champion_config:
                        champion_req = champion_config.get("requirements", {})
                        if consecutive_perfect >= champion_req.get("min_sessions", 0):
                            # Check server record (need to get user and metrics)
                            # For perfect streak, we calculate from sessions, so pass user
                            if AchievementService.checkChampionEligibility(champion_code, None, "champion", user, None):
                                achievement_code = champion_code
                                config = champion_config
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (perfect_streak: {consecutive_perfect} sessions)")
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
        
        # Process other achievements (non-tiered)
        for achievement_code, config in other_achievements:
            # Skip if already earned (unless it's a session-specific achievement that can be earned multiple times)
            # Session-specific achievements (fast_session, fast_questions) can be earned per session
            requirements = config.get("requirements", {})
            req_type = requirements.get("type")
            is_session_specific = req_type in ["fast_session", "fast_questions"]
            
            # For session-specific achievements, we'll check them even if already earned
            # (they can be awarded multiple times, once per qualifying session)
            if achievement_code in user_achievement_codes and not is_session_specific:
                continue
            
            _debug_print(f"[ACHIEVEMENT DEBUG] Checking achievement: {achievement_code} - {config.get('title')}")
            
            requirements = config.get("requirements", {})
            req_type = requirements.get("type")
            
            # Check operation_count achievements
            if req_type == "operation_count":
                operation = requirements.get("operation")
                count = requirements.get("count", 0)
                level = requirements.get("level")
                
                # Count correct answers for this operation at this level
                correct_count = (
                    db.session.query(func.count())
                    .select_from(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Response.is_correct == True,
                        Question.operation == operation,
                        Question.required_level == level,
                    )
                    .scalar()
                    or 0
                )
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   operation_count: operation={operation}, level={level}, required={count}, actual={correct_count}")
                
                if correct_count >= count:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (operation_count: {correct_count} >= {count})")
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
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {count}, have {correct_count})")
            
            # Check level_accuracy achievements
            elif req_type == "level_accuracy":
                level = requirements.get("level")
                min_accuracy = requirements.get("min_accuracy", 0.0)
                min_questions = requirements.get("min_questions", 0)
                max_questions = requirements.get("max_questions")
                max_speed = requirements.get("max_speed")
                operation_filter = requirements.get("operation")
                
                # Build query filter
                query_filter = [
                    Response.user_id == user.id,
                    Question.required_level == level,
                ]
                
                # Add operation filter if specified
                if operation_filter:
                    query_filter.append(Question.operation == operation_filter)
                
                # Get all responses for this level (and operation if specified)
                responses = (
                    db.session.query(Response)
                    .join(Question)
                    .filter(*query_filter)
                    .all()
                )
                
                total_responses = len(responses)
                correct_count = sum(1 for r in responses if r.is_correct) if responses else 0
                accuracy = correct_count / total_responses if total_responses > 0 else 0.0
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   level_accuracy: level={level}, operation={operation_filter}, required_accuracy={min_accuracy}, required_questions={min_questions}")
                _debug_print(f"[ACHIEVEMENT DEBUG]   actual: total={total_responses}, correct={correct_count}, accuracy={accuracy:.2%}")
                
                meets_requirements = True
                
                # Check question count requirements
                if total_responses < min_questions:
                    meets_requirements = False
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (questions {total_responses} < {min_questions})")
                elif max_questions and total_responses > max_questions:
                    meets_requirements = False
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (questions {total_responses} > {max_questions})")
                
                # Check accuracy requirement
                if meets_requirements and accuracy < min_accuracy:
                    meets_requirements = False
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (accuracy {accuracy:.2%} < {min_accuracy:.2%})")
                
                # Check speed requirement (if specified, calculate from session)
                if meets_requirements and max_speed:
                    # For level_accuracy achievements checked globally, speed check is optional
                    # This is mainly handled by session-based checking in check_generic_accuracy_achievements
                    # We skip speed check here as we don't have session context
                    pass
                
                if meets_requirements:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (accuracy: {accuracy:.2%} >= {min_accuracy:.2%}, questions: {total_responses} >= {min_questions})")
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
            
            # Check level_correct_count achievements
            elif req_type == "level_correct_count":
                level = requirements.get("level")
                min_correct = requirements.get("min_correct", 0)
                
                # Count correct answers for this level
                correct_count = (
                    db.session.query(func.count())
                    .select_from(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Response.is_correct == True,
                        Question.required_level == level,
                    )
                    .scalar()
                    or 0
                )
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   level_correct_count: level={level}, required={min_correct}, actual={correct_count}")
                
                if correct_count >= min_correct:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (correct_count: {correct_count} >= {min_correct})")
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
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_correct}, have {correct_count})")
            
            # Check session_accuracy_and_consecutive achievements
            elif req_type == "session_accuracy_and_consecutive":
                min_sessions = requirements.get("min_sessions", 0)
                min_session_accuracy = requirements.get("min_session_accuracy", 0.0)
                level = requirements.get("level")
                consecutive_correct = requirements.get("consecutive_correct", 0)
                
                # Count sessions with required accuracy
                sessions = (
                    PracticeSession.query.filter_by(
                        user_id=user.id,
                    )
                    .filter(
                        PracticeSession.completed_at.isnot(None),
                        PracticeSession.accuracy >= (min_session_accuracy * 100),  # accuracy is stored as percentage
                    )
                    .all()
                )
                
                session_count = len(sessions)
                
                # Check for consecutive correct answers at the specified level
                # Get the most recent responses for this level
                recent_responses = (
                    Response.query.filter_by(user_id=user.id, is_correct=True)
                    .join(Question)
                    .filter(Question.required_level == level)
                    .order_by(Response.answered_at.desc())
                    .limit(consecutive_correct)
                    .all()
                )
                
                # Check if we have enough consecutive correct
                has_consecutive = False
                if len(recent_responses) >= consecutive_correct:
                    # Get all recent responses (including incorrect) to verify they're truly consecutive
                    all_recent = (
                        Response.query.filter_by(user_id=user.id)
                        .join(Question)
                        .filter(Question.required_level == level)
                        .order_by(Response.answered_at.desc())
                        .limit(consecutive_correct)
                        .all()
                    )
                    
                    # Check if all most recent responses are correct
                    if len(all_recent) == consecutive_correct:
                        has_consecutive = all(r.is_correct for r in all_recent)
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   session_accuracy_and_consecutive: sessions={session_count} (need {min_sessions}), accuracy>={min_session_accuracy:.0%}, consecutive={has_consecutive} (need {consecutive_correct} at level {level})")
                
                if session_count >= min_sessions and has_consecutive:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (sessions: {session_count}/{min_sessions}, consecutive: {has_consecutive})")
            
            # Check test_completion achievements
            elif req_type == "test_completion":
                test_type = requirements.get("test_type")
                min_accuracy = requirements.get("min_accuracy", 0.0)
                question_count = requirements.get("question_count", 0)
                
                # Find completed test sessions for this test type
                sessions = (
                    PracticeSession.query.filter_by(
                        user_id=user.id,
                        is_test=True,
                        test_type=test_type,
                    )
                    .filter(PracticeSession.completed_at.isnot(None))
                    .all()
                )
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   test_completion: test_type={test_type}, required_accuracy={min_accuracy}, required_questions={question_count}")
                _debug_print(f"[ACHIEVEMENT DEBUG]   found {len(sessions)} completed test session(s) for this test type")
                
                for session in sessions:
                    if session.total_questions >= question_count:
                        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0
                        _debug_print(f"[ACHIEVEMENT DEBUG]   session {session.id}: questions={session.total_questions}, accuracy={accuracy:.2%}")
                        if accuracy >= min_accuracy:
                            _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (test_completion: accuracy {accuracy:.2%} >= {min_accuracy:.2%})")
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
                            break  # Only award once
                        else:
                            _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (accuracy {accuracy:.2%} < {min_accuracy:.2%})")
                    else:
                        _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (questions {session.total_questions} < {question_count})")
            
            # Check perfect_sessions achievements (legacy non-tier-based only, tier-based handled above)
            elif req_type == "perfect_sessions":
                # Skip perfect-streak-* achievements as they're handled above
                if achievement_code.startswith("perfect-streak-"):
                    continue
                
                min_sessions = requirements.get("min_sessions", 0)
                
                # Get all completed sessions ordered by completion time
                all_sessions = (
                    PracticeSession.query.filter_by(user_id=user.id)
                    .filter(PracticeSession.completed_at.isnot(None))
                    .order_by(PracticeSession.completed_at.desc())
                    .all()
                )
                
                # Count consecutive perfect sessions (100% accuracy)
                consecutive_perfect = 0
                for session in all_sessions:
                    if session.accuracy == 100.0:
                        consecutive_perfect += 1
                    else:
                        break  # Break on first non-perfect session
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   perfect_sessions: required={min_sessions}, consecutive={consecutive_perfect}")
                
                if consecutive_perfect >= min_sessions:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_sessions}, have {consecutive_perfect})")
            
            # Check basic_math_test achievement
            elif req_type == "basic_math_test":
                max_level = requirements.get("max_level", 4)
                question_count = requirements.get("question_count", 50)
                min_accuracy = requirements.get("min_accuracy", 0.80)
                
                # Find test sessions covering levels 1-4
                test_sessions = (
                    PracticeSession.query.filter_by(user_id=user.id, is_test=True)
                    .filter(PracticeSession.completed_at.isnot(None))
                    .all()
                )
                
                # Check if any test session meets the requirements
                for session in test_sessions:
                    if session.total_questions >= question_count:
                        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0
                        if accuracy >= min_accuracy:
                            # Check if session covers levels 1-4
                            session_questions = (
                                Question.query.join(Response)
                                .filter(Response.session_id == session.id)
                                .all()
                            )
                            levels_covered = set(q.required_level for q in session_questions)
                            if all(level <= max_level for level in levels_covered):
                                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
                                break
            
            # Check level_mastery achievements
            elif req_type == "level_mastery":
                level = requirements.get("level")
                min_accuracy = requirements.get("min_accuracy", 0.0)
                min_questions = requirements.get("min_questions", 0)
                consecutive_correct = requirements.get("consecutive_correct", 0)
                
                # Get all responses for this level
                responses = (
                    db.session.query(Response)
                    .join(Question)
                    .filter(
                        Response.user_id == user.id,
                        Question.required_level == level,
                    )
                    .all()
                )
                
                total_responses = len(responses)
                correct_count = sum(1 for r in responses if r.is_correct) if responses else 0
                accuracy = correct_count / total_responses if total_responses > 0 else 0.0
                
                # Check for consecutive correct answers
                recent_responses = (
                    Response.query.filter_by(user_id=user.id)
                    .join(Question)
                    .filter(Question.required_level == level)
                    .order_by(Response.answered_at.desc())
                    .limit(consecutive_correct)
                    .all()
                )
                
                has_consecutive = False
                if len(recent_responses) >= consecutive_correct:
                    has_consecutive = all(r.is_correct for r in recent_responses)
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   level_mastery: level={level}, accuracy={accuracy:.2%} (need {min_accuracy:.2%}), questions={total_responses} (need {min_questions}), consecutive={has_consecutive} (need {consecutive_correct})")
                
                if total_responses >= min_questions and accuracy >= min_accuracy and has_consecutive:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding")
            
            # Check test_tier achievements (for Rank A multiplication tests)
            elif req_type == "test_tier":
                test_type = requirements.get("test_type")
                tier = requirements.get("tier", "").lower()
                min_accuracy = requirements.get("min_accuracy", 100)
                max_question_count = requirements.get("max_question_count", 29)
                
                # Find completed test sessions for this test type
                sessions = (
                    PracticeSession.query.filter_by(
                        user_id=user.id,
                        is_test=True,
                        test_type=test_type,
                    )
                    .filter(PracticeSession.completed_at.isnot(None))
                    .all()
                )
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   test_tier: test_type={test_type}, tier={tier}, required_accuracy={min_accuracy}, max_questions={max_question_count}")
                
                for session in sessions:
                    if session.accuracy >= min_accuracy and session.total_questions <= max_question_count:
                        _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
                        break
            
            # Check multiplication_tests_s_rank achievement
            elif req_type == "multiplication_tests_s_rank":
                test_types = requirements.get("test_types", [])
                tier = requirements.get("tier", "s").lower()
                
                # Check if user has S rank on all specified test types
                all_have_s_rank = True
                for test_type in test_types:
                    # Find best session for this test type
                    sessions = (
                        PracticeSession.query.filter_by(
                            user_id=user.id,
                            is_test=True,
                            test_type=test_type,
                        )
                        .filter(PracticeSession.completed_at.isnot(None))
                        .all()
                    )
                    
                    has_s_rank = False
                    for session in sessions:
                        # S rank: 100% accuracy, 31-59 questions, <6s/question
                        if session.accuracy == 100.0:
                            if 31 <= session.total_questions <= 59:
                                total_duration_ms = session.total_duration_ms or 0
                                avg_time = (total_duration_ms / 1000.0 / session.total_questions) if session.total_questions > 0 else None
                                if avg_time and avg_time < 6.0:
                                    has_s_rank = True
                                    break
                    
                    if not has_s_rank:
                        all_have_s_rank = False
                        break
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   multiplication_tests_s_rank: all_have_s_rank={all_have_s_rank}")
                
                if all_have_s_rank:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
            
            # Check achievement_count_by_category achievements
            elif req_type == "achievement_count_by_category":
                category = requirements.get("category")
                min_level = requirements.get("min_level", 1)
                max_level = requirements.get("max_level", None)
                min_tier = requirements.get("min_tier", "bronze")
                min_count = requirements.get("min_count", 0)
                
                # Get user's achievements matching the category and tier
                user_achievements = Achievement.query.filter_by(user_id=user.id).all()
                
                # Map tier names to hierarchy
                tier_hierarchy = {
                    "bronze": 1,
                    "silver": 2,
                    "gold": 3,
                    "platinum": 4,
                    "diamond": 5,
                    "champion": 6,
                    "b": 1,
                    "a": 2,
                    "s": 3,
                    "ss": 4,
                    "sss": 5,
                }
                
                min_tier_value = tier_hierarchy.get(min_tier.lower(), 1)
                
                # Handle special category "addition_subtraction" which means either addition or subtraction
                if category == "addition_subtraction":
                    matching_categories = ["addition", "subtraction", "progression", "accuracy"]  # progression includes mixed operations
                elif category == "addition":
                    matching_categories = ["addition", "progression", "accuracy"]
                elif category == "subtraction":
                    matching_categories = ["subtraction", "progression", "accuracy"]
                else:
                    matching_categories = [category]
                
                matching_count = 0
                for ach in user_achievements:
                    # Check category
                    if ach.category not in matching_categories:
                        continue
                    
                    code_lower = ach.code.lower()
                    
                    # For addition category, check if achievement is addition-related
                    if category == "addition":
                        if not any(op in code_lower for op in ["addition", "add", "mixed-addition", "double-addition", "triple-addition"]):
                            continue
                        # For basic addition (1-digit), check if it's level 1 related
                        if min_level == 1 and max_level == 1:
                            if "basics" not in code_lower and "1digit" not in code_lower and "level-1" not in code_lower:
                                continue
                    
                    # For subtraction category, check if achievement is subtraction-related
                    elif category == "subtraction":
                        if not any(op in code_lower for op in ["subtraction", "subtract", "mixed-subtraction", "double-subtraction", "triple-subtraction"]):
                            continue
                        # For basic subtraction (1-digit), check if it's level 1 related
                        if min_level == 1 and max_level == 1:
                            if "basics" not in code_lower and "1digit" not in code_lower and "level-3" not in code_lower:
                                continue
                    
                    # For addition_subtraction, skip achievements that are clearly not addition/subtraction related
                    elif category == "addition_subtraction":
                        # Skip multiplication, division, and other non-addition/subtraction achievements
                        if ach.category in ["test", "speed", "consistency"]:
                            # Check if code suggests it's addition/subtraction related
                            if not any(op in code_lower for op in ["addition", "subtraction", "add", "subtract", "mixed", "double", "triple"]):
                                continue
                        # For advanced (outside basic 1-digit), skip level 1 achievements
                        if min_level == 2:
                            if any(level in code_lower for level in ["basics", "1digit", "level-1", "level-3"]):
                                continue
                    
                    # Check tier (extract from code or use category)
                    ach_tier = "bronze"  # default
                    if ach.code.endswith("-sss"):
                        ach_tier = "sss"
                    elif ach.code.endswith("-ss"):
                        ach_tier = "ss"
                    elif ach.code.endswith("-s") and not ach.code.endswith("-ss"):
                        ach_tier = "s"
                    elif ach.code.endswith("-a"):
                        ach_tier = "a"
                    elif ach.code.endswith("-b"):
                        ach_tier = "b"
                    # Check for tier in code (e.g., "fast-session-gold")
                    elif "-gold" in ach.code:
                        ach_tier = "gold"
                    elif "-platinum" in ach.code:
                        ach_tier = "platinum"
                    elif "-diamond" in ach.code:
                        ach_tier = "diamond"
                    elif "-champion" in ach.code:
                        ach_tier = "champion"
                    elif "-silver" in ach.code:
                        ach_tier = "silver"
                    elif "-bronze" in ach.code:
                        ach_tier = "bronze"
                    
                    ach_tier_value = tier_hierarchy.get(ach_tier.lower(), 1)
                    if ach_tier_value >= min_tier_value:
                        matching_count += 1
                
                _debug_print(f"[ACHIEVEMENT DEBUG]   achievement_count_by_category: category={category}, min_tier={min_tier}, required={min_count}, actual={matching_count}")
                
                if matching_count >= min_count:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
            
            # fast_session and fast_questions achievements are now handled separately above
            # (before this loop) to implement tier logic (only award highest tier)
            elif req_type in ["fast_session", "fast_questions"]:
                # Skip - already processed above
                continue
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
        from ..models import PracticeSession
        
        # Get all tiered test achievements for this user
        # Pattern: {test_type}-{tier} where tier is b, a, s, ss, or sss
        tier_achievements = (
            Achievement.query.filter_by(user_id=user_id, category="test")
            .filter(Achievement.code.like("%-b") | Achievement.code.like("%-a") | 
                   Achievement.code.like("%-s") | Achievement.code.like("%-ss") |
                   Achievement.code.like("%-sss"))
            .all()
        )
        
        removed_count = 0
        test_type_mapping = {
            "addition_1digit": "addition-1digit",
            "addition_2digit": "addition-2digit",
            "addition_3digit": "addition-3digit",
            "subtraction_1digit": "subtraction-1digit",
            "subtraction_2digit": "subtraction-2digit",
            "subtraction_3digit": "subtraction-3digit",
            "multiplication_2digit": "multiplication-2digit",
            "multiplication_3digit": "multiplication-3digit",
            "division_1digit": "division-1digit",
        }
        
        for achievement in tier_achievements:
            # Parse the achievement code to get test type and tier
            # Format: {frontend_test_type}-{tier}
            code_parts = achievement.code.rsplit("-", 1)
            if len(code_parts) != 2:
                continue
            
            frontend_test_type, tier_suffix = code_parts
            
            # Find the backend test_type that matches this frontend type
            backend_test_type = None
            for backend_type, frontend_type in test_type_mapping.items():
                if frontend_type == frontend_test_type:
                    backend_test_type = backend_type
                    break
            
            if not backend_test_type:
                continue
            
            # Find all sessions for this test type to check if any meet the requirements
            sessions = (
                PracticeSession.query.filter_by(
                    user_id=user_id,
                    is_test=True,
                    test_type=backend_test_type,
                )
                .filter(PracticeSession.completed_at.isnot(None))
                .order_by(PracticeSession.completed_at.desc())
                .all()
            )
            
            if not sessions:
                # No sessions found, remove the achievement
                with transaction():
                    db.session.delete(achievement)
                    removed_count += 1
                continue
            
            # Define tier requirements
            tier_requirements = {
                "sss": {
                    "min_accuracy": 100,
                    "question_count": 100,
                    "max_speed": 2,
                },
                "ss": {
                    "min_accuracy": 100,
                    "max_question_count": 90,
                    "max_speed": 4,
                },
                "s": {
                    "min_accuracy": 100,
                    "min_question_count": 31,
                    "max_question_count": 59,
                    "max_speed": 6,
                },
                "a": {
                    "min_accuracy": 100,
                    "max_question_count": 29,
                },
                "b": {
                    "min_question_count": 30,
                },
            }
            
            req = tier_requirements.get(tier_suffix)
            if not req:
                continue
            
            # Check if any session meets the tier requirements
            found_valid_session = False
            for session in sessions:
                total_questions = session.total_questions
                accuracy = session.accuracy
                total_duration_ms = session.total_duration_ms or 0
                avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
                
                meets_requirements = True
                
                # Check accuracy
                if "min_accuracy" in req and accuracy < req["min_accuracy"]:
                    meets_requirements = False
                
                # Check question counts
                if "min_question_count" in req and total_questions < req["min_question_count"]:
                    meets_requirements = False
                if "max_question_count" in req and total_questions > req["max_question_count"]:
                    meets_requirements = False
                if "question_count" in req and total_questions != req["question_count"]:
                    meets_requirements = False
                
                # Check speed
                if "max_speed" in req:
                    if avg_time_per_question is None:
                        meets_requirements = False
                    elif avg_time_per_question >= req["max_speed"]:
                        meets_requirements = False
                
                if meets_requirements:
                    found_valid_session = True
                    break
            
            # If no session meets the requirements, remove the achievement
            if not found_valid_session:
                with transaction():
                    db.session.delete(achievement)
                    removed_count += 1
        
        if removed_count > 0:
            db.session.commit()
        
        return removed_count

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
        return Achievement.query.filter_by(
            user_id=user_id,
            code=achievement_code
        ).count()

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
        from ..utils.tier_utils import (
            extract_base_code_and_tier,
            convert_tier_to_base_units,
            TIER_HIERARCHY,
        )
        
        # Extract base code and target tier
        base_code, target_tier = extract_base_code_and_tier(achievement_code)
        
        # Build query for all achievements with same base code (all tiers)
        # Match codes like "speed-demon-bronze", "speed-demon-silver", etc.
        if target_tier:
            # Use LIKE pattern to match base code with any tier
            code_pattern = f"{base_code}-%"
            query = Achievement.query.filter(
                Achievement.user_id == user_id,
                Achievement.code.like(code_pattern)
            )
        else:
            # No tier in code, just match exactly
            query = Achievement.query.filter_by(
                user_id=user_id,
                code=achievement_code
            )
        
        # Filter by metadata if provided
        if metadata_filter:
            metadata_json = json.dumps(metadata_filter, sort_keys=True)
            query = query.filter(Achievement.achievement_metadata == metadata_json)
        else:
            # If no metadata filter, only count achievements without metadata (global achievements)
            # This maintains backward compatibility
            query = query.filter(
                (Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == "")
            )
        
        # If we have other filters, we need to join with PracticeSession
        if level is not None or min_accuracy is not None or operation is not None:
            query = query.join(PracticeSession, Achievement.session_id == PracticeSession.id)
            
            # Filter by session level (deprecated, but kept for backward compatibility)
            if level is not None:
                query = query.filter(PracticeSession.level == level)
            
            # Filter by session accuracy (stored as percentage 0-100)
            if min_accuracy is not None:
                # min_accuracy is passed as 0.0-1.0, convert to percentage
                min_accuracy_percent = min_accuracy * 100.0
                query = query.filter(PracticeSession.accuracy >= min_accuracy_percent)
            
            # Filter by operation (need to check if session has questions with this operation)
            if operation is not None:
                # Join with Response and Question to check operation
                query = (
                    query.join(Response, PracticeSession.id == Response.session_id)
                    .join(Question, Response.question_id == Question.id)
                    .filter(Question.operation == operation)
                    .distinct()  # Avoid counting same achievement multiple times if multiple questions match
                )
        
        # Get all matching achievements
        achievements = query.all()
        
        # If no tier substitution needed (no tier in target code), just return count
        if not target_tier:
            return len(achievements)
        
        # Convert all matching achievements to bronze units, then to target tier
        total_bronze_units = 0
        target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1)
        
        for ach in achievements:
            _, ach_tier = extract_base_code_and_tier(ach.code)
            if ach_tier:
                # Convert this achievement to bronze units
                total_bronze_units += convert_tier_to_base_units(ach_tier, 1)
        
        # Convert total bronze units to target tier count
        # Each tier is worth 2^(tier_value - 1) bronze units
        bronze_units_per_target = 2 ** (target_tier_value - 1) if target_tier_value > 1 else 1
        equivalent_count = total_bronze_units // bronze_units_per_target
        
        return equivalent_count

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
        # Base query: achievements matching test type pattern
        # Match codes like "addition-1digit-bronze", "addition-1digit-silver", etc.
        query = Achievement.query.filter(
            Achievement.user_id == user_id,
            Achievement.code.like(f"{test_type}-%")
        )
        
        # If we have filters, we need to join with PracticeSession
        if level is not None or min_accuracy is not None or operation is not None:
            query = query.join(PracticeSession, Achievement.session_id == PracticeSession.id)
            
            # Filter by session level
            if level is not None:
                query = query.filter(PracticeSession.level == level)
            
            # Filter by session accuracy (stored as percentage 0-100)
            if min_accuracy is not None:
                # min_accuracy is passed as 0.0-1.0, convert to percentage
                min_accuracy_percent = min_accuracy * 100.0
                query = query.filter(PracticeSession.accuracy >= min_accuracy_percent)
            
            # Filter by operation (need to check if session has questions with this operation)
            if operation is not None:
                # Join with Response and Question to check operation
                query = (
                    query.join(Response, PracticeSession.id == Response.session_id)
                    .join(Question, Response.question_id == Question.id)
                    .filter(Question.operation == operation)
                    .distinct()  # Avoid counting same achievement multiple times if multiple questions match
                )
        
        return query.count()

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
        from ..utils.tier_utils import ALL_TIERS, get_tier_value
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = _get_achievement_configs()
        
        # Get all distinct levels from questions
        all_levels = [
            row[0] for row in
            db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]
        
        if not all_levels:
            return new_achievements
        
        _debug_print(f"\n[ACHIEVEMENT DEBUG] check_level_master_achievements: User {user.id}, levels={all_levels}")
        
        # Tier requirements
        tier_requirements = {
            "bronze": 30,
            "silver": 60,
            "gold": 120,
            "platinum": 240,
            "diamond": 480,
            "master": 960,
            "grandmaster": 1920,
            "legendary": 3840,
            "mythic": 7680,
            "divine": 15360,
            "champion": 15360,  # Same as divine, requires server record
        }
        
        # Track maximum consecutive correct at any level
        max_consecutive_any_level = 0
        # Track which levels have achieved bronze threshold (for Level Grandmaster)
        levels_with_bronze = set()
        
        # Check each level
        for target_level in all_levels:
            _debug_print(f"[ACHIEVEMENT DEBUG] Checking level {target_level}...")
            
            # Get all responses for this level, ordered chronologically
            level_responses = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(Question.required_level == target_level)
                .order_by(Response.answered_at.asc())
                .all()
            )
            
            if not level_responses:
                _debug_print(f"[ACHIEVEMENT DEBUG]   No responses at level {target_level}, skipping")
                continue
            
            # Calculate maximum consecutive correct count for this level
            max_consecutive = 0
            current_consecutive = 0
            
            for response in level_responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            _debug_print(f"[ACHIEVEMENT DEBUG]   Level {target_level}: max_consecutive={max_consecutive}")
            
            # Track maximum across all levels
            max_consecutive_any_level = max(max_consecutive_any_level, max_consecutive)
            
            # Track if this level has achieved bronze threshold
            if max_consecutive >= tier_requirements.get("bronze", 30):
                levels_with_bronze.add(target_level)
        
        _debug_print(f"[ACHIEVEMENT DEBUG]   Max consecutive at any level: {max_consecutive_any_level}")
        _debug_print(f"[ACHIEVEMENT DEBUG]   Levels with bronze threshold: {levels_with_bronze}")
        
        # Check Level Master achievements per level (with metadata)
        # Get existing level-master achievements with metadata to check what's already been awarded
        existing_level_master = Achievement.query.filter_by(user_id=user.id).filter(
            Achievement.code.like("level-master-%")
        ).all()
        
        # Build a map of level -> existing achievements for that level
        level_achievements_map: dict[int, list[Achievement]] = {}
        for ach in existing_level_master:
            if ach.achievement_metadata:
                try:
                    metadata_dict = json.loads(ach.achievement_metadata)
                    level = metadata_dict.get("level")
                    if level is not None:
                        if level not in level_achievements_map:
                            level_achievements_map[level] = []
                        level_achievements_map[level].append(ach)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Check each level separately
        for target_level in all_levels:
            # Get max consecutive for this level (already calculated above)
            level_responses = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(Question.required_level == target_level)
                .order_by(Response.answered_at.asc())
                .all()
            )
            
            if not level_responses:
                continue
            
            # Calculate max consecutive for this level
            max_consecutive = 0
            current_consecutive = 0
            for response in level_responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            # Get existing achievements for this level
            existing_for_level = level_achievements_map.get(target_level, [])
            existing_tiers = {ach.code.split("-")[-1] for ach in existing_for_level}
            
            # Find highest qualifying tier for this level
            qualifying_tiers = []
            for tier in ALL_TIERS:
                achievement_code = f"level-master-{tier}"
                config = achievement_configs.get(achievement_code)
                if not config:
                    continue
                
                requirements = config.get("requirements", {})
                min_consecutive = requirements.get("min_consecutive", 30)
                
                # Check if this tier is already awarded for this level
                if achievement_code in existing_tiers:
                    continue
                
                # Check if max_consecutive meets the requirement
                if max_consecutive >= min_consecutive:
                    qualifying_tiers.append((tier, achievement_code, config, min_consecutive))
            
            if qualifying_tiers:
                # Sort by tier value (highest first) and award the highest tier
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config, min_consecutive_req = qualifying_tiers[0]
                
                # Important: Don't award multiple for same streak
                # If user has bronze for 30, and now has 35, don't award another bronze
                # Only award if they've reached a NEW tier threshold
                # Check if there's a lower tier already awarded that would prevent this
                should_award = True
                for existing_ach in existing_for_level:
                    existing_tier = existing_ach.code.split("-")[-1]
                    existing_tier_value = get_tier_value(existing_tier)
                    new_tier_value = get_tier_value(highest_tier)
                    
                    # If we're trying to award the same tier, don't award
                    if existing_tier == highest_tier:
                        should_award = False
                        break
                    
                    # If we're trying to award a lower tier than what's already awarded, don't award
                    if new_tier_value < existing_tier_value:
                        should_award = False
                        break
                
                if should_award:
                    # Check for Champion tier if this is Divine
                    if highest_tier == "divine":
                        champion_code = "level-master-champion"
                        champion_config = achievement_configs.get(champion_code)
                        if champion_config:
                            # Check if champion already exists for this level
                            champion_exists = any(
                                ach.code == champion_code for ach in existing_for_level
                            )
                            if not champion_exists:
                                # Champion tier can be checked during session completion
                                pass
                    
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} with metadata level={target_level} ({max_consecutive} consecutive correct at level {target_level})")
                    achievement = AchievementService.create_achievement(
                        user_id=user.id,
                        code=achievement_code,
                        title=config["title"],
                        description=config["description"],
                        icon=config["icon"],
                        category=config["category"],
                        metadata={"level": target_level},
                    )
                    new_achievements.append(achievement)
        
        # Store levels_with_bronze in a way that can be checked for Level Grandmaster
        # We'll check this in the Level Grandmaster method
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
        from ..utils.tier_utils import ALL_TIERS, get_tier_value
        
        new_achievements = []
        achievement_configs = _get_achievement_configs()
        
        # Get session if provided
        session = None
        if session_id:
            session = PracticeSession.query.get(session_id)
            if not session or not session.completed_at:
                return []
        
        # Get all distinct levels from questions
        all_levels = [
            row[0] for row in
            db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]
        
        if not all_levels:
            return new_achievements
        
        _debug_print(f"\n[ACHIEVEMENT DEBUG] check_lightning_fast_achievements: User {user.id}, levels={all_levels}")
        
        # Get existing lightning-fast achievements with metadata
        existing_lightning_fast = Achievement.query.filter_by(user_id=user.id).filter(
            Achievement.code.like("lightning-fast-%")
        ).all()
        
        # Build a map of level -> existing achievements for that level
        level_achievements_map: dict[int, list[Achievement]] = {}
        for ach in existing_lightning_fast:
            if ach.achievement_metadata:
                try:
                    metadata_dict = json.loads(ach.achievement_metadata)
                    level = metadata_dict.get("level")
                    if level is not None:
                        if level not in level_achievements_map:
                            level_achievements_map[level] = []
                        level_achievements_map[level].append(ach)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        # Check each level separately
        for target_level in all_levels:
            # Get responses for this level
            level_responses = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(Question.required_level == target_level)
                .all()
            )
            
            if not level_responses:
                continue
            
            # Calculate average speed for this level
            total_duration_ms = sum(r.duration_ms or 0 for r in level_responses)
            total_questions = len(level_responses)
            avg_speed = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 else None
            
            if not avg_speed or total_questions < 10:  # Need at least 10 questions
                continue
            
            # Get existing achievements for this level
            existing_for_level = level_achievements_map.get(target_level, [])
            existing_tiers = {ach.code.split("-")[-1] for ach in existing_for_level}
            
            # Find highest qualifying tier for this level
            qualifying_tiers = []
            for tier in ALL_TIERS:
                achievement_code = f"lightning-fast-{tier}"
                config = achievement_configs.get(achievement_code)
                if not config:
                    continue
                
                requirements = config.get("requirements", {})
                max_speed = requirements.get("max_speed_seconds", 999)
                min_questions = requirements.get("min_questions", 10)
                
                # Check if this tier is already awarded for this level
                if achievement_code in existing_tiers:
                    continue
                
                # Check if avg_speed meets the requirement
                if avg_speed <= max_speed and total_questions >= min_questions:
                    qualifying_tiers.append((tier, achievement_code, config, max_speed))
            
            if qualifying_tiers:
                # Sort by tier value (highest first) and award the highest tier
                qualifying_tiers.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
                highest_tier, achievement_code, config, max_speed_req = qualifying_tiers[0]
                
                # Don't award multiple for same performance
                # Check if there's already a higher or equal tier awarded
                should_award = True
                for existing_ach in existing_for_level:
                    existing_tier = existing_ach.code.split("-")[-1]
                    existing_tier_value = get_tier_value(existing_tier)
                    new_tier_value = get_tier_value(highest_tier)
                    
                    # If we're trying to award the same tier, don't award
                    if existing_tier == highest_tier:
                        should_award = False
                        break
                    
                    # If we're trying to award a lower tier than what's already awarded, don't award
                    if new_tier_value < existing_tier_value:
                        should_award = False
                        break
                
                if should_award:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} with metadata level={target_level} (avg speed {avg_speed:.2f}s at level {target_level})")
                    achievement = AchievementService.create_achievement(
                        user_id=user.id,
                        code=achievement_code,
                        title=config["title"],
                        description=config["description"],
                        icon=config["icon"],
                        category=config["category"],
                        session_id=session_id,
                        metadata={"level": target_level},
                    )
                    new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        achievement_configs = _get_achievement_configs()
        
        # Check if user has Level Master (Bronze) achievement
        if "level-master-bronze" not in user_achievement_codes:
            return new_achievements
        
        # Get all distinct levels from questions
        all_levels = [
            row[0] for row in
            db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]
        
        if not all_levels:
            return new_achievements
        
        _debug_print(f"\n[ACHIEVEMENT DEBUG] check_level_grandmaster_achievement: User {user.id}, levels={all_levels}")
        
        milestone_code = "level-grandmaster"
        
        # Skip if already earned
        if milestone_code in user_achievement_codes:
            return new_achievements
        
        # Check if user has achieved 30 consecutive correct at ALL levels
        all_levels_qualified = True
        for target_level in all_levels:
            # Get all responses for this level, ordered chronologically
            level_responses = (
                Response.query.filter_by(user_id=user.id)
                .join(Question)
                .filter(Question.required_level == target_level)
                .order_by(Response.answered_at.asc())
                .all()
            )
            
            if not level_responses:
                all_levels_qualified = False
                break
            
            # Calculate maximum consecutive correct count for this level
            max_consecutive = 0
            current_consecutive = 0
            
            for response in level_responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            # Check if this level has achieved bronze threshold (30 consecutive)
            if max_consecutive < 30:
                all_levels_qualified = False
                _debug_print(f"[ACHIEVEMENT DEBUG]   Level {target_level} has only {max_consecutive} consecutive (need 30)")
                break
        
        if all_levels_qualified:
            config = achievement_configs.get(milestone_code)
            if config:
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {milestone_code} (Level Master Bronze on all {len(all_levels)} levels)")
                achievement = AchievementService.create_achievement(
                    user_id=user.id,
                    code=milestone_code,
                    title=config["title"],
                    description=config["description"],
                    icon=config["icon"],
                    category=config["category"],
                )
                new_achievements.append(achievement)
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
        from ..services.server_record_service import ServerRecordService
        
        if tier.lower() != "champion":
            return False
        
        # Check if this achievement can have Champion tier
        if not ServerRecordService.canAchievementHaveChampionTier(achievement_code):
            return False
        
        # Determine record type and value
        record_type = ServerRecordService._determine_record_type(achievement_code)
        if not record_type:
            return False
        
        record_value = ServerRecordService._determine_record_value(session, record_type)
        if record_value is None:
            return False
        
        # Check and update record
        record_set = ServerRecordService.checkAndUpdateRecord(
            achievement_type=achievement_code,
            record_type=record_type,
            value=record_value,
            user_id=session.user_id,
            session_id=session.id,
        )
        
        return record_set

    @staticmethod
    @log_query
    def check_generic_accuracy_achievements(session: PracticeSession) -> list[Achievement]:
        """Check session for generic accuracy achievements and award highest tier achieved.
        
        Args:
            session: Completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        if not session.completed_at or session.is_test:
            return []
        
        from ..config.achievements import ACCURACY_ACHIEVEMENTS
        from ..utils.tier_utils import ALL_TIERS, get_tier_value, get_highest_tier
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(session.user_id)
        
        # Get session metrics
        total_questions = session.total_questions
        accuracy = session.accuracy / 100.0 if session.accuracy else 0.0  # Convert to 0-1 range
        total_duration_ms = session.total_duration_ms or 0
        avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
        
        # Get the operation and level for this session
        # We need to determine operation and level from session
        if not session.level:
            return []
        
        # Get operation from session's questions
        from ..models import Question
        first_question = (
            Question.query.join(Response)
            .filter(Response.session_id == session.id)
            .first()
        )
        
        if not first_question:
            return []
        
        operation = first_question.operation
        level = session.level
        
        # Check all tiers for this operation-level combination
        # We'll check from highest to lowest and award the highest tier achieved
        tiers_achieved = []
        
        for tier in reversed(ALL_TIERS):  # Check from highest to lowest
            achievement_code = f"{operation}-basics-{tier}"
            
            if achievement_code not in ACCURACY_ACHIEVEMENTS:
                continue
            
            # Skip if already earned (unless we want to allow multiple of same tier)
            if achievement_code in user_achievement_codes:
                continue
            
            config = ACCURACY_ACHIEVEMENTS[achievement_code]
            requirements = config.get("requirements", {})
            
            # Check if this is for the correct level
            if requirements.get("level") != level:
                continue
            
            # Check if operation matches
            if requirements.get("operation") != operation:
                continue
            
            # Check tier requirements
            min_accuracy_req = requirements.get("min_accuracy", 0.0)
            min_questions_req = requirements.get("min_questions", 0)
            max_questions_req = requirements.get("max_questions")
            max_speed_req = requirements.get("max_speed")
            
            meets_requirements = True
            
            # Check accuracy
            if accuracy < min_accuracy_req:
                meets_requirements = False
            
            # Check question count
            if total_questions < min_questions_req:
                meets_requirements = False
            
            if max_questions_req and total_questions > max_questions_req:
                meets_requirements = False
            
            # Check speed
            if max_speed_req:
                if avg_time_per_question is None:
                    meets_requirements = False
                elif avg_time_per_question >= max_speed_req:
                    meets_requirements = False
            
            if meets_requirements:
                tiers_achieved.append((tier, achievement_code, config))
        
        # Award only the highest tier achieved
        if tiers_achieved:
            # Sort by tier value (highest first)
            tiers_achieved.sort(key=lambda x: get_tier_value(x[0]), reverse=True)
            highest_tier, achievement_code, config = tiers_achieved[0]
            
            # Check for Champion tier eligibility if this is Divine tier
            if highest_tier == "divine":
                # Check if Champion is also eligible
                champion_code = f"{operation}-basics-champion"
                if champion_code in ACCURACY_ACHIEVEMENTS:
                    champion_config = ACCURACY_ACHIEVEMENTS[champion_code]
                    champion_req = champion_config.get("requirements", {})
                    
                    # Check if Champion requirements are also met
                    champion_eligible = True
                    if accuracy < champion_req.get("min_accuracy", 0.0):
                        champion_eligible = False
                    if total_questions < champion_req.get("min_questions", 0):
                        champion_eligible = False
                    if champion_req.get("max_questions") and total_questions > champion_req.get("max_questions"):
                        champion_eligible = False
                    if champion_req.get("max_speed"):
                        if avg_time_per_question is None or avg_time_per_question >= champion_req.get("max_speed"):
                            champion_eligible = False
                    
                    # If Champion requirements met, check server record
                    if champion_eligible:
                        if AchievementService.checkChampionEligibility(champion_code, session, "champion"):
                            # Award Champion instead
                            achievement_code = champion_code
                            config = champion_config
            
            # Award the achievement
            achievement = AchievementService.create_achievement(
                user_id=session.user_id,
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

    # Test achievement methods removed - test achievements are no longer used

