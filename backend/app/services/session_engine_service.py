"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

import json
import random
import re
from typing import Any

from ..database import log_query, transaction
from ..models import User, db
from ..services.level_config_service import LevelConfigService
from ..services.practice_service import PracticeService
from ..services.question_service import QuestionService


class SessionEngineService:
    """Service for session generation orchestration."""

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
    def _concept_id_from_legacy_level(level: int) -> str:
        """Build a new-format concept ID from a legacy level number."""
        return f"c_concept_{level:03d}"

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
        level: int | None = None,
        concept_id: str | None = None,
        resume_oldest: bool = False,
    ) -> dict[str, Any]:
        """Generate a practice session with questions.
        
        Checks for incomplete session first. If found, returns existing session.
        Otherwise creates a new session.
        
        Args:
            user_id: The user ID
            mode: Session mode (standard/multiplication/division)
            level: Optional level override (defaults to user's level)
            concept_id: Optional concept identifier (e.g., "c_concept_001", "c_add_1s")
            resume_oldest: If True, resume the oldest incomplete session (for dashboard)
        
        Returns:
            Dictionary with session_id, mode, level, concept_id, and questions list
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
            # For concept-specific practice, concept_id must match.
            # For dashboard resume (resume_oldest) and general practice (no concept_id), allow resume.
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
            if level_matches and concept_matches:
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
                            "mode": incomplete_session.mode,
                            "level": incomplete_session.level,
                            "concept_id": incomplete_session.concept_id,
                            "questions": questions,
                        }
        
        # No incomplete session found, create new one
        # Default question count for practice
        question_count = 10

        # Concept-based default practice selection.
        # IMPORTANT: do this *after* checking for incomplete sessions above so that
        # general practice (no concept_id provided) can still resume any incomplete session.
        if concept_id is None:
            max_level = min(max(user.level or 1, 1), 45)
            selected_level = random.randint(1, max_level)
            concept_id = SessionEngineService._concept_id_from_legacy_level(selected_level)
            session_level = selected_level

        concept_level = SessionEngineService._extract_legacy_level_from_concept_id(concept_id)
        if concept_level is None:
            raise ValueError(f"Unsupported concept_id for practice session: {concept_id}")

        # Generate all questions from the concept's level config
        config = LevelConfigService.get_level_config(concept_level)
        if not config:
            raise ValueError(f"Concept {concept_id} (level {concept_level}) configuration not found")

        operation = config["operation"]
        questions: list[dict[str, Any]] = []

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
            
        # Create session (pass concept_id if provided)
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
            "mode": mode,
            "level": session_level,
            "concept_id": concept_id,
            "questions": questions,
        }
