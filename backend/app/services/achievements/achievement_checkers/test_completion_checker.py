"""Checker for test_completion, basic_math_test, test_tier, and multiplication_tests_s_rank achievements."""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from ....services.achievements.achievement_utils import debug_print
from .base_checker import AchievementChecker


class TestCompletionChecker(AchievementChecker):
    """Checker for test-related achievements."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award test completion achievements.
        
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
            if req_type not in ["test_completion", "basic_math_test", "test_tier", "multiplication_tests_s_rank"]:
                continue
            
            if achievement_code in user_achievement_codes:
                continue
            
            requirements = config.get("requirements", {})
            
            if req_type == "test_completion":
                new_achievements.extend(
                    self._check_test_completion(user, achievement_code, config, requirements, session_id)
                )
            elif req_type == "basic_math_test":
                new_achievements.extend(
                    self._check_basic_math_test(user, achievement_code, config, requirements, session_id)
                )
            elif req_type == "test_tier":
                new_achievements.extend(
                    self._check_test_tier(user, achievement_code, config, requirements, session_id)
                )
            elif req_type == "multiplication_tests_s_rank":
                new_achievements.extend(
                    self._check_multiplication_tests_s_rank(user, achievement_code, config, requirements, session_id)
                )
        
        return new_achievements
    
    def _check_test_completion(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check test_completion achievements."""
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
        
        # Check if any session meets the requirements
        for session in sessions:
            if session.total_questions >= question_count:
                accuracy = session.accuracy if session.accuracy else 0
                if accuracy >= (min_accuracy * 100):
                    debug_print(f"[ACHIEVEMENT DEBUG]   ✓ AWARDING {achievement_code} (test_completion: {test_type}, accuracy: {accuracy:.1f}% >= {min_accuracy:.0%})")
                    return [_create_achievement(
                        user_id=user.id,
                        code=achievement_code,
                        title=config["title"],
                        description=config["description"],
                        icon=config["icon"],
                        category=config["category"],
                        session_id=session_id,
                    )]
        
        debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (test_completion: {test_type})")
        return []
    
    def _check_basic_math_test(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check basic_math_test achievements."""
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
        
        return []
    
    def _check_test_tier(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check test_tier achievements."""
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
        
        debug_print(f"[ACHIEVEMENT DEBUG]   test_tier: test_type={test_type}, tier={tier}, required_accuracy={min_accuracy}, max_questions={max_question_count}")
        
        for session in sessions:
            if session.accuracy >= min_accuracy and session.total_questions <= max_question_count:
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
        
        return []
    
    def _check_multiplication_tests_s_rank(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check multiplication_tests_s_rank achievements."""
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
        
        debug_print(f"[ACHIEVEMENT DEBUG]   multiplication_tests_s_rank: all_have_s_rank={all_have_s_rank}")
        
        if all_have_s_rank:
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
            return []


