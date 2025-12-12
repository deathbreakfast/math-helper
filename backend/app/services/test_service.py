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
from ..models import PracticeSession, Response, TestAttempt, User, db
from ..services.achievement_service import AchievementService
# SessionEngineService imported lazily to avoid circular import


class TestService:
    """Service for test-related operations."""

    @staticmethod
    @log_query
    def check_test_unlock_requirements(user_id: int, test_type: str) -> dict[str, Any]:
        """Check if a user meets the unlock requirements for a test.
        
        Args:
            user_id: User ID
            test_type: Test type identifier
            
        Returns:
            Dictionary with unlock status:
            {
                "is_unlocked": bool,
                "requirements_met": int,
                "requirements_total": int,
                "unlock_requirements": dict,
                "reason": str
            }
        """
        # Get test definition from NEW_TEST_DEFINITIONS
        test_def = get_test_definition(test_type)
        
        if not test_def:
            return {
                "is_unlocked": False,
                "requirements_met": 0,
                "requirements_total": 0,
                "unlock_requirements": None,
                "reason": f"Test type '{test_type}' not found",
            }
        
        # Check if test has unlock_requirements
        unlock_reqs = test_def.get("unlock_requirements")
        if not unlock_reqs:
            # Fall back to level-based check
            user = db.session.get(User, user_id)
            if not user:
                return {
                    "is_unlocked": False,
                    "requirements_met": 0,
                    "requirements_total": 0,
                    "unlock_requirements": None,
                    "reason": "User not found",
                }
            
            level_requirement = test_def.get("level_requirement", 1)
            is_unlocked = user.level >= level_requirement
            return {
                "is_unlocked": is_unlocked,
                "requirements_met": 1 if is_unlocked else 0,
                "requirements_total": 1,
                "unlock_requirements": None,
                "reason": f"Level-based: user level {user.level} {'>=' if is_unlocked else '<'} required level {level_requirement}",
            }
        
        # Achievement-based unlock check
        achievement_code = unlock_reqs.get("achievement_code")
        achievement_codes = unlock_reqs.get("achievement_codes")  # Support multiple codes
        quantity = unlock_reqs.get("quantity", 1)
        level = unlock_reqs.get("level")
        min_accuracy = unlock_reqs.get("min_accuracy")
        operation = unlock_reqs.get("operation")
        
        # Handle multiple achievement codes (new format)
        if achievement_codes and isinstance(achievement_codes, list):
            # Support per-achievement quantities (e.g., {"perfect-streak-platinum": 2, "perfect-streak-gold": 6})
            # If quantities is a dict, use per-code quantities; otherwise use global quantity
            quantities = unlock_reqs.get("quantities", {})
            if not quantities and quantity:
                # If no per-code quantities, use global quantity for all
                quantities = {code: quantity for code in achievement_codes}
            
            # Check that user has at least required quantity of each achievement code
            requirements_met = 0
            requirements_total = len(achievement_codes)
            reason_parts = []
            all_unlocked = True
            
            # Get metadata filters if provided
            metadata_filters = unlock_reqs.get("metadata_filters", {})
            
            for code in achievement_codes:
                # Get required quantity for this specific code
                required_qty = quantities.get(code, quantity if quantity else 1)
                
                # Get metadata filter for this achievement code if specified
                metadata_filter = metadata_filters.get(code) if metadata_filters else None
                
                count = AchievementService.count_achievements_by_code_with_filters(
                    user_id=user_id,
                    achievement_code=code,
                    level=None,  # Don't apply level filter for milestone achievements
                    min_accuracy=None,
                    operation=None,
                    metadata_filter=metadata_filter,
                )
                has_required = count >= required_qty
                if has_required:
                    requirements_met += 1
                else:
                    all_unlocked = False
                reason_parts.append(f"{code}: {count}/{required_qty}")
            
            is_unlocked = all_unlocked
            
            # Include achievement_codes in unlock_requirements for frontend
            unlock_reqs_with_codes = unlock_reqs.copy()
            unlock_reqs_with_codes["achievement_codes"] = achievement_codes
            if quantities:
                unlock_reqs_with_codes["quantities"] = quantities
            
            return {
                "is_unlocked": is_unlocked,
                "requirements_met": requirements_met,
                "requirements_total": requirements_total,
                "unlock_requirements": unlock_reqs_with_codes,
                "reason": ", ".join(reason_parts),
            }
        
        # Handle single achievement code (backward compatible)
        # If achievement_code is missing but we have test_type, derive it from test_type
        # Default quantity to 10 if not specified (common requirement for test unlocks)
        if not achievement_code:
            # Use test type pattern matching (counts all tiers for this test type)
            if quantity is None:
                quantity = 10  # Default to 10 achievements
            count = AchievementService.count_achievements_by_test_type_with_filters(
                user_id=user_id,
                test_type=test_type,
                level=level,
                min_accuracy=min_accuracy,
                operation=operation,
            )
            achievement_code_display = f"{test_type} achievements"
        else:
            # Use specific achievement code
            if quantity is None:
                quantity = 1  # Default to 1 if specific code is provided
            
            # Get metadata filter if provided
            metadata_filter = unlock_reqs.get("metadata_filter")
            
            count = AchievementService.count_achievements_by_code_with_filters(
                user_id=user_id,
                achievement_code=achievement_code,
                level=level,
                min_accuracy=min_accuracy,
                operation=operation,
                metadata_filter=metadata_filter,
            )
            achievement_code_display = achievement_code
        
        is_unlocked = count >= quantity
        
        reason_parts = [f"{count}/{quantity} {achievement_code_display}"]
        if level is not None:
            reason_parts.append(f"at level {level}")
        if min_accuracy is not None:
            reason_parts.append(f"with {min_accuracy * 100:.0f}%+ accuracy")
        if operation is not None:
            reason_parts.append(f"for {operation}")
        
        return {
            "is_unlocked": is_unlocked,
            "requirements_met": count,
            "requirements_total": quantity,
            "unlock_requirements": unlock_reqs,
            "reason": " ".join(reason_parts),
        }

    @staticmethod
    @log_query
    def get_all_test_definitions(user_level: int | None = None, user_id: int | None = None, include_unlock_status: bool = False) -> list[dict[str, Any]]:
        """Get all test definitions.
        
        Args:
            user_level: Optional user level to filter available tests (deprecated, use unlock_status instead)
            user_id: Optional user ID to check unlock status
            include_unlock_status: If True and user_id provided, include unlock_status for each test
            
        Returns:
            List of test definition dictionaries
        """
        definitions = []
        
        # Add all test definitions from NEW_TEST_DEFINITIONS
        for test_def in get_all_test_definitions():
            if test_def:
                definitions.append(test_def)
        
        # Add unlock status if requested
        if include_unlock_status and user_id:
            for test_def in definitions:
                unlock_status = TestService.check_test_unlock_requirements(user_id, test_def["test_type"])
                test_def["unlock_status"] = unlock_status
        
        # Filter by level if provided (backward compatibility)
        if user_level is not None and not include_unlock_status:
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
        attempt = db.session.get(TestAttempt, attempt_id)
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

