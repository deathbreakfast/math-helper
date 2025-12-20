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
        if not concept_id:
            return None
        m = __import__("re").match(r"^c_concept_(\d+)$", str(concept_id))
        if m:
            return int(m.group(1))
        m = __import__("re").match(r"^c_level_(\d+)$", str(concept_id))
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def _metadata_matches_filter(
        ach_metadata_for_filter: dict[str, Any],
        metadata_filter: dict[str, Any],
    ) -> bool:
        """Metadata filter matching with concept_id compatibility.

        If metadata_filter includes concept_id, allow it to match either:
        - achievement.metadata.concept_id == concept_id, OR
        - achievement.metadata.level == legacy level parsed from concept_id

        All other keys must match exactly.
        """
        if not metadata_filter:
            return True

        # Fast path: exact match
        if ach_metadata_for_filter == metadata_filter:
            return True

        if "concept_id" not in metadata_filter:
            return False

        filter_concept_id = metadata_filter.get("concept_id")
        legacy_level = AchievementQueryService._legacy_level_from_concept_id(str(filter_concept_id) if filter_concept_id else None)

        # All non-concept keys must match exactly
        for k, v in metadata_filter.items():
            if k == "concept_id":
                continue
            if ach_metadata_for_filter.get(k) != v:
                return False

        # concept_id may match by concept_id or legacy level
        if ach_metadata_for_filter.get("concept_id") == filter_concept_id:
            return True
        if legacy_level is not None and ach_metadata_for_filter.get("level") == legacy_level:
            return True

        return False
    
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
                # Metadata is stored as JSON string; allow concept_id matching against legacy level metadata.
                # For non-tiered achievements we do an in-Python filter for compatibility.
                all_achievements = query.all()
                matching = 0
                for ach in all_achievements:
                    ach_metadata_str = ach.achievement_metadata
                    if not ach_metadata_str:
                        continue
                    try:
                        ach_metadata = json.loads(ach_metadata_str)
                        ach_metadata_for_filter = {k: v for k, v in ach_metadata.items() if k != "session_id"}
                    except (json.JSONDecodeError, TypeError):
                        continue

                    if AchievementQueryService._metadata_matches_filter(ach_metadata_for_filter, metadata_filter):
                        matching += 1

                # Apply session-level filters after metadata filtering if needed
                if level is not None or min_accuracy is not None or operation is not None:
                    # Fall back to the slower path below (tiered loop style) for correctness.
                    # Reuse the tiered path logic by treating each matching achievement as one unit.
                    # This is rare for non-tiered achievements with metadata.
                    filtered_achievements = []
                    for ach in all_achievements:
                        ach_metadata_str = ach.achievement_metadata
                        if not ach_metadata_str:
                            continue
                        try:
                            ach_metadata = json.loads(ach_metadata_str)
                            ach_metadata_for_filter = {k: v for k, v in ach_metadata.items() if k != "session_id"}
                        except (json.JSONDecodeError, TypeError):
                            continue
                        if AchievementQueryService._metadata_matches_filter(ach_metadata_for_filter, metadata_filter):
                            filtered_achievements.append(ach)

                    # Session-level filters
                    result = 0
                    for ach in filtered_achievements:
                        if not ach.session_id:
                            continue
                        session = db.session.get(PracticeSession, ach.session_id)
                        if not session:
                            continue
                        if level is not None and session.level != level:
                            continue
                        if min_accuracy is not None:
                            min_accuracy_percent = min_accuracy * 100.0
                            if (session.accuracy or 0) < min_accuracy_percent:
                                continue
                        if operation is not None:
                            # Only count if session includes at least one question of operation
                            has_op = (
                                db.session.query(Response)
                                .join(Question, Response.question_id == Question.id)
                                .filter(Response.session_id == session.id)
                                .filter(Question.operation == operation)
                                .first()
                                is not None
                            )
                            if not has_op:
                                continue
                        result += 1
                    return result

                return matching
            
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
                        # Remove session_id from metadata for comparison (it's added for uniqueness, not filtering)
                        ach_metadata_for_filter = {k: v for k, v in ach_metadata.items() if k != "session_id"}
                        if not AchievementQueryService._metadata_matches_filter(ach_metadata_for_filter, metadata_filter):
                            continue
                    except (json.JSONDecodeError, TypeError):
                        continue
                else:
                    # Achievement has no metadata but filter requires it
                    continue
            else:
                # No metadata filter - only match achievements with no metadata (or only session_id)
                if ach.achievement_metadata:
                    try:
                        ach_metadata = json.loads(ach.achievement_metadata)
                        # If metadata only contains session_id, treat it as no metadata for filtering
                        if set(ach_metadata.keys()) != {"session_id"}:
                            continue
                    except (json.JSONDecodeError, TypeError):
                        # If we can't parse metadata, skip it
                        continue
            
            # Check session-level filters if provided
            if level is not None or min_accuracy is not None or operation is not None:
                if not ach.session_id:
                    continue
                
                session = db.session.get(PracticeSession, ach.session_id)
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
