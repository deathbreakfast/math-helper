"""Session engine service for generating practice sessions."""

from __future__ import annotations

from typing import Any

from ..database import log_query
from ..models import User, db
from ..services.concept_selection_service import ConceptSelectionService
from ..services.question_count_service import QuestionCountService
from ..services.question_generation_service import QuestionGenerationService
from ..services.session_factory import SessionFactory
from ..services.session_resume_service import SessionResumeService
from ..services.xp_service import XPService


class SessionEngineService:
    """Service for session generation orchestration."""

    @staticmethod
    @log_query
    def generate_session(
        user_id: int,
        mode: str = "standard",
        concept_id: str | None = None,
        resume_oldest: bool = False,
    ) -> dict[str, Any]:
        """Generate a practice session with questions.
        
        Checks for incomplete session first. If found, returns existing session.
        Otherwise creates a new session.
        
        Args:
            user_id: The user ID
            mode: Session mode (standard/multiplication/division)
            concept_id: Optional concept identifier (e.g., "c_concept_001", "c_add_1s")
            resume_oldest: If True, resume the oldest incomplete session (for dashboard)
        
        Returns:
            Dictionary with session_id, mode, level (calculated from XP), concept_id, and questions list
        """
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Try to resume an existing incomplete session
        incomplete_session, session_data = SessionResumeService.find_resumable_session(
            user_id=user_id,
            mode=mode,
            concept_id=concept_id,
            resume_oldest=resume_oldest,
        )
        
        if session_data:
            return session_data
        
        # No resumable session found, create a new one
        # Select concept (either provided or random from unlocked)
        selected_concept_id = ConceptSelectionService.select_concept_for_practice(
            user_id=user_id,
            concept_id=concept_id,
        )

        # Calculate dynamic question count based on perfect session history
        question_count = QuestionCountService.get_question_count_for_concept(
            user_id=user_id,
            concept_id=selected_concept_id,
        )

        # Generate questions for the selected concept
        questions = QuestionGenerationService.generate_questions_for_concept(
            concept_id=selected_concept_id,
            question_count=question_count,
        )
        
        # Create session and persist question IDs (level=None, not setting session.level)
        session = SessionFactory.create_session_with_questions(
            user_id=user_id,
            mode=mode,
            concept_id=selected_concept_id,
            questions=questions,
            level=None,
        )
        
        # Calculate level from XP for display
        total_xp = int(getattr(user, "experience", 0) or 0)
        display_level = XPService.level_for_total_xp(total_xp)
        
        return {
            "session_id": session.id,
            "mode": mode,
            "level": display_level,
            "concept_id": selected_concept_id,
            "questions": questions,
        }
