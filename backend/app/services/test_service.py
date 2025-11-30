"""Test service for managing test definitions, attempts, and detailed results."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..config.test_requirements import get_test_requirements
from ..config.tests.test_definitions import (
    NEW_TEST_DEFINITIONS,
    get_all_test_definitions,
    get_test_definition,
    get_test_definitions_by_level,
)
from ..database import log_query
from ..models import PracticeSession, Response, TestAttempt, db
from ..services.session_engine_service import SessionEngineService


class TestService:
    """Service for test-related operations."""

    @staticmethod
    @log_query
    def get_all_test_definitions(user_level: int | None = None) -> list[dict[str, Any]]:
        """Get all test definitions (legacy + new).
        
        Args:
            user_level: Optional user level to filter available tests
            
        Returns:
            List of test definition dictionaries
        """
        definitions = []
        
        # Add legacy level-based tests
        for test_type, (operation, level, question_count, constraints) in SessionEngineService.LEVEL_TEST_TYPES.items():
            test_req = get_test_requirements(level)
            definitions.append({
                "test_type": test_type,
                "operation": operation,
                "level_requirement": level,
                "question_count": question_count,
                "constraints": constraints,
                "display_name": f"Level {level} Test",
                "is_legacy": True,
            })
        
        # Add legacy operation-based tests
        for test_type, (operation, level, question_count, constraints) in SessionEngineService.TEST_TYPES.items():
            # Skip new test types (they'll be added separately)
            if test_type in NEW_TEST_DEFINITIONS:
                continue
                
            definitions.append({
                "test_type": test_type,
                "operation": operation,
                "level_requirement": level,
                "question_count": question_count,
                "constraints": constraints,
                "display_name": test_type.replace("_", " ").title(),
                "is_legacy": True,
            })
        
        # Add new test definitions
        for test_def in get_all_test_definitions():
            if test_def:
                test_def["is_legacy"] = False
                definitions.append(test_def)
        
        # Filter by level if provided
        if user_level is not None:
            definitions = [d for d in definitions if d["level_requirement"] <= user_level]
        
        return definitions

    @staticmethod
    @log_query
    def get_test_attempts(user_id: int, test_type: str | None = None) -> list[dict[str, Any]]:
        """Get test attempts for a user, optionally filtered by test type.
        
        Args:
            user_id: User ID
            test_type: Optional test type filter
            
        Returns:
            List of test attempt dictionaries, ordered by most recent first
        """
        query = TestAttempt.query.filter_by(user_id=user_id)
        
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        attempts = query.order_by(TestAttempt.attempted_at.desc()).all()
        
        return [
            {
                "attempt_id": attempt.id,
                "user_id": attempt.user_id,
                "level": attempt.level,
                "test_type": attempt.test_type,
                "score": attempt.score,
                "accuracy": attempt.score * 100,  # Convert to percentage
                "avg_time_per_question_ms": attempt.avg_time_per_question_ms,
                "total_duration_ms": attempt.total_duration_ms,
                "passed": attempt.passed,
                "attempted_at": attempt.attempted_at.isoformat() if attempt.attempted_at else None,
                "tier": TestService._calculate_tier(
                    attempt.score,
                    attempt.avg_time_per_question_ms,
                    None,  # Question count not available in attempt list
                ),
            }
            for attempt in attempts
        ]

    @staticmethod
    @log_query
    def get_test_attempt_detail(attempt_id: int) -> dict[str, Any] | None:
        """Get detailed test attempt with all questions and responses.
        
        Args:
            attempt_id: Test attempt ID
            
        Returns:
            Dictionary with attempt details and questions/responses, or None if not found
        """
        attempt = TestAttempt.query.get(attempt_id)
        if not attempt:
            return None
        
        # Find the practice session associated with this test attempt
        # Match by user_id, test_type, level, and completion time
        session = (
            PracticeSession.query.filter_by(
                user_id=attempt.user_id,
                test_type=attempt.test_type,
                level=attempt.level,
                is_test=True,
            )
            .filter(PracticeSession.completed_at.isnot(None))
            .order_by(PracticeSession.completed_at.desc())
            .first()
        )
        
        # If we can't find exact match, try to find by time proximity
        if not session:
            # Find sessions completed around the same time
            time_window_start = attempt.attempted_at.replace(second=0, microsecond=0)
            time_window_end = attempt.attempted_at.replace(second=59, microsecond=999999)
            
            session = (
                PracticeSession.query.filter_by(
                    user_id=attempt.user_id,
                    test_type=attempt.test_type,
                    level=attempt.level,
                    is_test=True,
                )
                .filter(
                    PracticeSession.completed_at >= time_window_start,
                    PracticeSession.completed_at <= time_window_end,
                )
                .order_by(PracticeSession.completed_at.desc())
                .first()
            )
        
        questions_data = []
        if session:
            # Get all responses for this session
            responses = Response.query.filter_by(session_id=session.id).order_by(Response.answered_at).all()
            
            # Get question details
            for response in responses:
                question = response.question
                if question:
                    questions_data.append({
                        "question_id": question.id,
                        "prompt": question.prompt,
                        "operation": question.operation,
                        "operand1": question.operand1,
                        "operand2": question.operand2,
                        "correct_answer": question.correct_answer,
                        "user_answer": response.submitted_answer,
                        "is_correct": response.is_correct,
                        "time_taken_ms": response.duration_ms,
                        "answered_at": response.answered_at.isoformat() if response.answered_at else None,
                    })
        
        # Calculate tier
        question_count = len(questions_data) if questions_data else None
        # If we have question count from questions, use it; otherwise try to infer from session
        if question_count is None and session:
            question_count = session.total_questions or None
        tier = TestService._calculate_tier(attempt.score, attempt.avg_time_per_question_ms, question_count)
        
        return {
            "attempt_id": attempt.id,
            "user_id": attempt.user_id,
            "level": attempt.level,
            "test_type": attempt.test_type,
            "score": attempt.score,
            "accuracy": attempt.score * 100,
            "avg_time_per_question_ms": attempt.avg_time_per_question_ms,
            "total_duration_ms": attempt.total_duration_ms,
            "passed": attempt.passed,
            "attempted_at": attempt.attempted_at.isoformat() if attempt.attempted_at else None,
            "tier": tier,
            "questions": questions_data,
        }

    @staticmethod
    def _calculate_tier(
        accuracy: float,
        avg_time_per_question_ms: int | None,
        question_count: int | None,
    ) -> str:
        """Calculate tier rank (B, A, S, SS, SSS) based on accuracy, speed, and question count.
        
        Args:
            accuracy: Accuracy as decimal (0.0 to 1.0)
            avg_time_per_question_ms: Average time per question in milliseconds
            question_count: Number of questions in the test
            
        Returns:
            Tier rank: "B", "A", "S", "SS", or "SSS"
        """
        if accuracy < 1.0:  # Not 100% accurate
            return "B"
        
        if question_count is None:
            # If we don't have question count, use time-based tiering
            if avg_time_per_question_ms is None:
                return "B"
            
            avg_time_seconds = avg_time_per_question_ms / 1000.0
            
            if avg_time_seconds <= 3.0:
                return "SSS"
            elif avg_time_seconds <= 4.0:
                return "SS"
            elif avg_time_seconds <= 6.0:
                return "S"
            else:
                return "A"
        
        # Tier calculation with question count
        if question_count < 30:
            return "A"  # 100% accuracy, <30 questions
        
        if question_count >= 90:
            # 90+ questions
            if avg_time_per_question_ms is None:
                return "B"
            avg_time_seconds = avg_time_per_question_ms / 1000.0
            if avg_time_seconds <= 3.0:
                return "SSS"
            else:
                return "SS"
        
        # 31-89 questions
        if avg_time_per_question_ms is None:
            return "B"
        
        avg_time_seconds = avg_time_per_question_ms / 1000.0
        
        if question_count <= 59:
            # 31-59 questions
            if avg_time_seconds <= 6.0:
                return "S"
            else:
                return "B"
        else:
            # 60-89 questions
            if avg_time_seconds <= 4.0:
                return "SS"
            else:
                return "S"

