"""Practice service for session management, question generation/storage, and attempt recording."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select

from ..database import log_query, transaction
from ..models import FlaggedQuestion, LevelProblemConfig, PracticeSession, Question, Response, db


class PracticeService:
    """Service for practice-related operations."""

    @staticmethod
    @log_query
    def create_session(
        user_id: int,
        mode: str = "standard",
        level: int | None = None,
        concept_id: str | None = None,
        is_test: bool = False,
        test_type: str | None = None,
    ) -> PracticeSession:
        """Create a new practice session."""
        with transaction():
            session = PracticeSession(
                user_id=user_id,
                mode=mode,
                level=level,
                concept_id=concept_id,
                is_test=is_test,
                test_type=test_type,
                started_at=datetime.utcnow(),
            )
            db.session.add(session)
            db.session.flush()  # Get the ID

        return session

    @staticmethod
    @log_query
    def complete_session(
        session_id: int,
        total_questions: int,
        correct_count: int,
        total_duration_ms: int | None = None,
    ) -> PracticeSession:
        """Mark a practice session as completed with statistics."""
        session = db.session.get(PracticeSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0.0

        with transaction():
            session.completed_at = datetime.utcnow()
            session.total_questions = total_questions
            session.correct_count = correct_count
            session.accuracy = accuracy
            session.total_duration_ms = total_duration_ms
            db.session.add(session)

        return session

    @staticmethod
    @log_query
    def create_question(
        operation: str,
        operand1: int,
        operand2: int,
        correct_answer: str,
        prompt: str,
        required_level: int = 1,
        difficulty: str | None = None,
        level_tag: str | None = None,
        target_ms: int | None = None,
        hint: str | None = None,
        answer_format: str | None = None,
        accepted_answers: list[str] | None = None,
        layout_type: str | None = None,
        layout_config: dict[str, Any] | None = None,
        math_type_label: str | None = None,
    ) -> Question:
        """Create and store a question."""
        accepted_answers_json = json.dumps(accepted_answers) if accepted_answers else None
        layout_config_json = json.dumps(layout_config) if layout_config else None

        with transaction():
            question = Question(
                operation=operation,
                operand1=operand1,
                operand2=operand2,
                correct_answer=correct_answer,
                prompt=prompt,
                required_level=required_level,
                difficulty=difficulty,
                level_tag=level_tag,
                target_ms=target_ms,
                hint=hint,
                answer_format=answer_format,
                accepted_answers=accepted_answers_json,
                layout_type=layout_type,
                layout_config=layout_config_json,
                math_type_label=math_type_label,
            )
            db.session.add(question)
            db.session.flush()

        return question

    @staticmethod
    @log_query
    def get_question(question_id: int) -> Question | None:
        """Get a question by ID."""
        return db.session.get(Question, question_id)

    @staticmethod
    @log_query
    def get_questions_for_level(
        level: int, operation: str | None = None, limit: int | None = None
    ) -> list[Question]:
        """Get questions available for a given level."""
        query = Question.query.filter(Question.required_level <= level)

        if operation:
            query = query.filter_by(operation=operation)

        query = query.order_by(Question.created_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    @log_query
    def record_response(
        session_id: int | None,
        question_id: int,
        user_id: int,
        submitted_answer: str,
        correct_answer: str,
        is_correct: bool,
        duration_ms: int | None = None,
        is_flagged: bool = False,
    ) -> Response:
        """Record a user's response to a question."""
        with transaction():
            response = Response(
                session_id=session_id,
                question_id=question_id,
                user_id=user_id,
                submitted_answer=submitted_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                duration_ms=duration_ms,
                is_flagged=is_flagged,
                answered_at=datetime.utcnow(),
            )
            db.session.add(response)
            db.session.flush()

        return response

    @staticmethod
    @log_query
    def flag_question(
        user_id: int, question_id: int, session_id: int | None = None, notes: str | None = None
    ) -> FlaggedQuestion:
        """Flag a question for review."""
        # Check if already flagged
        existing = db.session.scalar(
            select(FlaggedQuestion).where(
                FlaggedQuestion.user_id == user_id,
                FlaggedQuestion.question_id == question_id,
                FlaggedQuestion.session_id == session_id
            )
        )

        if existing:
            return existing

        with transaction():
            flagged = FlaggedQuestion(
                user_id=user_id,
                question_id=question_id,
                session_id=session_id,
                notes=notes,
                flagged_at=datetime.utcnow(),
            )
            db.session.add(flagged)
            db.session.flush()

        return flagged

    @staticmethod
    @log_query
    def unflag_question(user_id: int, question_id: int, session_id: int | None = None) -> bool:
        """Remove a flag from a question."""
        flagged = db.session.scalar(
            select(FlaggedQuestion).where(
                FlaggedQuestion.user_id == user_id,
                FlaggedQuestion.question_id == question_id,
                FlaggedQuestion.session_id == session_id
            )
        )

        if not flagged:
            return False

        with transaction():
            db.session.delete(flagged)

        return True

    @staticmethod
    @log_query
    def get_flagged_questions(user_id: int, session_id: int | None = None) -> list[FlaggedQuestion]:
        """Get all flagged questions for a user."""
        query = FlaggedQuestion.query.filter_by(user_id=user_id)

        if session_id:
            query = query.filter_by(session_id=session_id)

        return query.order_by(FlaggedQuestion.flagged_at.desc()).all()

    @staticmethod
    @log_query
    def get_level_problem_config(level: int, operation: str | None = None) -> list[LevelProblemConfig]:
        """Get problem configuration for a level."""
        query = LevelProblemConfig.query.filter_by(level=level, is_available=True)

        if operation:
            query = query.filter_by(operation=operation)

        return query.all()

    @staticmethod
    @log_query
    def create_level_problem_config(
        level: int,
        operation: str,
        min_operand1: int | None = None,
        max_operand1: int | None = None,
        min_operand2: int | None = None,
        max_operand2: int | None = None,
        layout_types: list[str] | None = None,
        answer_formats: list[str] | None = None,
        is_available: bool = True,
    ) -> LevelProblemConfig:
        """Create or update level problem configuration."""
        layout_types_json = json.dumps(layout_types) if layout_types else None
        answer_formats_json = json.dumps(answer_formats) if answer_formats else None

        # Check if config already exists
        existing = LevelProblemConfig.query.filter_by(level=level, operation=operation).first()

        with transaction():
            if existing:
                existing.min_operand1 = min_operand1
                existing.max_operand1 = max_operand1
                existing.min_operand2 = min_operand2
                existing.max_operand2 = max_operand2
                existing.layout_types = layout_types_json
                existing.answer_formats = answer_formats_json
                existing.is_available = is_available
                config = existing
            else:
                config = LevelProblemConfig(
                    level=level,
                    operation=operation,
                    min_operand1=min_operand1,
                    max_operand1=max_operand1,
                    min_operand2=min_operand2,
                    max_operand2=max_operand2,
                    layout_types=layout_types_json,
                    answer_formats=answer_formats_json,
                    is_available=is_available,
                )
                db.session.add(config)

            db.session.flush()

        return config

    @staticmethod
    @log_query
    def get_incomplete_session(
        user_id: int, 
        mode: str | None = None, 
        concept_id: str | None = None
    ) -> tuple[PracticeSession | None, int, int]:
        """Get the most recent incomplete session for a user.
        
        Args:
            user_id: User ID
            mode: Optional mode filter (standard/multiplication/division)
            concept_id: Optional concept_id filter (e.g., "c_level_1", "c_add_1s")
        
        Returns:
            Tuple of (session, total_responses_count, None)
            Only returns session if it has unanswered questions (responses exist but session not completed).
        """
        query = PracticeSession.query.filter_by(
            user_id=user_id,
            completed_at=None  # Incomplete sessions have null completed_at
        )
        
        if mode:
            query = query.filter_by(mode=mode)
        
        if concept_id:
            query = query.filter_by(concept_id=concept_id)
        
        session = query.order_by(PracticeSession.started_at.desc()).first()
        
        if not session:
            return None, 0, 0
        
        # Get response count for this session
        responses = list(db.session.scalars(
            select(Response).where(Response.session_id == session.id)
        ))
        response_count = len(responses)
        
        # Check if all questions are answered
        if session.question_ids:
            try:
                question_ids = json.loads(session.question_ids)
                total_questions = len(question_ids)
                # If we have responses for all questions, session is effectively complete
                if response_count >= total_questions:
                    # Mark as complete to prevent future resumption
                    with transaction():
                        session.completed_at = datetime.utcnow()
                        db.session.add(session)
                    return None, 0, 0
            except (json.JSONDecodeError, TypeError):
                # If question_ids is invalid JSON, fall through to return session
                pass
        
        return session, response_count, response_count
    
    @staticmethod
    @log_query
    def get_oldest_incomplete_session(user_id: int, mode: str | None = None) -> tuple[PracticeSession | None, int, int]:
        """Get the oldest incomplete session for a user (for dashboard resume).
        
        Args:
            user_id: User ID
            mode: Optional mode filter (standard/multiplication/division)
        
        Returns:
            Tuple of (session, total_responses_count, None)
            Only returns session if it has unanswered questions (responses exist but session not completed).
        """
        query = PracticeSession.query.filter_by(
            user_id=user_id,
            completed_at=None  # Incomplete sessions have null completed_at
        )
        
        if mode:
            query = query.filter_by(mode=mode)
        
        session = query.order_by(PracticeSession.started_at.asc()).first()  # Oldest first
        
        if not session:
            return None, 0, 0
        
        # Get response count for this session
        responses = list(db.session.scalars(
            select(Response).where(Response.session_id == session.id)
        ))
        response_count = len(responses)
        
        # Check if all questions are answered
        if session.question_ids:
            try:
                question_ids = json.loads(session.question_ids)
                total_questions = len(question_ids)
                # If we have responses for all questions, session is effectively complete
                if response_count >= total_questions:
                    # Mark as complete to prevent future resumption
                    with transaction():
                        session.completed_at = datetime.utcnow()
                        db.session.add(session)
                    return None, 0, 0
            except (json.JSONDecodeError, TypeError):
                # If question_ids is invalid JSON, fall through to return session
                pass
        
        return session, response_count, response_count
    
    @staticmethod
    @log_query
    def get_session_with_details(session_id: int) -> dict[str, Any] | None:
        """Get a session with its questions and responses.
        
        Uses stored question_ids from session to fetch all questions.
        Orders questions: answered first (by answered_at time), then unanswered.
        Falls back to inferring from responses if question_ids is NULL (backward compatibility).
        """
        session = db.session.get(PracticeSession, session_id)
        if not session:
            return None
        
        # Get all responses for this session
        responses = Response.query.filter_by(session_id=session_id).all()
        response_map = {r.question_id: r for r in responses if r.question_id}
        
        # Get question IDs - use stored question_ids if available, otherwise infer from responses
        question_id_list = []
        if session.question_ids:
            try:
                question_id_list = json.loads(session.question_ids)
            except (json.JSONDecodeError, TypeError):
                # Invalid JSON, fall back to inferring from responses
                question_id_list = list(response_map.keys())
        else:
            # Backward compatibility: infer from responses
            question_id_list = list(response_map.keys())
        
        # Get all questions for this session
        questions = []
        if question_id_list:
            questions = Question.query.filter(Question.id.in_(question_id_list)).all()
            # Create a map for quick lookup
            question_map = {q.id: q for q in questions}
            # Reorder to match question_id_list order
            questions = [question_map[qid] for qid in question_id_list if qid in question_map]
        
        # Separate answered and unanswered questions
        answered_questions = []
        unanswered_questions = []
        
        for question in questions:
            response = response_map.get(question.id)
            if response:
                answered_questions.append((question, response))
            else:
                unanswered_questions.append((question, None))
        
        # Sort answered questions by answered_at time (most recent first)
        answered_questions.sort(key=lambda x: x[1].answered_at if x[1] and x[1].answered_at else datetime.min, reverse=True)
        
        # Combine: answered first, then unanswered
        ordered_questions = [q for q, _ in answered_questions] + [q for q, _ in unanswered_questions]
        
        # Serialize questions with their responses
        questions_data = []
        for question in ordered_questions:
            response = response_map.get(question.id)
            question_data = {
                "id": f"q-{question.id}",
                "question_id": question.id,
                "prompt": question.prompt,
                "correctAnswer": question.correct_answer,
                "operation": question.operation,
                "operand1": question.operand1,
                "operand2": question.operand2,
                "layout": {
                    "type": question.layout_type,
                    "config": json.loads(question.layout_config) if question.layout_config else None,
                } if question.layout_type else None,
                "hint": question.hint,
                "answer_format": question.answer_format,
                "math_type_label": question.math_type_label,
            }
            
            if response:
                question_data["response"] = {
                    "submitted_answer": response.submitted_answer,
                    "is_correct": response.is_correct,
                    "duration_ms": response.duration_ms,
                    "answered_at": response.answered_at.isoformat() if response.answered_at else None,
                }
            
            questions_data.append(question_data)
        
        return {
            "session": {
                "id": session.id,
                "user_id": session.user_id,
                "mode": session.mode,
                "level": session.level,
                "is_test": session.is_test,
                "test_type": session.test_type,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            },
            "questions": questions_data,
        }
    
    @staticmethod
    def validate_answer(question: Question, submitted_answer: str) -> bool:
        """Validate a submitted answer against the question's correct answer and accepted answers.
        
        Args:
            question: The Question object
            submitted_answer: The answer submitted by the user
        
        Returns:
            True if the answer is correct, False otherwise
        """
        submitted = str(submitted_answer).strip()
        correct = str(question.correct_answer).strip()
        
        # Direct match
        if submitted == correct:
            return True
        
        # Handle different answer formats
        answer_format = question.answer_format or "integer"
        
        if answer_format == "remainder":
            # Format: "quotient R remainder" or just "quotient"
            # Normalize both answers for comparison
            submitted_normalized = submitted.replace(" ", "").upper()
            correct_normalized = correct.replace(" ", "").upper()
            if submitted_normalized == correct_normalized:
                return True
        
        elif answer_format == "fraction":
            # Format: "numerator/denominator"
            # Parse and compare fractions
            try:
                from fractions import Fraction
                submitted_frac = Fraction(submitted)
                correct_frac = Fraction(correct)
                if submitted_frac == correct_frac:
                    return True
            except (ValueError, ZeroDivisionError):
                pass
        
        elif answer_format == "decimal":
            # Format: decimal number
            # Compare with tolerance for floating point
            try:
                submitted_float = float(submitted)
                correct_float = float(correct)
                # Allow small tolerance (0.01)
                if abs(submitted_float - correct_float) < 0.01:
                    return True
            except ValueError:
                pass
        
        # Check accepted_answers if available
        if question.accepted_answers:
            try:
                accepted = json.loads(question.accepted_answers)
                if isinstance(accepted, list):
                    for accepted_answer in accepted:
                        if str(accepted_answer).strip() == submitted:
                            return True
            except (json.JSONDecodeError, TypeError):
                pass
        
        return False

