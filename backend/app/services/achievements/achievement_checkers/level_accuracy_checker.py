"""Checker for level_accuracy achievements."""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from .base_checker import AchievementChecker


class LevelAccuracyChecker(AchievementChecker):
    """Checker for level_accuracy achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award level_accuracy achievements.
        
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
            if req_type != "level_accuracy":
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            new_achievements.extend(
                self._check_level_accuracy(user, achievement_code, config, requirements, session_id)
            )
        
        return new_achievements
    
    def _check_level_accuracy(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check level_accuracy achievements."""
        level = requirements.get("level")
        min_accuracy = requirements.get("min_accuracy", 0.0)
        question_count = requirements.get("question_count", 0)
        min_speed = requirements.get("min_speed")
        
        # Get all responses for this level
        responses = (
            Response.query.filter_by(user_id=user.id)
            .join(Question)
            .filter(Question.required_level == level)
            .all()
        )
        
        if not responses:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (no responses at level {level})")
            return []
        
        # Check question count requirements
        if question_count > 0 and len(responses) < question_count:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {question_count} questions, have {len(responses)})")
            return []
        
        # Check accuracy requirement
        correct_count = sum(1 for r in responses if r.is_correct)
        accuracy = (correct_count / len(responses)) * 100 if responses else 0
        
        if accuracy < min_accuracy * 100:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_accuracy:.0%} accuracy, have {accuracy:.1f}%)")
            return []
        
        # Check speed requirement (if specified, calculate from session)
        if min_speed is not None:
            # Get most recent session for this level
            session = (
                PracticeSession.query.filter_by(user_id=user.id)
                .filter(PracticeSession.completed_at.isnot(None))
                .order_by(PracticeSession.completed_at.desc())
                .first()
            )
            
            if session and session.total_duration_ms and session.total_questions:
                avg_speed = (session.total_duration_ms / 1000.0) / session.total_questions
                if avg_speed > min_speed:
                    debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need speed <= {min_speed}s/question, have {avg_speed:.2f}s/question)")
                    return []
        
        debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (accuracy: {accuracy:.1f}% >= {min_accuracy:.0%})")
        return [_create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
        )]


