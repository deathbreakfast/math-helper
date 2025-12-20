"""Level master achievement checker.

Awards level-specific achievements for consecutive correct answers at each level.
Each bucket gets its own achievement with metadata:
- {"level": N} for legacy level-based buckets (existing behavior)
- {"concept_id": "..."} for concept-based buckets (enables descriptive concept IDs)
"""

from __future__ import annotations

import json
from typing import Any

from ....models import Achievement, Question, Response, User, db
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
    
    def check(
        self,
        user: User,
        metrics: dict[str, Any] | None = None,
        session_id: int | None = None
    ) -> list[Achievement]:
        """Check and award level master achievements.
        
        This checks consecutive correct answers at each level separately.
        Awards separate achievements per level with metadata {"level": N}.
        Only awards the highest qualifying tier per level.
        
        Args:
            user: The user to check achievements for
            metrics: Optional pre-computed user metrics (not used)
            session_id: Optional session ID to link achievements
        
        Returns:
            List of newly created Achievement objects
        """
        from ....services.achievements.achievement_utils import create_achievement
        
        new_achievements = []
        
        # Get all distinct legacy levels from questions
        all_levels = [
            row[0]
            for row in db.session.query(Question.required_level)
            .distinct()
            .order_by(Question.required_level.asc())
            .all()
        ]

        # Get all distinct concept_ids from the user's sessions (supports descriptive concept ids)
        concept_rows = (
            db.session.query(Response.session_id)
            .filter(Response.user_id == user.id)
            .distinct()
            .all()
        )
        session_ids = [row[0] for row in concept_rows if row and row[0] is not None]
        concept_ids: list[str] = []
        if session_ids:
            from ....models import PracticeSession

            concept_ids = [
                row[0]
                for row in db.session.query(PracticeSession.concept_id)
                .filter(PracticeSession.id.in_(session_ids))
                .filter(PracticeSession.concept_id.isnot(None))
                .distinct()
                .order_by(PracticeSession.concept_id.asc())
                .all()
                if row and row[0]
            ]
        
        # Get Level Master achievement configs
        level_master_configs = {
            code: config for code, config in self.achievement_configs.items()
            if code.startswith("level-master-") and not code.startswith("level-master-milestone-")
        }
        
        if not level_master_configs:
            return new_achievements
        
        def _award_for_bucket(
            bucket_label: str,
            level_filter: int | None = None,
            concept_filter: str | None = None,
        ) -> None:
            nonlocal new_achievements

            if level_filter is not None:
                # Get all responses for this level, ordered chronologically
                responses = (
                    Response.query.filter_by(user_id=user.id)
                    .join(Question)
                    .filter(Question.required_level == level_filter)
                    .order_by(Response.answered_at.asc())
                    .all()
                )
                metadata = {"level": level_filter}
            else:
                # Get all responses for this concept_id, ordered chronologically
                from ....models import PracticeSession

                responses = (
                    Response.query.filter_by(user_id=user.id)
                    .join(PracticeSession, Response.session_id == PracticeSession.id)
                    .filter(PracticeSession.concept_id == concept_filter)
                    .order_by(Response.answered_at.asc())
                    .all()
                )
                metadata = {"concept_id": concept_filter}

            if not responses:
                return

            max_consecutive = 0
            current_consecutive = 0
            for response in responses:
                if response.is_correct:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0

            metadata_json = json.dumps(metadata, sort_keys=True)

            existing_achievements = (
                Achievement.query.filter_by(user_id=user.id, achievement_metadata=metadata_json)
                .filter(Achievement.code.like("level-master-%"))
                .all()
            )

            highest_existing_tier_value = -1
            for existing in existing_achievements:
                code_parts = existing.code.split("-")
                if len(code_parts) >= 3 and code_parts[0] == "level" and code_parts[1] == "master":
                    tier = code_parts[2]
                    tier_value = get_tier_value(tier)
                    highest_existing_tier_value = max(highest_existing_tier_value, tier_value)

            qualifying_tiers = []
            for achievement_code, config in level_master_configs.items():
                requirements = config.get("requirements", {})
                min_consecutive = requirements.get("min_consecutive", 30)
                tier = config.get("tier", "bronze")
                tier_value = get_tier_value(tier)

                if max_consecutive >= min_consecutive and tier_value > highest_existing_tier_value:
                    qualifying_tiers.append((tier_value, tier, achievement_code, config))

            if not qualifying_tiers:
                return

            qualifying_tiers.sort(reverse=True)
            _, tier, achievement_code, config = qualifying_tiers[0]

            # Champion eligibility is session-contextual; skip here.
            if tier == "divine":
                pass

            achievement = create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
                metadata=metadata,
            )
            new_achievements.append(achievement)

        # Award per legacy level (existing behavior)
        for target_level in all_levels:
            _award_for_bucket(bucket_label=f"level:{target_level}", level_filter=target_level)

        # Award per concept_id (enables descriptive concepts)
        for cid in concept_ids:
            _award_for_bucket(bucket_label=f"concept:{cid}", concept_filter=cid)

        if new_achievements:
            db.session.commit()

        return new_achievements







