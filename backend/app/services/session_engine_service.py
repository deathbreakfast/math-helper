"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

import json
import random
from typing import Any

from ..config.levels_config import LEVELS_CONFIG
from ..config.test_requirements import get_test_requirements
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
    
    # Add new test types from NEW_TEST_DEFINITIONS
    # Convert format: (operation, level, question_count, constraints, display_name) -> (operation, level, question_count, constraints)
    for test_type, (operation, level, question_count, constraints, _) in NEW_TEST_DEFINITIONS.items():
        TEST_TYPES[test_type] = (operation, level, question_count, constraints)
    
    # Level-based test types (levels 1-45) - will be initialized below
    LEVEL_TEST_TYPES: dict[str, tuple[str, int, int, dict[str, Any]]] = {}

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
        # Check if it's a level-based test type
        if test_type in SessionEngineService.LEVEL_TEST_TYPES:
            # Extract level from test_type (e.g., "level_1" -> 1)
            try:
                level = int(test_type.split("_")[1])
            except (ValueError, IndexError):
                return False, f"Invalid level-based test type: {test_type}"
            
            # Use new test eligibility service
            is_eligible, reason, _ = TestEligibilityService.check_test_eligibility(user, level)
            return is_eligible, reason
        
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
            if test_type in SessionEngineService.LEVEL_TEST_TYPES:
                operation, required_level, question_count, constraints = SessionEngineService.LEVEL_TEST_TYPES[test_type]
            elif test_type in SessionEngineService.TEST_TYPES:
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
            
            # Check if adaptive distribution should be applied
            # Check all levels up to user's level for failed retakes
            use_adaptive = False
            adaptive_level = None
            for level in range(1, user.level + 1):
                if AdaptiveDistributionService.should_apply_adaptive_distribution(user.id, level):
                    use_adaptive = True
                    adaptive_level = level
                    break  # Use the first level that needs adaptive distribution
            
            # Generate questions
            questions = []
            if use_adaptive and adaptive_level:
                # Use adaptive distribution
                distribution = AdaptiveDistributionService.generate_adaptive_question_distribution(
                    user, session_level
                )
                
                for i in range(question_count):
                    # Select level from distribution
                    question_level = AdaptiveDistributionService.select_level_from_distribution(distribution)
                    
                    # Get operation for the selected level
                    operation = AdaptiveDistributionService.get_operation_for_level(question_level)
                    
                    # Generate question
                    question_data = QuestionService.generate_question(
                        operation=operation,
                        level=question_level,
                        test_constraints=None,
                    )
                    questions.append(question_data)
            else:
                # Standard practice session distribution
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


def _initialize_level_test_types():
    """Initialize level-based test types from test requirements config."""
    level_test_types = {}
    for level in range(1, 46):  # Levels 1-45
        test_requirements = get_test_requirements(level)
        if test_requirements:
            level_config = LEVELS_CONFIG.get(level, {})
            operation = level_config.get("operation", "addition")
            question_count = test_requirements["question_count"]
            test_type = test_requirements["test_type"]
            # No special constraints for level-based tests
            level_test_types[test_type] = (operation, level, question_count, {})
    return level_test_types


# Initialize level test types at module load
SessionEngineService.LEVEL_TEST_TYPES = _initialize_level_test_types()
