"""Practice session-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from ..database import transaction
from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService
from ..services.practice_service import PracticeService
from ..services.session_completion_service import SessionCompletionService
from ..services.session_engine_service import SessionEngineService
from ..services.user_service import UserService
from .common import invalidate_user_cache
from .route_helpers import (
    create_error_response,
    create_success_response,
    get_json_payload,
    get_user_id_from_payload,
    validate_required_fields,
)

practice_bp = Blueprint("practice", __name__)


@practice_bp.get("/practice/sessions")
def list_practice_sessions():
    """List practice sessions for a user (optionally filtered by concept_id/completion)."""
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    concept_id = request.args.get("concept_id", type=str)
    completed = request.args.get("completed")

    if not user_id:
        return create_error_response("user_id is required", 400)

    # Fallback to direct model import (kept local to avoid circular imports at module import time)
    from ..models import PracticeSession, User
    from ..services.xp_service import XPService

    query = PracticeSession.query.filter_by(user_id=user_id)
    if concept_id:
        query = query.filter_by(concept_id=concept_id)

    if completed is not None:
        completed_bool = str(completed).lower() in ("1", "true", "yes")
        query = query.filter(PracticeSession.completed_at.isnot(None) if completed_bool else PracticeSession.completed_at.is_(None))

    sessions = query.order_by(PracticeSession.completed_at.desc().nullslast(), PracticeSession.started_at.desc()).limit(200).all()
    
    # Calculate level from XP for display (if user exists)
    user = User.query.get(user_id)
    total_xp = int(getattr(user, "experience", 0) or 0) if user else 0
    display_level = XPService.level_for_total_xp(total_xp)

    return create_success_response({
        "sessions": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "mode": s.mode,
                "level": display_level,  # Calculated from XP for display
                "concept_id": s.concept_id,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "total_questions": s.total_questions,
                "correct_count": s.correct_count,
                "accuracy": s.accuracy,
                "total_duration_ms": s.total_duration_ms,
            }
            for s in sessions
        ]
    })


@practice_bp.get("/practice/sessions/incomplete")
def get_incomplete_session():
    """Get the most recent incomplete session for a user.
    
    Returns session details along with response count to help determine if session has unanswered questions.
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    mode = request.args.get("mode")

    if not user_id:
        return create_error_response("user_id is required", 400)

    incomplete_session, response_count, _ = PracticeService.get_incomplete_session(user_id, mode)
    
    if not incomplete_session:
        return create_success_response({"session": None, "response_count": 0})

    # Get session details with questions and responses
    session_data = PracticeService.get_session_with_details(incomplete_session.id)
    
    # Calculate level from XP for display
    from ..models import User
    from ..services.xp_service import XPService
    user = User.query.get(user_id)
    total_xp = int(getattr(user, "experience", 0) or 0) if user else 0
    display_level = XPService.level_for_total_xp(total_xp)
    
    return create_success_response({
        "session": {
            "id": incomplete_session.id,
            "user_id": incomplete_session.user_id,
            "mode": incomplete_session.mode,
            "level": display_level,  # Calculated from XP for display
            "concept_id": incomplete_session.concept_id,
            "started_at": incomplete_session.started_at.isoformat() if incomplete_session.started_at else None,
        },
        "response_count": response_count,
        "questions": session_data["questions"] if session_data else [],
    })


@practice_bp.get("/practice/sessions/<int:session_id>")
def get_session_details(session_id: int):
    """Get session details including questions and responses."""
    session_data = PracticeService.get_session_with_details(session_id)
    
    if not session_data:
        return create_error_response("Session not found", 404)
    
    return create_success_response(session_data)


