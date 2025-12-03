"""Achievement service for rules engine and achievement assignment."""

from __future__ import annotations

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
    ) -> Achievement:
        """Manually create an achievement for a user."""
        if earned_at is None:
            earned_at = datetime.utcnow()

        # Check if already exists
        existing = Achievement.query.filter_by(user_id=user_id, code=code).first()
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
            test_type: Optional test type to check (e.g., "multiplication_1")
        
        Returns:
            List of newly created achievements
        """
        from ..models import Response, Question
        from ..services.session_engine_service import SessionEngineService
        
        new_achievements = []
        
        # If test_type is provided, check only that type
        test_types_to_check = [test_type] if test_type else [
            "multiplication_1", "multiplication_2", "multiplication_3", "multiplication_4",
            "multiplication_5", "multiplication_6", "multiplication_7", "multiplication_8",
            "multiplication_9", "multiplication_10", "multiplication_11", "multiplication_12",
            "division_2digit", "division_3digit", "division_fraction", "division_decimal",
        ]
        
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
            elif check_test_type in SessionEngineService.LEVEL_TEST_TYPES:
                operation, required_level, _, _ = SessionEngineService.LEVEL_TEST_TYPES[check_test_type]
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
            "multiplication_1": "multiplication-2",
            "multiplication_2": "multiplication-3",
            "multiplication_3": "multiplication-4",
            "multiplication_4": "multiplication-5",
            "multiplication_5": "multiplication-6",
            "multiplication_6": "multiplication-7",
            "multiplication_7": "multiplication-8",
            "multiplication_8": "multiplication-9",
            "multiplication_9": "multiplication-10",
            "multiplication_10": "multiplication-11",
            "multiplication_11": "multiplication-12",
            "multiplication_2digit": "multiplication-2digit",
            "multiplication_3digit": "multiplication-3digit",
            "division_1digit": "division-1digit",
            "division_2digit": "division-2digit",
            "division_3digit": "division-3digit",
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

    @staticmethod
    @log_query
    def check_test_tier_achievements(session: PracticeSession) -> list[Achievement]:
        """Check and award tiered test achievements (B, A, S, SS, SSS) based on session performance.
        
        Args:
            session: The completed practice session to check
            
        Returns:
            List of newly created achievements
        """
        if not session.is_test or not session.test_type or not session.completed_at:
            return []
        
        _debug_print(f"\n[ACHIEVEMENT DEBUG] check_test_tier_achievements: Session {session.id}, User {session.user_id}, test_type={session.test_type}")
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(session.user_id)
        
        # Map backend test_type to frontend test type format
        # Backend: "addition_1digit" -> Frontend: "addition-1digit"
        test_type_mapping = {
            "addition_1digit": "addition-1digit",
            "addition_2digit": "addition-2digit",
            "addition_3digit": "addition-3digit",
            "subtraction_1digit": "subtraction-1digit",
            "subtraction_2digit": "subtraction-2digit",
            "subtraction_3digit": "subtraction-3digit",
            "multiplication_1": "multiplication-2",
            "multiplication_2": "multiplication-3",
            "multiplication_3": "multiplication-4",
            "multiplication_4": "multiplication-5",
            "multiplication_5": "multiplication-6",
            "multiplication_6": "multiplication-7",
            "multiplication_7": "multiplication-8",
            "multiplication_8": "multiplication-9",
            "multiplication_9": "multiplication-10",
            "multiplication_10": "multiplication-11",
            "multiplication_11": "multiplication-12",
            "multiplication_2digit": "multiplication-2digit",
            "multiplication_3digit": "multiplication-3digit",
            "division_1digit": "division-1digit",
            "division_2digit": "division-2digit",
            "division_3digit": "division-3digit",
        }
        
        frontend_test_type = test_type_mapping.get(session.test_type)
        if not frontend_test_type:
            _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ No frontend mapping for test_type: {session.test_type}")
            return []
        
        _debug_print(f"[ACHIEVEMENT DEBUG]   frontend_test_type={frontend_test_type}")
        
        # Calculate session metrics
        total_questions = session.total_questions
        correct_count = session.correct_count
        accuracy = session.accuracy  # Already in percentage (0-100)
        total_duration_ms = session.total_duration_ms or 0
        
        # Calculate average time per question in seconds
        avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
        
        _debug_print(f"[ACHIEVEMENT DEBUG]   Session metrics: questions={total_questions}, correct={correct_count}, accuracy={accuracy}%, duration={total_duration_ms}ms, avg_time={avg_time_per_question:.2f}s" if avg_time_per_question else f"[ACHIEVEMENT DEBUG]   Session metrics: questions={total_questions}, correct={correct_count}, accuracy={accuracy}%, duration={total_duration_ms}ms, avg_time=None")
        
        # Tier definitions (check in order from highest to lowest tier)
        tiers = [
            {
                "suffix": "sss",
                "title": f"{frontend_test_type.replace('-', ' ').title()} - Rank SSS",
                "description": "Legendary mastery",
                "icon": "💎",
                "requirements": {
                    "min_accuracy": 100,
                    "question_count": 100,  # Exactly 100
                    "max_question_count": 100,
                    "max_speed": 2,  # <2s per question
                }
            },
            {
                "suffix": "ss",
                "title": f"{frontend_test_type.replace('-', ' ').title()} - Rank SS",
                "description": "Elite performance",
                "icon": "🌟",
                "requirements": {
                    "min_accuracy": 100,
                    "max_question_count": 90,  # <90
                    "max_speed": 4,  # <4s per question
                }
            },
            {
                "suffix": "s",
                "title": f"{frontend_test_type.replace('-', ' ').title()} - Rank S",
                "description": "Perfect score with speed",
                "icon": "⭐",
                "requirements": {
                    "min_accuracy": 100,
                    "min_question_count": 31,  # >30 (more than 30)
                    "max_question_count": 59,  # <60 (less than 60)
                    "max_speed": 6,  # <6s per question
                }
            },
            {
                "suffix": "a",
                "title": f"{frontend_test_type.replace('-', ' ').title()} - Rank A",
                "description": "100% accuracy (under 30 questions)",
                "icon": "📗",
                "requirements": {
                    "min_accuracy": 100,
                    "max_question_count": 29,  # <30
                }
            },
            {
                "suffix": "b",
                "title": f"{frontend_test_type.replace('-', ' ').title()} - Rank B",
                "description": "Complete test",
                "icon": "📘",
                "requirements": {
                    "min_question_count": 30,  # >=30
                }
            },
        ]
        
        # Check each tier from highest to lowest
        for tier in tiers:
            achievement_code = f"{frontend_test_type}-{tier['suffix']}"
            
            # Skip if already earned
            if achievement_code in user_achievement_codes:
                _debug_print(f"[ACHIEVEMENT DEBUG]   Skipping {achievement_code} - already earned")
                continue
            
            _debug_print(f"[ACHIEVEMENT DEBUG]   Checking tier {tier['suffix'].upper()}: {achievement_code}")
            
            req = tier["requirements"]
            meets_requirements = True
            failure_reasons = []
            
            # Check accuracy requirement
            if "min_accuracy" in req:
                if accuracy < req["min_accuracy"]:
                    meets_requirements = False
                    failure_reasons.append(f"accuracy {accuracy}% < {req['min_accuracy']}%")
                else:
                    _debug_print(f"[ACHIEVEMENT DEBUG]     ✓ accuracy: {accuracy}% >= {req['min_accuracy']}%")
            
            # Check minimum question count
            if "min_question_count" in req:
                if total_questions < req["min_question_count"]:
                    meets_requirements = False
                    failure_reasons.append(f"questions {total_questions} < {req['min_question_count']}")
                else:
                    _debug_print(f"[ACHIEVEMENT DEBUG]     ✓ min_questions: {total_questions} >= {req['min_question_count']}")
            
            # Check maximum question count
            if "max_question_count" in req:
                if total_questions > req["max_question_count"]:
                    meets_requirements = False
                    failure_reasons.append(f"questions {total_questions} > {req['max_question_count']}")
                else:
                    _debug_print(f"[ACHIEVEMENT DEBUG]     ✓ max_questions: {total_questions} <= {req['max_question_count']}")
            
            # Check exact question count (for SSS)
            if "question_count" in req:
                if total_questions != req["question_count"]:
                    meets_requirements = False
                    failure_reasons.append(f"questions {total_questions} != {req['question_count']}")
                else:
                    _debug_print(f"[ACHIEVEMENT DEBUG]     ✓ question_count: {total_questions} == {req['question_count']}")
            
            # Check speed requirement
            if "max_speed" in req:
                if avg_time_per_question is None:
                    meets_requirements = False
                    failure_reasons.append("avg_time is None")
                elif avg_time_per_question >= req["max_speed"]:
                    meets_requirements = False
                    failure_reasons.append(f"avg_time {avg_time_per_question:.2f}s >= {req['max_speed']}s")
                else:
                    _debug_print(f"[ACHIEVEMENT DEBUG]     ✓ speed: {avg_time_per_question:.2f}s < {req['max_speed']}s")
            
            if meets_requirements:
                _debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
                achievement = AchievementService.create_achievement(
                    user_id=session.user_id,
                    code=achievement_code,
                    title=tier["title"],
                    description=tier["description"],
                    icon=tier["icon"],
                    category="test",
                    session_id=session.id,
                )
                new_achievements.append(achievement)
                break  # Only award the highest tier achieved
            else:
                if failure_reasons:
                    _debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding {achievement_code} - reasons: {', '.join(failure_reasons)}")
        
        if new_achievements:
            db.session.commit()
        
        return new_achievements

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
    ) -> int:
        """Count achievements with filters for level, accuracy, and operation.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count (must be tiered code like "addition-basics-bronze")
            level: Optional level filter (session level must match)
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            
        Returns:
            Number of achievements matching all filters
        """
        # Base query: achievements with matching code
        query = Achievement.query.filter_by(
            user_id=user_id,
            code=achievement_code
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

    @staticmethod
    @log_query
    def check_generic_test_achievements(session: PracticeSession) -> list[Achievement]:
        """Check session for generic test achievements using new tier system and award highest tier.
        
        This replaces the old check_test_tier_achievements with the new metal/prestige tier system.
        
        Args:
            session: Completed test session to check
            
        Returns:
            List of newly created achievements
        """
        if not session.is_test or not session.test_type or not session.completed_at:
            return []
        
        from ..config.achievements import ACHIEVEMENTS_CONFIG
        from ..utils.tier_utils import ALL_TIERS, get_tier_value
        
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(session.user_id)
        
        # Get all test achievements from config (includes both new and legacy)
        # Filter to only test category achievements
        test_achievements = {
            code: config for code, config in ACHIEVEMENTS_CONFIG.items()
            if config.get("category") == "test" and config.get("requirements", {}).get("type") == "test_tier"
        }
        
        # Map backend test_type to frontend format
        test_type_mapping = {
            "addition_1digit": "addition-1digit",
            "addition_2digit": "addition-2digit",
            "addition_3digit": "addition-3digit",
            "subtraction_1digit": "subtraction-1digit",
            "subtraction_2digit": "subtraction-2digit",
            "subtraction_3digit": "subtraction-3digit",
            "multiplication_1": "multiplication-by-1",
            "multiplication_2": "multiplication-by-2",
            "multiplication_3": "multiplication-by-3",
            "multiplication_4": "multiplication-by-4",
            "multiplication_5": "multiplication-by-5",
            "multiplication_6": "multiplication-by-6",
            "multiplication_7": "multiplication-by-7",
            "multiplication_8": "multiplication-by-8",
            "multiplication_9": "multiplication-by-9",
            "multiplication_10": "multiplication-by-10",
            "multiplication_11": "multiplication-by-11",
            "multiplication_12": "multiplication-by-12",
            "multiplication_2digit": "multiplication-2digit",
            "multiplication_3digit": "multiplication-3digit",
            "division_1digit": "division-by-1",
            "division_2digit": "division-by-2",
            "division_3digit": "division-by-3",
        }
        
        frontend_test_type = test_type_mapping.get(session.test_type)
        if not frontend_test_type:
            # Try direct match
            frontend_test_type = session.test_type.replace("_", "-")
        
        # Get session metrics
        total_questions = session.total_questions
        accuracy = session.accuracy  # Already in percentage (0-100)
        total_duration_ms = session.total_duration_ms or 0
        avg_time_per_question = (total_duration_ms / 1000.0 / total_questions) if total_questions > 0 and total_duration_ms else None
        
        # Check all tiers from highest to lowest
        tiers_achieved = []
        
        for tier in reversed(ALL_TIERS):
            achievement_code = f"{frontend_test_type}-{tier}"
            
            if achievement_code not in test_achievements:
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            config = test_achievements[achievement_code]
            requirements = config.get("requirements", {})
            
            # Check if test_type matches
            if requirements.get("test_type") != frontend_test_type:
                continue
            
            # Check tier requirements
            min_accuracy_req = requirements.get("min_accuracy")
            min_question_count_req = requirements.get("min_question_count", 1)
            max_question_count_req = requirements.get("max_question_count")
            max_speed_req = requirements.get("max_speed")
            
            meets_requirements = True
            
            # Check accuracy (convert percentage to 0-100 range for comparison)
            if min_accuracy_req:
                if accuracy < min_accuracy_req:
                    meets_requirements = False
            
            # Check question count
            if total_questions < min_question_count_req:
                meets_requirements = False
            
            if max_question_count_req and total_questions > max_question_count_req:
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
                champion_code = f"{frontend_test_type}-champion"
                if champion_code in test_achievements:
                    champion_config = test_achievements[champion_code]
                    champion_req = champion_config.get("requirements", {})
                    
                    # Check if Champion requirements are also met
                    champion_eligible = True
                    if champion_req.get("min_accuracy") and accuracy < champion_req.get("min_accuracy"):
                        champion_eligible = False
                    if total_questions < champion_req.get("min_question_count", 1):
                        champion_eligible = False
                    if champion_req.get("max_question_count") and total_questions > champion_req.get("max_question_count"):
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

