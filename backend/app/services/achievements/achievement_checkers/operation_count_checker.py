"""Checker for operation_count achievements."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func

from ....models import Achievement, Question, Response, User, db
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from .base_checker import AchievementChecker


class OperationCountChecker(AchievementChecker):
    """Checker for operation_count achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award operation_count achievements.
        
        Args:
            user: User to check achievements for
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of newly created achievements
        """
        achievement_configs = self.achievement_configs
        new_achievements = []
        user_achievement_codes = set(
            Achievement.query.filter_by(user_id=user.id).with_entities(Achievement.code).all()
        )
        user_achievement_codes = {code[0] for code in user_achievement_codes}
        
        for achievement_code, config in achievement_configs.items():
            req_type = config.get("requirements", {}).get("type")
            if req_type != "operation_count":
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            new_achievements.extend(
                self._check_operation_count(user, achievement_code, config, requirements, session_id)
            )
        
        return new_achievements
    
    def _check_operation_count(
        self, user: User, achievement_code: str, config: dict[str, Any], 
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check operation_count achievements.
        
        Note: Level filtering removed - this checker now operates across all concepts for the operation.
        This checker may be legacy as level-based achievements are being phased out.
        """
        operation = requirements.get("operation")
        count = requirements.get("count", 0)
        
        # Count correct answers for this operation (level filtering removed - no longer filtering by Question.required_level)
        correct_count = (
            db.session.query(func.count())
            .select_from(Response)
            .join(Question)
            .filter(
                Response.user_id == user.id,
                Response.is_correct == True,
                Question.operation == operation,
            )
            .scalar()
            or 0
        )
        
        debug_print(f"[ACHIEVEMENT DEBUG]   operation_count: operation={operation}, required={count}, actual={correct_count}")
        
        if correct_count >= count:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (operation_count: {correct_count} >= {count})")
            return [_create_achievement(
                user_id=user.id,
                code=achievement_code,
                title=config["title"],
                description=config["description"],
                icon=config["icon"],
                category=config["category"],
                session_id=session_id,
            )]
        else:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {count}, have {correct_count})")
            return []


