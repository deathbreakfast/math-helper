"""Level master achievement checker.

Awards concept-specific achievements for consecutive correct answers per concept.
Each bucket gets its own achievement with metadata:
- {"concept_id": "c_concept_XXX"} for legacy level-based buckets (derived from level)
- {"concept_id": "..."} for concept-based buckets (enables descriptive concept IDs)
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User, db
from ....utils.tier_utils import get_tier_value
from .base_checker import AchievementChecker


class LevelMasterChecker(AchievementChecker):
    """Checker for level master achievements (consecutive correct per level)."""
    
    def __init__(self, achievement_configs: dict[str, Any]):
        """Initialize checker with achievement configs.
        
        Args:
            achievement_configs: Dictionary of achievement configurations
        """
        self.achievement_configs = achievement_configs
    
    @staticmethod
    def _get_all_levels() -> list[int]:
        """Get all distinct legacy levels from questions.
        
        Returns:
            List of distinct level numbers, ordered ascending
        """
        return [
            row[0]
            for row in db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]
    
    @staticmethod
    def _get_user_concept_ids(user_id: int) -> list[str]:
        """Get all distinct concept_ids from the user's sessions.
        
        Supports descriptive concept IDs (e.g., "c_add_1s", "c_concept_001").
        
        Args:
            user_id: The user ID to get concept IDs for
        
        Returns:
            List of distinct concept IDs, ordered ascending
        """
        # Get all session IDs for this user
        concept_rows = (
            db.session.query(Response.session_id)
            .filter(Response.user_id == user_id)
            .distinct()
            .all()
        )
        session_ids = [row[0] for row in concept_rows if row and row[0] is not None]
        
        if not session_ids:
            return []
        
        # Get distinct concept_ids from those sessions
        return [
            row[0]
            for row in db.session.query(PracticeSession.concept_id)
            .filter(PracticeSession.id.in_(session_ids))
            .filter(PracticeSession.concept_id.isnot(None))
            .distinct()
            .order_by(PracticeSession.concept_id.asc())
            .all()
            if row and row[0]
        ]
    
    def _get_level_master_configs(self) -> dict[str, Any]:
        """Get Level Master achievement configs (excluding milestones).
        
        Returns:
            Dictionary of level master achievement configs
        """
        return {
            code: config for code, config in self.achievement_configs.items()
            if code.startswith("level-master-") and not code.startswith("level-master-milestone-")
        }
    
    @staticmethod
    def _get_responses_for_bucket(
        user_id: int,
        level_filter: int | None = None,
        concept_filter: str | None = None,
    ) -> tuple[list[Response], dict[str, Any]]:
        """Get responses for a specific bucket (level or concept) with metadata.
        
        Args:
            user_id: The user ID
            level_filter: Optional level filter
            concept_filter: Optional concept ID filter
        
        Returns:
            Tuple of (list of responses ordered chronologically, metadata dict)
        """
        if level_filter is not None:
            # Get all responses for this level, ordered chronologically
            # For legacy levels, derive concept_id from level
            responses = (
                Response.query.filter_by(user_id=user_id)
                .join(Question)
                .filter(Question.required_level == level_filter)
                .order_by(Response.answered_at.asc())
                .all()
            )
            metadata = {"concept_id": f"c_concept_{level_filter:03d}"}
        else:
            # Get all responses for this concept_id, ordered chronologically
            responses = (
                Response.query.filter_by(user_id=user_id)
                .join(PracticeSession, Response.session_id == PracticeSession.id)
                .filter(PracticeSession.concept_id == concept_filter)
                .order_by(Response.answered_at.asc())
                .all()
            )
            metadata = {"concept_id": concept_filter}
        
        return responses, metadata
    
    @staticmethod
    def _calculate_max_consecutive_correct(responses: list[Response]) -> int:
        """Calculate maximum consecutive correct answers from responses.
        
        Args:
            responses: List of responses ordered chronologically
        
        Returns:
            Maximum number of consecutive correct answers
        """
        max_consecutive = 0
        current_consecutive = 0
        
        for response in responses:
            if response.is_correct:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    @staticmethod
    def _find_highest_existing_tier(user_id: int, metadata_json: str) -> int:
        """Find the highest existing tier value for achievements with given metadata.
        
        Args:
            user_id: The user ID
            metadata_json: JSON string representation of metadata
        
        Returns:
            Highest tier value found, or -1 if none found
        """
        existing_achievements = (
            Achievement.query.filter_by(user_id=user_id, achievement_metadata=metadata_json)
            .filter(Achievement.code.like("level-master-%"))
            .all()
        )
        
        highest_tier_value = -1
        for existing in existing_achievements:
            code_parts = existing.code.split("-")
            if len(code_parts) >= 3 and code_parts[0] == "level" and code_parts[1] == "master":
                tier = code_parts[2]
                tier_value = get_tier_value(tier)
                highest_tier_value = max(highest_tier_value, tier_value)
        
        return highest_tier_value
    
    @staticmethod
    def _determine_highest_qualifying_tier(
        max_consecutive: int,
        highest_existing_tier: int,
        level_master_configs: dict[str, Any],
    ) -> tuple[str, str, dict[str, Any]] | None:
        """Determine the highest qualifying tier for an achievement.
        
        Args:
            max_consecutive: Maximum consecutive correct answers
            highest_existing_tier: Highest tier value already earned
            level_master_configs: Dictionary of level master achievement configs
        
        Returns:
            Tuple of (tier, achievement_code, config) for highest qualifying tier, or None
        """
        qualifying_tiers = []
        
        for achievement_code, config in level_master_configs.items():
            requirements = config.get("requirements", {})
            min_consecutive = requirements.get("min_consecutive", 30)
            tier = config.get("tier", "bronze")
            tier_value = get_tier_value(tier)
            
            if max_consecutive >= min_consecutive and tier_value > highest_existing_tier:
                qualifying_tiers.append((tier_value, tier, achievement_code, config))
        
        if not qualifying_tiers:
            return None
        
        # Return highest tier
        qualifying_tiers.sort(reverse=True)
        _, tier, achievement_code, config = qualifying_tiers[0]
        
        # Champion eligibility is session-contextual; skip divine tier here.
        if tier == "divine":
            return None
        
        return (tier, achievement_code, config)
    
    def _award_for_bucket(
        self,
        user: User,
        level_master_configs: dict[str, Any],
        session_id: int | None,
        level_filter: int | None = None,
        concept_filter: str | None = None,
    ) -> Achievement | None:
        """Award achievement for a specific bucket (level or concept).
        
        Args:
            user: The user to award achievements for
            level_master_configs: Dictionary of level master achievement configs
            session_id: Optional session ID to link achievements
            level_filter: Optional level filter
            concept_filter: Optional concept ID filter
        
        Returns:
            Newly created Achievement object, or None if no award
        """
        from ....services.achievements.achievement_utils import create_achievement
        
        # Get responses and metadata for this bucket
        responses, metadata = self._get_responses_for_bucket(
            user_id=user.id,
            level_filter=level_filter,
            concept_filter=concept_filter,
        )
        
        if not responses:
            return None
        
        # Calculate max consecutive correct
        max_consecutive = self._calculate_max_consecutive_correct(responses)
        
        # Find highest existing tier
        metadata_json = json.dumps(metadata, sort_keys=True)
        highest_existing_tier = self._find_highest_existing_tier(user.id, metadata_json)
        
        # Determine highest qualifying tier
        qualifying_tier_info = self._determine_highest_qualifying_tier(
            max_consecutive=max_consecutive,
            highest_existing_tier=highest_existing_tier,
            level_master_configs=level_master_configs,
        )
        
        if not qualifying_tier_info:
            return None
        
        tier, achievement_code, config = qualifying_tier_info
        
        # Create and return achievement
        return create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
            metadata=metadata,
        )
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award level master achievements.
        
        This checks consecutive correct answers at each concept separately.
        Awards separate achievements per concept with metadata {"concept_id": "..."}.
        Only awards the highest qualifying tier per concept.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        new_achievements = []
        
        # Get all distinct legacy levels from questions
        all_levels = self._get_all_levels()
        
        # Get all distinct concept_ids from the user's sessions
        concept_ids = self._get_user_concept_ids(user.id)
        
        # Get Level Master achievement configs
        level_master_configs = self._get_level_master_configs()
        
        if not level_master_configs:
            return new_achievements
        
        # Award per legacy level (existing behavior)
        for target_level in all_levels:
            achievement = self._award_for_bucket(
                user=user,
                level_master_configs=level_master_configs,
                session_id=session_id,
                level_filter=target_level,
            )
            if achievement:
                new_achievements.append(achievement)
        
        # Award per concept_id (enables descriptive concepts)
        for cid in concept_ids:
            achievement = self._award_for_bucket(
                user=user,
                level_master_configs=level_master_configs,
                session_id=session_id,
                concept_filter=cid,
            )
            if achievement:
                new_achievements.append(achievement)
        
        if new_achievements:
            from ....database import flush_or_commit
            flush_or_commit()
        
        return new_achievements







