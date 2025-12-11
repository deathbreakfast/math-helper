"""Achievement query service for retrieving achievement data.

This service handles all read-only queries for achievements, providing
a clean separation between query operations and business logic.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import joinedload

from ....database import log_query
from ....models import Achievement, PracticeSession, Question, Response, db
from ..achievement_validators.tier_validator import TierValidator


class AchievementQueryService:
    """Service for querying achievement data."""
    
    @staticmethod
    @log_query
    def get_user_achievements(user_id: int, limit: int | None = None) -> list[Achievement]:
        """Get all achievements for a user.
        
        Args:
            user_id: The user ID to query achievements for
            limit: Optional limit on number of achievements to return
            
        Returns:
            List of achievements for the user, ordered by earned_at DESC
        """
        # Validate and cleanup any incorrectly awarded tier achievements
        TierValidator.validate_and_cleanup_tier_achievements(user_id)
        
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
        user_id: int | None = None, 
        category: str | None = None, 
        limit: int = 50, 
        include_user_name: bool = False
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
            TierValidator.validate_and_cleanup_tier_achievements(user_id)
        
        # Use JOIN with User table if we need user names (for all-users queries)
        # Use joinedload to eager load user relationship in a single query (avoids N+1)
        if include_user_name and not user_id:
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
    def get_achievement_codes(user_id: int) -> set[str]:
        """Get set of achievement codes earned by a user.
        
        Args:
            user_id: The user ID to query achievement codes for
            
        Returns:
            Set of achievement codes (strings)
        """
        achievements = Achievement.query.filter_by(user_id=user_id).all()
        return {a.code for a in achievements}

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
        """Count achievements with filters for level, accuracy, and operation.
        
        Supports tier substitution: higher tier achievements can substitute for lower tier requirements.
        Conversion: 4 bronze = 2 silver = 1 gold, etc.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count (must be tiered code like "addition-basics-bronze")
            level: Optional level filter (session level must match)
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            metadata_filter: Optional metadata filter (achievement metadata must match)
            
        Returns:
            Number of achievements matching all filters (with tier substitution applied)
        """
        from ....utils.tier_utils import extract_base_code_and_tier, TIER_HIERARCHY, convert_tier_to_base_units
        import json
        
        # Extract base code and target tier
        base_code, target_tier = extract_base_code_and_tier(achievement_code)
        
        # If no tier, just count exact matches (but still apply filters)
        if target_tier is None:
            query = Achievement.query.filter_by(user_id=user_id, code=achievement_code)
            if metadata_filter:
                metadata_json = json.dumps(metadata_filter, sort_keys=True)
                query = query.filter(Achievement.achievement_metadata == metadata_json)
            
            # Apply session-level filters if provided
            if level is not None or min_accuracy is not None or operation is not None:
                query = query.join(PracticeSession, Achievement.session_id == PracticeSession.id)
                
                if level is not None:
                    query = query.filter(PracticeSession.level == level)
                
                if min_accuracy is not None:
                    min_accuracy_percent = min_accuracy * 100.0
                    query = query.filter(PracticeSession.accuracy >= min_accuracy_percent)
                
                if operation is not None:
                    query = (
                        query.join(Response, PracticeSession.id == Response.session_id)
                        .join(Question, Response.question_id == Question.id)
                        .filter(Question.operation == operation)
                        .distinct()
                    )
            
            return query.count()
        
        # For tiered achievements, we need to find all achievements with the same base code
        # and apply tier substitution. We'll query all achievements with the base code pattern.
        # Get all achievements for this user
        all_achievements = Achievement.query.filter_by(user_id=user_id).all()
        
        # Filter achievements by base code and metadata
        matching_achievements = []
        for ach in all_achievements:
            ach_base, ach_tier = extract_base_code_and_tier(ach.code)
            
            # Must match base code
            if ach_base != base_code:
                continue
            
            # Must have a tier (skip non-tiered achievements)
            if ach_tier is None:
                continue
            
            # Check metadata filter if provided
            if metadata_filter:
                ach_metadata_str = ach.achievement_metadata
                if ach_metadata_str:
                    try:
                        ach_metadata = json.loads(ach_metadata_str)
                        if ach_metadata != metadata_filter:
                            continue
                    except (json.JSONDecodeError, TypeError):
                        continue
                else:
                    # Achievement has no metadata but filter requires it
                    continue
            else:
                # No metadata filter - only match achievements with no metadata
                if ach.achievement_metadata:
                    continue
            
            # Check session-level filters if provided
            if level is not None or min_accuracy is not None or operation is not None:
                if not ach.session_id:
                    continue
                
                session = PracticeSession.query.get(ach.session_id)
                if not session:
                    continue
                
                if level is not None and session.level != level:
                    continue
                
                if min_accuracy is not None:
                    session_accuracy = session.accuracy / 100.0 if session.accuracy else 0.0
                    if session_accuracy < min_accuracy:
                        continue
                
                if operation is not None:
                    # Check if session has questions with this operation
                    has_operation = (
                        Response.query.join(Question)
                        .filter(Response.session_id == session.id)
                        .filter(Question.operation == operation)
                        .first() is not None
                    )
                    if not has_operation:
                        continue
            
            matching_achievements.append(ach_tier)
        
        # Calculate total bronze units from matching achievements
        total_bronze_units = 0
        for ach_tier in matching_achievements:
            total_bronze_units += convert_tier_to_base_units(ach_tier, 1)
        
        # Convert bronze units to target tier count
        target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1)
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


