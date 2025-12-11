"""Checker for other achievement types not handled by specialized checkers.

This includes:
- operation_count
- level_accuracy
- level_correct_count
- session_accuracy_and_consecutive
- test_completion
- perfect_sessions
- achievement_count_by_category
"""

from __future__ import annotations

from typing import Any

from ....models import Achievement, PracticeSession, Question, Response, User, db
from ....utils.tier_utils import extract_base_code_and_tier, get_tier_value, ALL_TIERS
from ....services.achievement_service import AchievementService
from ....services.achievements.achievement_utils import debug_print
from ....services.achievements.achievement_utils import create_achievement as _create_achievement
from .base_checker import AchievementChecker
from sqlalchemy import func


class OtherAchievementsChecker(AchievementChecker):
    """Checker for other achievement types."""
    
    def check(self, user: User, session_id: int | None = None) -> list[Achievement]:
        """Check and award other achievement types.
        
        Args:
            user: User to check achievements for
            session_id: Optional session ID to link achievements to a specific session
            
        Returns:
            List of newly created achievements
        """
        achievement_configs = self.achievement_configs
        new_achievements = []
        user_achievement_codes = AchievementService.get_achievement_codes(user.id)
        
        debug_print(f"[ACHIEVEMENT DEBUG] check_level_specific_achievements: User {user.id} (level {user.level})")
        debug_print(f"[ACHIEVEMENT DEBUG] Checking {len(achievement_configs)} achievement configs")
        debug_print(f"[ACHIEVEMENT DEBUG] User already has {len(user_achievement_codes)} achievements: {sorted(user_achievement_codes)}")
        
        # Collect other achievements (not handled by LevelAchievementChecker)
        other_achievements = []
        
        for achievement_code, config in achievement_configs.items():
            req_type = config.get("requirements", {}).get("type")
            # Skip achievements handled by LevelAchievementChecker
            if achievement_code.startswith("perfect-streak-"):
                continue
            other_achievements.append((achievement_code, config))
        
        # Process other achievements (non-tiered)
        for achievement_code, config in other_achievements:
            # Skip if already earned
            if achievement_code in user_achievement_codes:
                continue
            
            debug_print(f"[ACHIEVEMENT DEBUG] Checking achievement: {achievement_code} - {config.get('title')}")
            
            # Check operation_count achievements
            if req_type == "operation_count":
                new_achievements.extend(self._check_operation_count(user, achievement_code, config, requirements, session_id))
            
            # Check level_accuracy achievements
            elif req_type == "level_accuracy":
                new_achievements.extend(self._check_level_accuracy(user, achievement_code, config, requirements, session_id))
            
            # Check level_correct_count achievements
            elif req_type == "level_correct_count":
                new_achievements.extend(self._check_level_correct_count(user, achievement_code, config, requirements, session_id))
            
            # Check session_accuracy_and_consecutive achievements
            elif req_type == "session_accuracy_and_consecutive":
                new_achievements.extend(self._check_session_accuracy_and_consecutive(user, achievement_code, config, requirements, session_id))
            
            # Check test_completion achievements
            elif req_type == "test_completion":
                new_achievements.extend(self._check_test_completion(user, achievement_code, config, requirements, session_id))
            
            # Check perfect_sessions achievements
            elif req_type == "perfect_sessions":
                new_achievements.extend(self._check_perfect_sessions(user, achievement_code, config, requirements, session_id))
            
            # Check achievement_count_by_category achievements
            elif req_type == "achievement_count_by_category":
                new_achievements.extend(self._check_achievement_count_by_category(user, achievement_code, config, requirements, session_id))
            
            # Check basic_math_test achievements
            elif req_type == "basic_math_test":
                new_achievements.extend(self._check_basic_math_test(user, achievement_code, config, requirements, session_id))
            
            # Check level_mastery achievements
            elif req_type == "level_mastery":
                new_achievements.extend(self._check_level_mastery(user, achievement_code, config, requirements, session_id))
            
            # Check test_tier achievements
            elif req_type == "test_tier":
                new_achievements.extend(self._check_test_tier(user, achievement_code, config, requirements, session_id))
            
            # Check multiplication_tests_s_rank achievements
            elif req_type == "multiplication_tests_s_rank":
                new_achievements.extend(self._check_multiplication_tests_s_rank(user, achievement_code, config, requirements, session_id))
        
        return new_achievements
    
    def _check_operation_count(
        self, user: User, achievement_code: str, config: dict[str, Any], 
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check operation_count achievements."""
        operation = requirements.get("operation")
        count = requirements.get("count", 0)
        level = requirements.get("level")
        
        # Count correct answers for this operation at this level
        correct_count = (
            db.session.query(func.count())
            .select_from(Response)
            .join(Question)
            .filter(
                Response.user_id == user.id,
                Response.is_correct == True,
                Question.operation == operation,
                Question.required_level == level,
            )
            .scalar()
            or 0
        )
        
        debug_print(f"[ACHIEVEMENT DEBUG]   operation_count: operation={operation}, level={level}, required={count}, actual={correct_count}")
        
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
        return [create_achievement(
            user_id=user.id,
            code=achievement_code,
            title=config["title"],
            description=config["description"],
            icon=config["icon"],
            category=config["category"],
            session_id=session_id,
        )]
    
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
    
    def _check_achievement_count_by_category(
        self, user: User, achievement_code: str, config: dict[str, Any],
        requirements: dict[str, Any], session_id: int | None
    ) -> list[Achievement]:
        """Check achievement_count_by_category achievements."""
        category = requirements.get("category")
        min_count = requirements.get("min_count", 0)
        min_tier = requirements.get("min_tier")
        
        # Get all user achievements in this category
        user_achievements = Achievement.query.filter_by(
            user_id=user.id,
            category=category,
        ).all()
        
        # Count achievements that meet the minimum tier requirement
        matching_count = 0
        tier_hierarchy = {tier.lower(): get_tier_value(tier) for tier in ALL_TIERS}
        min_tier_value = tier_hierarchy.get(min_tier.lower(), 1) if min_tier else 0
        
        for ach in user_achievements:
            _, ach_tier = extract_base_code_and_tier(ach.code)
            if not min_tier or not ach_tier:
                # If no tier requirement or achievement has no tier, count it
                matching_count += 1
            else:
                ach_tier_value = tier_hierarchy.get(ach_tier.lower(), 1)
                if ach_tier_value >= min_tier_value:
                    matching_count += 1
        
        debug_print(f"[ACHIEVEMENT DEBUG]   achievement_count_by_category: category={category}, min_tier={min_tier}, required={min_count}, actual={matching_count}")
        
        if matching_count >= min_count:
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
            debug_print(f"[ACHIEVEMENT DEBUG]   ✗ Not awarding (need {min_count}, have {matching_count})")
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