@practice_bp.get("/practice/sessions/<int:session_id>/answers")
def get_session_answers(session_id: int):
    """Get all questions with their correct answers for a given session.
    
    This endpoint is useful for E2E tests to verify answers programmatically.
    Returns questions with their correct answers without requiring responses to be submitted.
    """
    session_data = PracticeService.get_session_with_details(session_id)
    
    if not session_data:
        return create_error_response("Session not found", 404)
    
    # Extract questions with their correct answers
    questions_with_answers = []
    for question in session_data.get("questions", []):
        questions_with_answers.append({
            "id": question.get("id"),
            "question_id": question.get("question_id"),
            "prompt": question.get("prompt"),
            "correct_answer": question.get("correctAnswer"),
            "operation": question.get("operation"),
            "operand1": question.get("operand1"),
            "operand2": question.get("operand2"),
            "layout": question.get("layout"),
            "answer_format": question.get("answer_format"),
        })
    
    return create_success_response({
        "session_id": session_id,
        "questions": questions_with_answers,
    })


@practice_bp.post("/practice/sessions/start")
def start_practice_session():
    """Start a new practice session with generated questions."""
    payload = get_json_payload()
    user_id = get_user_id_from_payload(payload)
    mode = payload.get("mode", "standard")
    concept_id = payload.get("concept_id")
    resume_oldest = payload.get("resume_oldest", False)

    if not user_id:
        return create_error_response("user_id is required", 400)

    try:
        session_data = SessionEngineService.generate_session(
            user_id=user_id,
            mode=mode,
            concept_id=concept_id,
            resume_oldest=resume_oldest,
        )
        return create_success_response(session_data, 201)
    except ValueError as e:
        return create_error_response(str(e), 400)
    except Exception as e:
        return create_error_response(f"Failed to create session: {str(e)}", 500)


@practice_bp.post("/practice/questions/check")
def check_answer():
    """Check if an answer is correct and store the response."""
    payload = get_json_payload()
    session_id = payload.get("session_id") or payload.get("sessionId")
    question_id = payload.get("question_id") or payload.get("questionId")
    submitted_answer = payload.get("submitted_answer") or payload.get("submittedAnswer")
    duration_ms = payload.get("duration_ms") or payload.get("durationMs")

    # Validate required fields
    is_valid, error_msg = validate_required_fields(
        payload,
        ["session_id", "question_id", "submitted_answer"],
        {
            "session_id": ["sessionId"],
            "question_id": ["questionId"],
            "submitted_answer": ["submittedAnswer"],
        }
    )
    if not is_valid:
        return create_error_response(error_msg or "Missing required fields", 400)

    # Get question
    question = PracticeService.get_question(question_id)
    if not question:
        return create_error_response("Question not found", 404)

    # Get session to get user_id
    from ..models import PracticeSession, db

    session = db.session.get(PracticeSession, session_id)
    if not session:
        return create_error_response("Session not found", 404)

    # Validate answer
    is_correct = PracticeService.validate_answer(question, submitted_answer)

    # Record response
    PracticeService.record_response(
        session_id=session_id,
        question_id=question_id,
        user_id=session.user_id,
        submitted_answer=str(submitted_answer),
        correct_answer=question.correct_answer,
        is_correct=is_correct,
        duration_ms=duration_ms,
    )

    return create_success_response({
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
    })


@practice_bp.post("/practice/sessions/<int:session_id>/complete")
def complete_session(session_id: int):
    """Complete a practice session, award achievements, and check leveling."""
    import logging
    
    logger = logging.getLogger(__name__)
    payload = request.get_json(silent=True) or {}
    total_duration_ms = payload.get("total_duration_ms") or payload.get("totalDurationMs")

    try:
        # Delegate to orchestration service
        result = SessionCompletionService.complete_session(session_id, total_duration_ms)
        
        # Invalidate user cache since state may have changed
        from ..models import PracticeSession, db
        session = db.session.get(PracticeSession, session_id)
        if session:
            invalidate_user_cache(session.user_id)
        
        return create_success_response(result)
    except ValueError as e:
        # Session/user not found
        return create_error_response(str(e), 404)
    except Exception as e:
        # Log the full exception with traceback
        logger.exception("Failed to complete session")
        return create_error_response("Failed to complete session", 500)



