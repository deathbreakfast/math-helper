"""Factory for creating and persisting practice sessions."""

from __future__ import annotations

import json
from typing import Any

from ..database import transaction
from ..models import db
from ..services.practice_service import PracticeService


class SessionFactory:
    """Factory for persist + attach question IDs."""

    @staticmethod
    def create_session_with_questions(
        user_id: int,
        mode: str,
        concept_id: str,
        questions: list[dict[str, Any]],
        level: int | None = None,
    ) -> Any:
        """Create a new session and persist question IDs.
        
        Args:
            user_id: The user ID
            mode: Session mode (standard/multiplication/division)
            concept_id: Concept identifier
            questions: List of question dictionaries (must have question_id field)
            level: Optional level override
        
        Returns:
            The created PracticeSession object
        """
        # Create session
        session = PracticeService.create_session(
            user_id=user_id,
            mode=mode,
            level=level,
            concept_id=concept_id,
        )
        
        # Store question IDs
        question_ids = [q.get("question_id") for q in questions if q.get("question_id")]
        if question_ids:
            with transaction():
                session.question_ids = json.dumps(question_ids)
                db.session.add(session)
        
        return session

