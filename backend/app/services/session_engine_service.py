"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

import json
import random
import re
from typing import Any

from ..config.tests.test_definitions import NEW_TEST_DEFINITIONS
from ..database import log_query, transaction
from ..models import User, db
from ..services.achievement_service import AchievementService
from ..services.adaptive_distribution_service import AdaptiveDistributionService
from ..services.level_config_service import LevelConfigService
from ..services.practice_service import PracticeService
from ..services.question_service import QuestionService
from ..services.test_eligibility_service import TestEligibilityService


class SessionEngineService:
    """Service for session generation orchestration."""

    # Test type definitions: (test_type, operation, level, question_count, constraints)
    # Populated from NEW_TEST_DEFINITIONS
    TEST_TYPES = {}
    
    # Add test types from NEW_TEST_DEFINITIONS
    # Convert format: (operation, level, question_count, constraints, display_name) -> (operation, level, question_count, constraints)
    for test_type, (operation, level, question_count, constraints, _) in NEW_TEST_DEFINITIONS.items():
        TEST_TYPES[test_type] = (operation, level, question_count, constraints)

    @staticmethod
    def _extract_legacy_level_from_concept_id(concept_id: str | None) -> int | None:
        """Extract legacy level number from concept ID.
        
        Supports:
        - Old format: c_level_1 -> 1
        - New format: c_concept_001 -> 1
        - Descriptive format: c_add_1s -> None (no legacy level mapping)
        
        Args:
            concept_id: The concept ID to parse
            
        Returns:
            The legacy level number if found, None otherwise
        """
        if not concept_id:
            return None
        
        # Old format: c_level_1, c_level_2, etc.
        old_format_match = re.match(r'^c_level_(\d+)$', concept_id)
        if old_format_match:
            return int(old_format_match.group(1))
        
        # New format: c_concept_001, c_concept_002, etc.
        new_format_match = re.match(r'^c_concept_(\d+)$', concept_id)
        if new_format_match:
            return int(new_format_match.group(1))
        
        # Descriptive format (c_add_1s, c_sub_2s, etc.) - no legacy level mapping
        return None


    @staticmethod
    @log_query
    def check_test_eligibility(user: User, test_type: str) -> tuple[bool, str]:
        """Check if a user is eligible to take a specific test.
        
        Returns:
            Tuple of (is_eligible, error_message)
        """
        # Check if it's a valid test type
        if test_type in SessionEngineService.TEST_TYPES:
            _, required_level, _, _ = SessionEngineService.TEST_TYPES[test_type]
            
            # Check level restriction
            if user.level < required_level:
                return False, f"User level {user.level} is below required level {required_level}"
            
            # All test types only require level (no achievement requirement)
            return True, ""
        
        return False, f"Unknown test type: {test_type}"

    @staticmethod
    def _get_test_achievement_code(test_type: str) -> str:
        """Get the achievement code format for a test type (for backward compatibility).
        
        Note: This method is kept for backward compatibility but is no longer used
        in the eligibility checking logic.
        """
        return f"{test_type}_mastery"

    @staticmethod
    @log_query
    def get_eligible_tests(user: User) -> list[dict[str, Any]]:
        """Get list of eligible test types for a user.
        
        Tests are eligible if the user's level meets the test's level requirement.
        No achievement requirement is needed.
        """
        eligible_tests = []
        
        for test_type, (operation, required_level, question_count, constraints) in SessionEngineService.TEST_TYPES.items():
            # Check level restriction
            if user.level < required_level:
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
        concept_id: str | None = None,
        resume_oldest: bool = False,
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
            concept_id: Optional concept identifier (e.g., "c_concept_001", "c_add_1s")
            resume_oldest: If True, resume the oldest incomplete session (for dashboard)
        
        Returns:
            Dictionary with session_id, is_test, test_type, and questions list
        """
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Determine level
        session_level = level if level is not None else user.level
        
        # Check for incomplete session first
        # If resume_oldest is True (dashboard), get oldest session
        # Otherwise, if concept_id is provided, only resume matching concept sessions
        if resume_oldest:
            incomplete_session, response_count, _ = PracticeService.get_oldest_incomplete_session(user_id, mode)
        else:
            incomplete_session, response_count, _ = PracticeService.get_incomplete_session(
                user_id, mode, concept_id=concept_id
            )
        
        if incomplete_session:
            # Check if it matches the requested type (test vs practice)
            # For concept-specific practice, concept_id must match
            # For dashboard resume (resume_oldest), we resume any incomplete session
            concept_matches = (
                incomplete_session.concept_id == concept_id
                if concept_id is not None
                else True  # If no concept_id specified, allow resume
            )
            level_matches = (
                incomplete_session.level == session_level 
                if session_level is not None and incomplete_session.level is not None
                else True  # If either is None, allow resume (backward compatibility)
            )
            if incomplete_session.is_test == is_test and level_matches and concept_matches:
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
                            "concept_id": incomplete_session.concept_id,
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
            
            # Create session (concept_id should already be passed from caller)
            session = PracticeService.create_session(
                user_id=user_id,
                mode=mode,
                level=required_level,
                concept_id=concept_id,
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
                "concept_id": concept_id,
                "questions": questions,
            }
        
        # Handle practice sessions (mixed levels)
        else:
            # Default question count for practice
            question_count = 10
            
            # If concept_id is provided, generate questions from that concept's config
            # Otherwise, use adaptive distribution (new category-based system)
            concept_level = SessionEngineService._extract_legacy_level_from_concept_id(concept_id)
            
            if concept_id and concept_level is not None:
                # Generate all questions from the concept's level config
                config = LevelConfigService.get_level_config(concept_level)
                if not config:
                    raise ValueError(f"Concept {concept_id} (level {concept_level}) configuration not found")
                
                operation = config["operation"]
                questions = []
                
                for i in range(question_count):
                    max_retries = 3
                    question_data = None
                    for retry in range(max_retries):
                        try:
                            question_data = QuestionService.generate_question(
                                operation=operation,
                                level=concept_level,
                                test_constraints=None,
                            )
                            break  # Success, exit retry loop
                        except ValueError:
                            # Invalid level configuration (e.g., division by zero)
                            if retry >= max_retries - 1:
                                raise
                    
                    if question_data:
                        questions.append(question_data)
            else:
                # Use adaptive distribution (category-based system)
                # Category is selected at session level - all questions use same category
                distribution = AdaptiveDistributionService.generate_adaptive_question_distribution(
                    user, session_level
                )
                
                # Detect if this is a Type A distribution (single level with weight 1.0)
                # Type A: All questions use same level (e.g., Level Category Type A, Random category)
                # Type B: Each question selects from distribution (e.g., Level Category Type B)
                is_type_a = len(distribution) == 1 and distribution[0].get("weight", 0) >= 0.99
                
                # Generate questions
                questions = []
                
                if is_type_a:
                    # Type A: Use the single level for all questions (more efficient)
                    selected_level = distribution[0]["level"]
                    operation = AdaptiveDistributionService.get_operation_for_level(selected_level)
                    
                    for i in range(question_count):
                        max_retries = 3
                        question_data = None
                        for retry in range(max_retries):
                            try:
                                question_data = QuestionService.generate_question(
                                    operation=operation,
                                    level=selected_level,
                                    test_constraints=None,
                                )
                                break  # Success, exit retry loop
                            except ValueError:
                                # Invalid level configuration (e.g., division by zero)
                                # Retry without changing level to preserve distribution integrity.
                                if retry >= max_retries - 1:
                                    # Exhausted retries: raise so callers/tests can detect failure.
                                    raise
                        
                        if question_data:
                            questions.append(question_data)
                else:
                    # Type B: Select level from distribution for each question
                    for i in range(question_count):
                        # Select level from distribution
                        selected_level = AdaptiveDistributionService.select_level_from_distribution(distribution)
                        
                        # Get operation for the selected level
                        operation = AdaptiveDistributionService.get_operation_for_level(selected_level)
                        
                        # Generate question with retry logic for invalid level configurations
                        # CRITICAL: Always preserve the originally selected level to maintain distribution
                        # Changing the level breaks the distribution statistics
                        max_retries = 3
                        question_data = None
                        for retry in range(max_retries):
                            try:
                                question_data = QuestionService.generate_question(
                                    operation=operation,
                                    level=selected_level,  # Always use originally selected level
                                    test_constraints=None,
                                )
                                break  # Success, exit retry loop
                            except ValueError:
                                # Invalid level configuration (e.g., division by zero)
                                # Retry without changing level to preserve distribution integrity.
                                if retry >= max_retries - 1:
                                    # Exhausted retries: raise so callers/tests can detect failure.
                                    raise
                        
                        if question_data:
                            questions.append(question_data)
            
            # Create session (pass concept_id if provided)
            # Note: questions should already be populated from either concept-based or adaptive generation above
            session = PracticeService.create_session(
                user_id=user_id,
                mode=mode,
                level=session_level,
                concept_id=concept_id,
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
                "concept_id": concept_id,
                "questions": questions,
            }
