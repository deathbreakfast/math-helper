"""Achievement query service for retrieving achievement data.

This service handles all read-only queries for achievements, providing
a clean separation between query operations and business logic.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import joinedload

from ....database import log_query
from ....models import Achievement, PracticeSession, Question, Response, db


class AchievementQueryService:
    """Service for querying achievement data."""

    @staticmethod
    def _legacy_level_from_concept_id(concept_id: str | None) -> int | None:
        """Extract level number from c_concept_### format concept ID.
        
        Note: Legacy level system removed. This is kept for minimal backward compatibility.
        """
        if not concept_id:
            return None
        m = __import__("re").match(r"^c_concept_(\d+)$", str(concept_id))
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def _metadata_matches_filter(
        ach_metadata_for_filter: dict[str, Any],
        metadata_filter: dict[str, Any],
    ) -> bool:
        """Metadata filter matching.

        All keys in metadata_filter must match exactly in ach_metadata_for_filter.
        """
        if not metadata_filter:
            return True

        # Exact match required
        return ach_metadata_for_filter == metadata_filter
    
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
        """Get all achievements for a user by achievement code.
        
        This returns *all* instances of the given code (including different metadata variants),
        ordered by most recent first.
        
        Args:
            user_id: The user ID to query achievements for
            achievement_code: The achievement code to filter by
        
        Returns:
            List of achievements with the given code for the user, ordered by earned_at DESC
        """
        return (
            Achievement.query.filter_by(user_id=user_id, code=achievement_code)
            .order_by(Achievement.earned_at.desc())
            .all()
        )

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
    def _parse_achievement_metadata(achievement: Achievement) -> dict[str, Any] | None:
        """Parse achievement metadata from JSON string.
        
        Args:
            achievement: Achievement object with achievement_metadata field
            
        Returns:
            Parsed metadata dict (excluding session_id), or None if parsing fails or no metadata
        """
        import json
        
        ach_metadata_str = achievement.achievement_metadata
        if not ach_metadata_str:
            return None
        
        try:
            ach_metadata = json.loads(ach_metadata_str)
            # Remove session_id from metadata for comparison (it's added for uniqueness, not filtering)
            return {k: v for k, v in ach_metadata.items() if k != "session_id"}
        except (json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _apply_metadata_filter(
        achievement: Achievement,
        metadata_filter: dict[str, Any] | None,
    ) -> bool:
        """Check if achievement matches metadata filter.
        
        Args:
            achievement: Achievement to check
            metadata_filter: Optional metadata filter dict
            
        Returns:
            True if achievement matches filter (or no filter provided), False otherwise
        """
        if not metadata_filter:
            # No metadata filter - only match achievements with no metadata (or only session_id)
            if not achievement.achievement_metadata:
                return True
            
            parsed = AchievementQueryService._parse_achievement_metadata(achievement)
            if parsed is None:
                # Can't parse, skip it
                return False
            
            # If metadata only contains session_id, treat it as no metadata for filtering
            return len(parsed) == 0
        
        # Metadata filter provided - must match
        parsed = AchievementQueryService._parse_achievement_metadata(achievement)
        if parsed is None:
            # Achievement has no metadata but filter requires it
            return False
        
        return AchievementQueryService._metadata_matches_filter(parsed, metadata_filter)

    @staticmethod
    def _apply_session_filters(
        achievement: Achievement,
        min_accuracy: float | None = None,
        operation: str | None = None,
    ) -> bool:
        """Check if achievement's session matches session-level filters.
        
        Args:
            achievement: Achievement to check
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            
        Returns:
            True if session matches all provided filters (or no filters provided), False otherwise
        """
        if min_accuracy is None and operation is None:
            return True
        
        if not achievement.session_id:
            return False
        
        session = db.session.get(PracticeSession, achievement.session_id)
        if not session:
            return False
        
        if min_accuracy is not None:
            min_accuracy_percent = min_accuracy * 100.0
            if (session.accuracy or 0) < min_accuracy_percent:
                return False
        
        if operation is not None:
            # Check if session has questions with this operation
            has_operation = (
                db.session.query(Response)
                .join(Question, Response.question_id == Question.id)
                .filter(Response.session_id == session.id)
                .filter(Question.operation == operation)
                .first()
                is not None
            )
            if not has_operation:
                return False
        
        return True

    @staticmethod
    def _count_non_tiered_achievements(
        user_id: int,
        achievement_code: str,
        min_accuracy: float | None = None,
        operation: str | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> int:
        """Count non-tiered achievements with filters.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count (non-tiered)
            min_accuracy: Optional minimum accuracy filter
            operation: Optional operation filter
            metadata_filter: Optional metadata filter
            
        Returns:
            Number of achievements matching all filters
        """
        query = Achievement.query.filter_by(user_id=user_id, code=achievement_code)
        
        # If we have metadata filter or session filters, we need to do in-Python filtering
        # because metadata is stored as JSON string and can't be efficiently queried in SQL
        has_metadata_filter = metadata_filter is not None
        has_session_filters = min_accuracy is not None or operation is not None
        
        if has_metadata_filter or has_session_filters:
            all_achievements = query.all()
            matching = 0
            
            for ach in all_achievements:
                # Apply metadata filter
                if not AchievementQueryService._apply_metadata_filter(ach, metadata_filter):
                    continue
                
                # Apply session-level filters (level filtering removed)
                if not AchievementQueryService._apply_session_filters(ach, min_accuracy, operation):
                    continue
                
                matching += 1
            
            return matching
        
        # No filters - can use efficient SQL count
        return query.count()

    @staticmethod
    def _count_tiered_achievements(
        user_id: int,
        base_code: str,
        target_tier: str,
        min_accuracy: float | None = None,
        operation: str | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> int:
        """Count tiered achievements with tier substitution.
        
        Args:
            user_id: User ID
            base_code: Base achievement code (without tier)
            target_tier: Target tier to count (e.g., "bronze")
            min_accuracy: Optional minimum accuracy filter
            operation: Optional operation filter
            metadata_filter: Optional metadata filter
            
        Returns:
            Number of achievements matching all filters (with tier substitution applied)
        """
        from ....utils.tier_utils import extract_base_code_and_tier, TIER_HIERARCHY, convert_tier_to_base_units
        
        # Get all achievements for this user
        all_achievements = Achievement.query.filter_by(user_id=user_id).all()
        
        # Filter achievements by base code, tier, metadata, and session filters
        matching_tiers = []
        for ach in all_achievements:
            ach_base, ach_tier = extract_base_code_and_tier(ach.code)
            
            # Must match base code
            if ach_base != base_code:
                continue
            
            # Must have a tier (skip non-tiered achievements)
            if ach_tier is None:
                continue
            
            # Apply metadata filter
            if not AchievementQueryService._apply_metadata_filter(ach, metadata_filter):
                continue
            
            # Apply session-level filters (level filtering removed)
            if not AchievementQueryService._apply_session_filters(ach, min_accuracy, operation):
                continue
            
            matching_tiers.append(ach_tier)
        
        # Calculate total bronze units from matching achievements
        total_bronze_units = 0
        for ach_tier in matching_tiers:
            total_bronze_units += convert_tier_to_base_units(ach_tier, 1)
        
        # Convert bronze units to target tier count
        target_tier_value = TIER_HIERARCHY.get(target_tier.lower(), 1)
        bronze_units_per_target = 2 ** (target_tier_value - 1) if target_tier_value > 1 else 1
        equivalent_count = total_bronze_units // bronze_units_per_target
        
        return equivalent_count

    @staticmethod
    @log_query
    def count_achievements_by_code_with_filters(
        user_id: int,
        achievement_code: str,
        min_accuracy: float | None = None,
        operation: str | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> int:
        """Count achievements with filters for accuracy and operation.
        
        Supports tier substitution: higher tier achievements can substitute for lower tier requirements.
        Conversion: 4 bronze = 2 silver = 1 gold, etc.
        
        Args:
            user_id: User ID
            achievement_code: Achievement code to count (must be tiered code like "addition-basics-bronze")
            min_accuracy: Optional minimum accuracy filter (session accuracy must be >= this, as 0.0-1.0)
            operation: Optional operation filter (session must have questions with this operation)
            metadata_filter: Optional metadata filter (achievement metadata must match)
            
        Returns:
            Number of achievements matching all filters (with tier substitution applied)
        """
        from ....utils.tier_utils import extract_base_code_and_tier
        
        # Extract base code and target tier
        base_code, target_tier = extract_base_code_and_tier(achievement_code)
        
        # Route to appropriate counting method
        if target_tier is None:
            return AchievementQueryService._count_non_tiered_achievements(
                user_id=user_id,
                achievement_code=achievement_code,
                min_accuracy=min_accuracy,
                operation=operation,
                metadata_filter=metadata_filter,
            )
        else:
            return AchievementQueryService._count_tiered_achievements(
                user_id=user_id,
                base_code=base_code,
                target_tier=target_tier,
                min_accuracy=min_accuracy,
                operation=operation,
                metadata_filter=metadata_filter,
            )
