"""Checker for session_accuracy_and_consecutive, perfect_sessions, and level_mastery achievements."""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User, db
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from .base_checker import AchievementChecker


class SessionAchievementsChecker(AchievementChecker):
    """Checker for session-based achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award session-based achievements.
        
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
            if req_type not in ["session_accuracy_and_consecutive", "perfect_sessions", "level_mastery"]:
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            
            if req_type == "session_accuracy_and_consecutive":
                new_achievements.extend(
                    self._check_session_accuracy_and_consecutive(user, achievement_code, config, requirements, session_id)
                )
            elif req_type == "perfect_sessions":
                new_achievements.extend(
                    self._check_perfect_sessions(user, achievement_code, config, requirements, session_id)
                )
            elif req_type == "level_mastery":
                new_achievements.extend(
                    self._check_level_mastery(user, achievement_code, config, requirements, session_id)
                )
        
        return new_achievements
    
    def _check_session_accuracy_and_consecutive(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check session_accuracy_and_consecutive achievements."""
        min_sessions = requirements.get("min_sessions", 0)
        min_session_accuracy = requirements.get("min_session_accuracy", 0.0)
        level = requirements.get("level")
        consecutive_correct = requirements.get("consecutive_correct", 0)
        
        # Count sessions with required accuracy
        sessions = (
            PracticeSession.query.filter_by(user_id=user.id)
            .filter(
                PracticeSession.completed_at.isnot(None),
                PracticeSession.accuracy >= (min_session_accuracy * 100),  # accuracy is stored as percentage
            )
            .all()
        )
        
        session_count = len(sessions)
        
        # Check for consecutive correct answers at the specified level
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
        
        debug_print(f"[ACHIEVEMENT DEBUG]   session_accuracy_and_consecutive: sessions={session_count} (need {min_sessions}), accuracy>={min_session_accuracy:.0%}, consecutive={has_consecutive} (need {consecutive_correct} at level {level})")
        
        if session_count >= min_sessions and has_consecutive:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (sessions: {session_count}/{min_sessions}, consecutive: {has_consecutive})")
            return []
    
    def _check_perfect_sessions(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check perfect_sessions achievements."""
        min_sessions = requirements.get("min_sessions", 0)
        level = requirements.get("level")
        
        # Count perfect sessions (100% accuracy) at this level
        perfect_sessions = (
            PracticeSession.query.filter_by(
                user_id=user.id,
                level=level,
            )
            .filter(
                PracticeSession.completed_at.isnot(None),
                PracticeSession.accuracy == 100.0,
            )
            .count()
        )
        
        debug_print(f"[ACHIEVEMENT DEBUG]   perfect_sessions: level={level}, required={min_sessions}, actual={perfect_sessions}")
        
        if perfect_sessions >= min_sessions:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (perfect_sessions: {perfect_sessions} >= {min_sessions})")
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
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_sessions}, have {perfect_sessions})")
            return []
    
    def _check_level_mastery(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check level_mastery achievements."""
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
        
        debug_print(f"[ACHIEVEMENT DEBUG]   level_mastery: level={level}, accuracy={accuracy:.2%} (need {min_accuracy:.2%}), questions={total_responses} (need {min_questions}), consecutive={has_consecutive} (need {consecutive_correct})")
        
        if total_responses >= min_questions and accuracy >= min_accuracy and has_consecutive:
            debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code}")
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
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding")
            return []


