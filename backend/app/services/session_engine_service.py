"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

import random
from typing import Any

from ..database import log_query
from ..models import User
from ..services.achievement_service import AchievementService
from ..services.practice_service import PracticeService
from ..services.question_service import QuestionService


class SessionEngineService:
    """Service for session generation orchestration."""

    # Test type definitions: (test_type, operation, level, question_count, constraints)
    TEST_TYPES = {
        # Multiplication tables (levels 9-21)
        "multiplication_1": ("multiplication", 9, 20, {"multiplication_table": 1}),
        "multiplication_2": ("multiplication", 10, 20, {"multiplication_table": 2}),
        "multiplication_3": ("multiplication", 11, 20, {"multiplication_table": 3}),
        "multiplication_4": ("multiplication", 12, 20, {"multiplication_table": 4}),
        "multiplication_5": ("multiplication", 13, 20, {"multiplication_table": 5}),
        "multiplication_6": ("multiplication", 14, 20, {"multiplication_table": 6}),
        "multiplication_7": ("multiplication", 15, 20, {"multiplication_table": 7}),
        "multiplication_8": ("multiplication", 16, 20, {"multiplication_table": 8}),
        "multiplication_9": ("multiplication", 17, 20, {"multiplication_table": 9}),
        "multiplication_0": ("multiplication", 18, 20, {"multiplication_table": 0}),
        "multiplication_10": ("multiplication", 19, 20, {"multiplication_table": 10}),
        "multiplication_11": ("multiplication", 20, 20, {"multiplication_table": 11}),
        "multiplication_12": ("multiplication", 21, 20, {"multiplication_table": 12}),
        # Division tables (levels 26-37)
        "division_1": ("division", 26, 20, {"division_table": 1}),
        "division_2": ("division", 27, 20, {"division_table": 2}),
        "division_3": ("division", 28, 20, {"division_table": 3}),
        "division_4": ("division", 29, 20, {"division_table": 4}),
        "division_5": ("division", 30, 20, {"division_table": 5}),
        "division_6": ("division", 31, 20, {"division_table": 6}),
        "division_7": ("division", 32, 20, {"division_table": 7}),
        "division_8": ("division", 33, 20, {"division_table": 8}),
        "division_9": ("division", 34, 20, {"division_table": 9}),
        "division_10": ("division", 35, 20, {"division_table": 10}),
        "division_11": ("division", 36, 20, {"division_table": 11}),
        "division_12": ("division", 37, 20, {"division_table": 12}),
        # Legacy division tests (kept for backward compatibility)
        "division_2digit": ("division", 4, 30, {"division_digits": 2}),
        "division_3digit": ("division", 4, 40, {"division_digits": 3}),
        "division_fraction": ("division", 4, 30, {"answer_format": "fraction"}),
        "division_decimal": ("division", 4, 30, {"answer_format": "decimal"}),
    }

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
        if test_type not in SessionEngineService.TEST_TYPES:
            return False, f"Unknown test type: {test_type}"
        
        _, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
        
        # Check level restriction
        if user.level < required_level:
            return False, f"User level {user.level} is below required level {required_level}"
        
        # Check achievement requirement (30 correct in a row)
        achievement_code = SessionEngineService._get_test_achievement_code(test_type)
        user_achievements = AchievementService.get_achievement_codes(user.id)
        
        if achievement_code not in user_achievements:
            return False, f"User has not earned the '{achievement_code}' achievement (30 correct in a row)"
        
        return True, ""

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
    @log_query
    def generate_session(
        user_id: int,
        mode: str = "standard",
        is_test: bool = False,
        test_type: str | None = None,
        level: int | None = None,
    ) -> dict[str, Any]:
        """Generate a practice or test session with questions.
        
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
        
        # Handle test sessions
        if is_test:
            if not test_type:
                raise ValueError("test_type is required for test sessions")
            
            # Check eligibility
            is_eligible, error_msg = SessionEngineService.check_test_eligibility(user, test_type)
            if not is_eligible:
                raise ValueError(f"Test eligibility check failed: {error_msg}")
            
            # Get test configuration
            if test_type not in SessionEngineService.TEST_TYPES:
                raise ValueError(f"Unknown test type: {test_type}")
            
            operation, required_level, question_count, constraints = SessionEngineService.TEST_TYPES[test_type]
            
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
            
            return {
                "session_id": session.id,
                "is_test": True,
                "test_type": test_type,
                "level": required_level,
                "questions": questions,
            }
        
        # Handle practice sessions (mixed levels)
        else:
            # Default question count for practice
            question_count = 10
            
            # Determine operations based on mode and level
            operations = []
            if mode == "multiplication":
                operations = ["multiplication"]
            elif mode == "division":
                operations = ["division"]
            else:
                # Standard mode - mix operations based on level
                if session_level == 1:
                    operations = ["addition", "subtraction"]
                elif session_level == 2:
                    operations = ["addition", "subtraction"]
                elif session_level == 3:
                    operations = ["multiplication"]
                elif session_level == 4:
                    operations = ["division"]
                else:
                    operations = QuestionService.OPERATIONS
            
            # Generate questions with mixed levels for practice
            questions = []
            for i in range(question_count):
                # Mix levels: 70% current level, 20% level-1, 10% level-2 (if available)
                rand = random.random()
                if rand < 0.7:
                    question_level = session_level
                elif rand < 0.9 and session_level > 1:
                    question_level = session_level - 1
                elif session_level > 2:
                    question_level = session_level - 2
                else:
                    question_level = session_level
                
                # Ensure level is at least 1
                question_level = max(1, question_level)
                
                # Select operation
                operation = random.choice(operations)
                
                # Generate question
                question_data = QuestionService.generate_question(
                    operation=operation,
                    level=question_level,
                    test_constraints=None,
                )
                questions.append(question_data)
            
            # Create session
            session = PracticeService.create_session(
                user_id=user_id,
                mode=mode,
                level=session_level,
                is_test=False,
                test_type=None,
            )
            
            return {
                "session_id": session.id,
                "is_test": False,
                "test_type": None,
                "level": session_level,
                "questions": questions,
            }

