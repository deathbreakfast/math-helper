"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

import json
import random
from typing import Any

from ..config.tests.test_definitions import NEW_TEST_DEFINITIONS
from ..database import log_query, transaction
from ..models import User, db
from ..services.achievement_service import AchievementService
from ..services.adaptive_distribution_service import AdaptiveDistributionService
from ..services.practice_service import PracticeService
from ..services.question_service import QuestionService
from ..services.test_eligibility_service import TestEligibilityService


class SessionEngineService:
    """Service for session generation orchestration."""

    # Test type definitions: (test_type, operation, level, question_count, constraints)
    # Legacy test types (kept for backward compatibility)
    TEST_TYPES = {
    }
    
    # Add new test types from NEW_TEST_DEFINITIONS
    # Convert format: (operation, level, question_count, constraints, display_name) -> (operation, level, question_count, constraints)
    for test_type, (operation, level, question_count, constraints, _) in NEW_TEST_DEFINITIONS.items():
        TEST_TYPES[test_type] = (operation, level, question_count, constraints)

    @staticmethod
    def _get_test_achievement_code(test_type: str) -> str:
        """Get the achievement code required for a test type."""
        # Format: {test_type}_mastery
        return f"{test_type}_mastery"

    @staticmethod
    @log_query
    def check_test_eligibility(user: User, test_type: str) -> tuple[bool, str]:
        """Check if a user is eligible to take a specific test.
        
        Returns:
            Tuple of (is_eligible, error_message)
        """
        # Check if it's a new test type (descriptive identifier)
        if test_type in SessionEngineService.TEST_TYPES:
            _, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
            
            # Check level restriction
            if user.level < required_level:
                return False, f"User level {user.level} is below required level {required_level}"
            
            # For new test types, only level requirement is needed (no achievement requirement)
            # Legacy test types still require achievement
            if test_type.startswith(("addition-", "subtraction-", "multiplication-", "division-", "basic-math-")):
                # New test types: only level requirement
                return True, ""
            else:
                # Legacy test types: check achievement requirement (30 correct in a row)
                achievement_code = SessionEngineService._get_test_achievement_code(test_type)
                user_achievements = AchievementService.get_achievement_codes(user.id)
                
                if achievement_code not in user_achievements:
                    return False, f"User has not earned the '{achievement_code}' achievement (30 correct in a row)"
                
                return True, ""
        
        return False, f"Unknown test type: {test_type}"

    @staticmethod
    @log_query
    def get_eligible_tests(user: User) -> list[dict[str, Any]]:
        """Get list of eligible test types for a user."""
        eligible_tests = []
        user_achievements = AchievementService.get_achievement_codes(user.id)
        
        for test_type, (operation, required_level, question_count, constraints) in SessionEngineService.TEST_TYPES.items():
            # Check level restriction
            if user.level < required_level:
                continue
            
            # Check achievement requirement
            achievement_code = SessionEngineService._get_test_achievement_code(test_type)
            if achievement_code not in user_achievements:
                continue
            
            eligible_tests.append({
                "test_type": test_type,
                "operation": operation,
                "level": required_level,
                "question_count": question_count,
                "description": f"{operation.capitalize()} test - {test_type.replace('_', ' ')}",
            })
        
        return eligible_tests

    @staticmethod
    def _transform_session_questions_to_generate_format(questions_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform questions from get_session_with_details format to generate_session format."""
        transformed = []
        for q in questions_data:
            transformed_q = {
                "id": str(q.get("question_id", q.get("id", ""))),
                "question_id": q.get("question_id"),
                "prompt": q.get("prompt", ""),
                "operation": q.get("operation", ""),
                "operand1": q.get("operand1", 0),
                "operand2": q.get("operand2", 0),
                "correctAnswer": q.get("correctAnswer", ""),
                "difficulty": f"Level {q.get('level', 1)}",  # Default if not available
                "targetMs": 4000,  # Default if not available
                "hint": q.get("hint", ""),
                "layout": q.get("layout"),
                "answerFormat": q.get("answer_format"),
                "mathTypeLabel": q.get("math_type_label", ""),
            }
            # Include response if present
            if "response" in q:
                transformed_q["response"] = q["response"]
            transformed.append(transformed_q)
        return transformed

    @staticmethod
    @log_query
    def generate_session(
        user_id: int,
        mode: str = "standard",
        is_test: bool = False,
        test_type: str | None = None,
        level: int | None = None,
    ) -> dict[str, Any]:
        """Generate a practice or test session with questions.
        
        Checks for incomplete session first. If found, returns existing session.
        Otherwise creates a new session.
        
        Args:
            user_id: The user ID
            mode: Session mode (standard/multiplication/division)
            is_test: Whether this is a test session
            test_type: Test type identifier (required if is_test=True)
            level: Optional level override (defaults to user's level)
        
        Returns:
            Dictionary with session_id, is_test, test_type, and questions list
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Determine level
        session_level = level if level is not None else user.level
        
        # Check for incomplete session first
        incomplete_session, response_count, _ = PracticeService.get_incomplete_session(user_id, mode)
        if incomplete_session:
            # Check if it matches the requested type (test vs practice)
            if incomplete_session.is_test == is_test:
                # Get full session details with all questions
                session_data = PracticeService.get_session_with_details(incomplete_session.id)
                if session_data and session_data.get("questions"):
                    # Check if all questions are answered
                    questions = session_data["questions"]
                    all_answered = all(q.get("response") is not None for q in questions)
                    if all_answered:
                        # All questions answered but not marked complete - mark it now
                        correct_count = sum(1 for q in questions if q.get("response", {}).get("is_correct", False))
                        PracticeService.complete_session(
                            incomplete_session.id,
                            total_questions=len(questions),
                            correct_count=correct_count,
                            total_duration_ms=None
                        )
                        # Continue to create new session below
                    else:
                        # Transform questions to match generate_session format
                        questions = SessionEngineService._transform_session_questions_to_generate_format(
                            session_data["questions"]
                        )
                        return {
                            "session_id": incomplete_session.id,
                            "is_test": incomplete_session.is_test,
                            "test_type": incomplete_session.test_type,
                            "mode": incomplete_session.mode,
                            "level": incomplete_session.level,
                            "questions": questions,
                        }
        
        # No incomplete session found, create new one
        # Handle test sessions
        if is_test:
            if not test_type:
                raise ValueError("test_type is required for test sessions")
            
            # Check eligibility
            is_eligible, error_msg = SessionEngineService.check_test_eligibility(user, test_type)
            if not is_eligible:
                raise ValueError(f"Test eligibility check failed: {error_msg}")
            
            # Get test configuration
            if test_type in SessionEngineService.TEST_TYPES:
                operation, required_level, question_count, constraints = SessionEngineService.TEST_TYPES[test_type]
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            # Generate questions for test (all same type/level)
            questions = []
            for i in range(question_count):
                question_data = QuestionService.generate_question(
                    operation=operation,
                    level=required_level,
                    test_constraints=constraints,
                )
                questions.append(question_data)
            
            # Create session
            session = PracticeService.create_session(
                user_id=user_id,
                mode=mode,
                level=required_level,
                is_test=True,
                test_type=test_type,
            )
            
            # Store question IDs
            question_ids = [q.get("question_id") for q in questions if q.get("question_id")]
            if question_ids:
                with transaction():
                    session.question_ids = json.dumps(question_ids)
                    db.session.add(session)
            
            return {
                "session_id": session.id,
                "is_test": True,
                "test_type": test_type,
                "mode": mode,
                "level": required_level,
                "questions": questions,
            }
        
        # Handle practice sessions (mixed levels)
        else:
            # Default question count for practice
            question_count = 10
            
            # Always use adaptive distribution (new category-based system)
            # Category is selected at session level - all questions use same category
            distribution = AdaptiveDistributionService.generate_adaptive_question_distribution(
                user, session_level
            )
            
            # Generate questions
            questions = []
            for i in range(question_count):
                # Select level from distribution
                question_level = AdaptiveDistributionService.select_level_from_distribution(distribution)
                
                # Get operation for the selected level
                operation = AdaptiveDistributionService.get_operation_for_level(question_level)
                
                # Generate question with retry logic for invalid level configurations
                max_retries = 3
                question_data = None
                for retry in range(max_retries):
                    try:
                        question_data = QuestionService.generate_question(
                            operation=operation,
                            level=question_level,
                            test_constraints=None,
                        )
                        break  # Success, exit retry loop
                    except ValueError as e:
                        # Invalid level configuration (e.g., division by zero)
                        if retry < max_retries - 1:
                            # Try with user's current level as fallback
                            question_level = user.level
                            operation = AdaptiveDistributionService.get_operation_for_level(question_level)
                        else:
                            # Last retry failed, raise the error
                            raise
                
                if question_data:
                    questions.append(question_data)
            
            # Create session
            session = PracticeService.create_session(
                user_id=user_id,
                mode=mode,
                level=session_level,
                is_test=False,
                test_type=None,
            )
            
            # Store question IDs
            question_ids = [q.get("question_id") for q in questions if q.get("question_id")]
            if question_ids:
                with transaction():
                    session.question_ids = json.dumps(question_ids)
                    db.session.add(session)
            
            return {
                "session_id": session.id,
                "is_test": False,
                "test_type": None,
                "mode": mode,
                "level": session_level,
                "questions": questions,
            }
