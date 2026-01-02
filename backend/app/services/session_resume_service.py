"""Service for handling session resumption logic."""

from __future__ import annotations

from typing import Any

from ..models import User
from ..services.practice_service import PracticeService


class SessionResumeService:
    """Service for resume selection and validation."""

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
    def find_resumable_session(
        user_id: int,
        mode: str,
        concept_id: str | None = None,
        resume_oldest: bool = False,
    ) -> tuple[Any | None, dict[str, Any] | None]:
        """Find a resumable session for the user.
        
        Args:
            user_id: The user ID
            mode: Session mode (standard/multiplication/division)
            concept_id: Optional concept identifier filter
            resume_oldest: If True, resume the oldest incomplete session (for dashboard)
        
        Returns:
            Tuple of (incomplete_session, session_data_dict or None)
            If a resumable session is found, returns the session and its transformed data.
            If not found, returns (None, None).
        """
        # Get incomplete session based on resume mode
        if resume_oldest:
            incomplete_session, response_count, _ = PracticeService.get_oldest_incomplete_session(user_id, mode)
        else:
            incomplete_session, response_count, _ = PracticeService.get_incomplete_session(
                user_id, mode, concept_id=concept_id
            )
        
        if not incomplete_session:
            return None, None
        
        # Validate that the session matches the requested concept_id (no level filtering)
        concept_matches = (
            incomplete_session.concept_id == concept_id
            if concept_id is not None
            else True  # If no concept_id specified, allow resume
        )
        
        if not concept_matches:
            return None, None
        
        # Get full session details with all questions
        session_data = PracticeService.get_session_with_details(incomplete_session.id)
        if not session_data or not session_data.get("questions"):
            return None, None
        
        questions = session_data["questions"]
        
        # Check if all questions are answered
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
            # Session is now complete, return None to indicate a new session should be created
            return None, None
        
        # Transform questions to match generate_session format
        transformed_questions = SessionResumeService._transform_session_questions_to_generate_format(questions)
        
        # Calculate level from XP for display (backward compatibility during transition)
        from ..models import db
        from ..services.xp_service import XPService
        user = db.session.get(User, user_id)
        total_xp = int(getattr(user, "experience", 0) or 0) if user else 0
        display_level = XPService.level_for_total_xp(total_xp)
        
        return incomplete_session, {
            "session_id": incomplete_session.id,
            "mode": incomplete_session.mode,
            "level": display_level,
            "concept_id": incomplete_session.concept_id,
            "questions": transformed_questions,
        }

