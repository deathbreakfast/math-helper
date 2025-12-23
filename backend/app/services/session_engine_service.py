"""Session engine service for generating practice and test sessions."""

from __future__ import annotations

from typing import Any

from ..database import log_query
from ..models import User, db
from ..services.concept_selection_service import ConceptSelectionService
from ..services.question_generation_service import QuestionGenerationService
from ..services.session_factory import SessionFactory
from ..services.session_resume_service import SessionResumeService
from ..utils.legacy_mappings import concept_id_from_legacy_level, extract_legacy_level_from_concept_id


class SessionEngineService:
    """Service for session generation orchestration."""

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
        
        # Determine legacy "level" field for PracticeSession.
        # - For concept-based practice, level is optional and should not be derived from the user's current level.
        # - For non-concept practice, default to the user's current level.
        session_level = level if level is not None else (user.level if concept_id is None else None)
        
        # Try to resume an existing incomplete session
        incomplete_session, session_data = SessionResumeService.find_resumable_session(
            user_id=user_id,
            mode=mode,
            concept_id=concept_id,
            session_level=session_level,
            resume_oldest=resume_oldest,
        )
        
        if session_data:
            return session_data
        
        # No resumable session found, create a new one
        # Select concept (either provided or random from unlocked)
        selected_concept_id, extracted_level = ConceptSelectionService.select_concept_for_practice(
            user_id=user_id,
            concept_id=concept_id,
        )
        
        # Update session_level if we selected a concept with a legacy level
        if extracted_level is not None:
            session_level = extracted_level
        
        # Generate questions for the selected concept
        questions = QuestionGenerationService.generate_questions_for_concept(
            concept_id=selected_concept_id,
            question_count=10,
        )
        
        # Create session and persist question IDs
        session = SessionFactory.create_session_with_questions(
            user_id=user_id,
            mode=mode,
            concept_id=selected_concept_id,
            questions=questions,
            level=session_level,
        )
        
        # Determine response level (for backward compatibility)
        concept_level = extract_legacy_level_from_concept_id(selected_concept_id)
        response_level = session_level if session_level is not None else (concept_level if concept_level is not None else user.level)
        
        return {
            "session_id": session.id,
            "mode": mode,
            "level": response_level,
            "concept_id": selected_concept_id,
            "questions": questions,
        }
