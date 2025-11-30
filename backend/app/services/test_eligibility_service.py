"""Test eligibility service for checking if users can take tests."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ..config.levels_config import LEVELS_CONFIG
from ..config.test_requirements import get_test_requirements
from ..database import log_query
from ..models import PracticeSession, Question, Response, TestAttempt, User, db


class TestEligibilityService:
    """Service for test eligibility checks."""

    @staticmethod
    @log_query
    def count_completed_sessions(user_id: int, level: int) -> int:
        """Count completed practice sessions for a user at a specific level (excluding tests)."""
        return PracticeSession.query.filter(
            PracticeSession.user_id == user_id,
            PracticeSession.level == level,
            PracticeSession.is_test == False,
            PracticeSession.completed_at.isnot(None),
        ).count()

    @staticmethod
    @log_query
    def count_missed_questions_by_level(user_id: int, level: int, days: int = 7) -> int:
        """Count missed questions for a user at a specific level in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return Response.query.join(Question).filter(
            Response.user_id == user_id,
            Response.is_correct == False,
            Question.required_level == level,
            Response.answered_at >= cutoff_date,
        ).count()

    @staticmethod
    @log_query
    def has_passed_test(user_id: int, level: int) -> bool:
        """Check if user has passed a test for a specific level."""
        test_requirements = get_test_requirements(level)
        if not test_requirements:
            return False
        
        test_type = test_requirements["test_type"]
        passing_score = test_requirements["passing_score"]
        
        # Check if there's a passed test attempt
        passed_attempt = TestAttempt.query.filter(
            TestAttempt.user_id == user_id,
            TestAttempt.level == level,
            TestAttempt.test_type == test_type,
            TestAttempt.passed == True,
        ).first()
        
        return passed_attempt is not None

    @staticmethod
    @log_query
    def has_taken_test_today(user_id: int) -> bool:
        """Check if user has taken any test today (one test per day limit)."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        test_today = TestAttempt.query.filter(
            TestAttempt.user_id == user_id,
            TestAttempt.attempted_at >= today_start,
        ).first()
        
        return test_today is not None

    @staticmethod
    @log_query
    def get_user_historical_average_time(user_id: int, level: int) -> float | None:
        """Get user's historical average time per question for a specific level from test attempts."""
        attempts = TestAttempt.query.filter(
            TestAttempt.user_id == user_id,
            TestAttempt.level == level,
            TestAttempt.avg_time_per_question_ms.isnot(None),
        ).all()
        
        if not attempts:
            return None
        
        total_time = sum(attempt.avg_time_per_question_ms for attempt in attempts if attempt.avg_time_per_question_ms)
        return total_time / len(attempts) if attempts else None

    @staticmethod
    @log_query
    def check_test_eligibility(user: User, level: int) -> tuple[bool, str, dict[str, Any]]:
        """Check if a user is eligible to take a test for a specific level.
        
        Returns:
            Tuple of (is_eligible, reason_message, eligibility_details)
        """
        eligibility_details = {
            "level": level,
            "sessions_completed": 0,
            "sessions_required": 0,
            "has_passed_before": False,
            "missed_questions_count": 0,
            "missed_questions_threshold": 0,
            "has_taken_test_today": False,
            "is_retake_eligible": False,
        }
        
        # Get test requirements for this level
        test_requirements = get_test_requirements(level)
        if not test_requirements:
            return False, f"No test requirements found for level {level}", eligibility_details
        
        sessions_required = test_requirements["sessions_required"]
        missed_threshold = test_requirements["missed_questions_threshold"]
        missed_window_days = test_requirements["missed_questions_window_days"]
        
        eligibility_details["sessions_required"] = sessions_required
        
        # Check if user has reached the required level
        if user.level < level:
            return False, f"User level {user.level} is below required level {level}", eligibility_details
        
        # Check daily limit (one test per day)
        has_taken_today = TestEligibilityService.has_taken_test_today(user.id)
        eligibility_details["has_taken_test_today"] = has_taken_today
        if has_taken_today:
            return False, "User has already taken a test today (one test per day limit)", eligibility_details
        
        # Count completed sessions
        sessions_completed = TestEligibilityService.count_completed_sessions(user.id, level)
        eligibility_details["sessions_completed"] = sessions_completed
        
        # Check if user has passed this test before
        has_passed = TestEligibilityService.has_passed_test(user.id, level)
        eligibility_details["has_passed_before"] = has_passed
        
        # Count missed questions
        missed_count = TestEligibilityService.count_missed_questions_by_level(
            user.id, level, missed_window_days
        )
        eligibility_details["missed_questions_count"] = missed_count
        eligibility_details["missed_questions_threshold"] = missed_threshold
        
        # Initial test eligibility: need required sessions
        if not has_passed:
            if sessions_completed < sessions_required:
                return False, f"User needs {sessions_required} completed sessions, has {sessions_completed}", eligibility_details
            return True, "User is eligible for initial test", eligibility_details
        
        # Retake eligibility: passed before AND missed 3+ questions in last 7 days
        if has_passed and missed_count >= missed_threshold:
            eligibility_details["is_retake_eligible"] = True
            return True, f"User is eligible for retake (missed {missed_count} questions in last {missed_window_days} days)", eligibility_details
        
        # Not eligible for retake
        return False, f"User has passed test but only missed {missed_count} questions (need {missed_threshold}+)", eligibility_details

    @staticmethod
    @log_query
    def get_available_tests(user: User) -> list[dict[str, Any]]:
        """Get all available tests a user can take (manual selection).
        
        Returns list of tests with eligibility status.
        """
        available_tests = []
        
        # Check all levels up to user's level
        for level in range(1, user.level + 1):
            test_requirements = get_test_requirements(level)
            if not test_requirements:
                continue
            
            is_eligible, reason, details = TestEligibilityService.check_test_eligibility(user, level)
            
            # Get operation from level config
            level_config = LEVELS_CONFIG.get(level, {})
            operation = level_config.get("operation", "unknown")
            
            available_tests.append({
                "level": level,
                "test_type": test_requirements["test_type"],
                "operation": operation,
                "question_count": test_requirements["question_count"],
                "passing_score": test_requirements["passing_score"],
                "is_eligible": is_eligible,
                "reason": reason,
                "eligibility_details": details,
            })
        
        return available_tests

