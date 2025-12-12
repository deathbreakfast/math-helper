"""Checker for level_correct_count achievements."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func

from ....models import Achievement, Question, Response, User, db
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from .base_checker import AchievementChecker


class LevelCorrectCountChecker(AchievementChecker):
    """Checker for level_correct_count achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award level_correct_count achievements.
        
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
            if req_type != "level_correct_count":
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            new_achievements.extend(
                self._check_level_correct_count(user, achievement_code, config, requirements, session_id)
            )
        
        return new_achievements
    
    def _check_level_correct_count(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check level_correct_count achievements."""
        level = requirements.get("level")
        min_correct = requirements.get("min_correct", 0)
        
        # Count correct answers at this level
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
        
        debug_print(f"[ACHIEVEMENT DEBUG]   level_correct_count: level={level}, required={min_correct}, actual={correct_count}")
        
        if correct_count >= min_correct:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (correct_count: {correct_count} >= {min_correct})")
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
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_correct}, have {correct_count})")
            return []
