"""Practice session-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from ..database import transaction
from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService
from ..services.practice_service import PracticeService
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
    """List practice sessions for a user (optionally filtered by concept_id/level/completion)."""
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    concept_id = request.args.get("concept_id", type=str)
    level = request.args.get("level", type=int)
    completed = request.args.get("completed")

    if not user_id:
        return create_error_response("user_id is required", 400)

    # Fallback to direct model import (kept local to avoid circular imports at module import time)
    from ..models import PracticeSession

    query = PracticeSession.query.filter_by(user_id=user_id)
    if concept_id:
        query = query.filter_by(concept_id=concept_id)
    if level is not None:
        query = query.filter_by(level=level)

    if completed is not None:
        completed_bool = str(completed).lower() in ("1", "true", "yes")
        query = query.filter(PracticeSession.completed_at.isnot(None) if completed_bool else PracticeSession.completed_at.is_(None))

    sessions = query.order_by(PracticeSession.completed_at.desc().nullslast(), PracticeSession.started_at.desc()).limit(200).all()

    return create_success_response({
        "sessions": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "mode": s.mode,
                "level": s.level,
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
    
    return create_success_response({
        "session": {
            "id": incomplete_session.id,
            "user_id": incomplete_session.user_id,
            "mode": incomplete_session.mode,
            "level": incomplete_session.level,
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
    level = payload.get("level")
    concept_id = payload.get("concept_id")
    resume_oldest = payload.get("resume_oldest", False)

    if not user_id:
        return create_error_response("user_id is required", 400)

    try:
        session_data = SessionEngineService.generate_session(
            user_id=user_id,
            mode=mode,
            level=level,
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
    payload = request.get_json(silent=True) or {}
    total_duration_ms = payload.get("total_duration_ms") or payload.get("totalDurationMs")

    from ..models import PracticeSession, Response, db

    # Get session
    session = db.session.get(PracticeSession, session_id)
    if not session:
        return create_error_response("Session not found", 404)

    # Get all responses for this session
    responses = list(db.session.scalars(
        select(Response).where(Response.session_id == session_id)
    ))

    # Calculate statistics based on unique questions (not all responses)
    # Group responses by question_id and get the latest response per question
    # This handles cases where a user may have answered the same question multiple times
    from collections import defaultdict
    latest_responses_by_question: dict[int, Response] = {}
    for response in responses:
        question_id = response.question_id
        if question_id not in latest_responses_by_question:
            latest_responses_by_question[question_id] = response
        else:
            # Keep the response with the latest answered_at timestamp
            if response.answered_at > latest_responses_by_question[question_id].answered_at:
                latest_responses_by_question[question_id] = response
    
    # Count unique questions and correct answers
    total_questions = len(latest_responses_by_question)
    correct_count = sum(1 for r in latest_responses_by_question.values() if r.is_correct)
    
    # Calculate duration from latest responses (one per question)
    calculated_duration = sum(r.duration_ms or 0 for r in latest_responses_by_question.values() if r.duration_ms)

    # Complete the session
    PracticeService.complete_session(
        session_id=session_id,
        total_questions=total_questions,
        correct_count=correct_count,
        total_duration_ms=total_duration_ms or (calculated_duration if calculated_duration > 0 else None),
    )

    # Get user
    user = UserService.get_user(session.user_id)
    if not user:
        return create_error_response("User not found", 404)

    # Aggregate daily stats
    AnalyticsService.aggregate_daily_stats(user.id)

    # Update achievements
    metrics = AnalyticsService.compute_user_metrics(user.id)
    
    # Award new achievements with session context
    try:
        AchievementService.ensure_achievements(user, metrics, session_id=session_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return create_error_response(f"Failed to award achievements: {str(e)}", 500)
    
    # Check for generic accuracy achievements (new metal/prestige tier system)
    generic_accuracy_achievements = AchievementService.check_generic_accuracy_achievements(session)
    
    # Check for lightning-fast achievements (level-specific speed)
    lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(user, session.id)
    
    # Check for accuracy-ace achievements (session-based accuracy)
    accuracy_ace_achievements = AchievementService.check_accuracy_ace_achievements(session)
    
    # Check for level-master achievements (per-level consecutive correct)
    level_master_achievements = AchievementService.check_level_master_achievements(user)
    
    # Ensure all achievements are committed before querying
    from ..models import db
    db.session.commit()
    db.session.flush()
    
    # Simple query: get all achievements for this session using indexed field
    new_achievements = AchievementService.get_achievements_by_session(session_id)
    
    # Check for So, Wow! achievements (awarded when first achievement of a tier is earned)
    # This must be called after all other achievements are awarded
    so_wow_achievements = AchievementService.check_so_wow_achievements(user, new_achievements, session_id=session_id)
    
    # Update new_achievements list to include So, Wow! achievements
    if so_wow_achievements:
        new_achievements.extend(so_wow_achievements)
        db.session.commit()
        db.session.flush()

    # Award XP + update level (XP-based leveling)
    from ..services.xp_service import XPService
    from ..services.concept_xp_service import ConceptXPService
    from ..services.achievement_xp_service import AchievementXPService

    xp_per_correct = ConceptXPService.xp_per_correct(session.concept_id)
    base_xp = int(correct_count) * int(xp_per_correct)

    # Only achievements earned during this session contribute to multiplier/bonus XP.
    achievement_rewards = [AchievementXPService.reward_for_achievement_code(a.code) for a in new_achievements]
    # Convert multiplier factors to deltas (e.g., 1.03 -> 0.03, 1.32 -> 0.32)
    # Multipliers are stored as factors but should be treated as bonus deltas
    multiplier_factors = [r.multiplier for r in achievement_rewards if r.multiplier and r.multiplier > 0]
    multiplier_deltas = [factor - 1.0 for factor in multiplier_factors]
    bonus_xp = sum(r.bonus_xp for r in achievement_rewards)

    # Calculate total multiplier as 1.0 + sum of deltas (e.g., 1.0 + 0.03 + 0.32 = 1.35)
    total_multiplier = 1.0 + sum(multiplier_deltas) if multiplier_deltas else 1.0
    multiplied_xp = float(base_xp) * float(total_multiplier)
    total_awarded_xp_raw = multiplied_xp + float(bonus_xp)
    earned_xp = int(round(total_awarded_xp_raw))
    prev_total_xp = int(getattr(user, "experience", 0) or 0)
    prev_level = int(user.level or 1)

    new_total_xp = prev_total_xp + earned_xp
    new_level = XPService.level_for_total_xp(new_total_xp)

    with transaction():
        user.experience = new_total_xp
        user.level = new_level
        db.session.add(user)

    level_up_result = {
        "earned_xp": earned_xp,
        "xp_breakdown": {
            "concept_id": session.concept_id,
            "xp_per_correct": xp_per_correct,
            "correct_count": int(correct_count),
            "base_xp": base_xp,
            "multipliers": [
                {"achievement_code": a.code, "multiplier": r.multiplier - 1.0}  # Return delta, not factor
                for a, r in zip(new_achievements, achievement_rewards)
                if r.multiplier and r.multiplier > 0
            ],
            "total_multiplier": total_multiplier,
            "multiplied_xp": multiplied_xp,
            "bonus_xp": bonus_xp,
            "bonus_xp_sources": [
                {"achievement_code": a.code, "bonus_xp": r.bonus_xp}
                for a, r in zip(new_achievements, achievement_rewards)
                if r.bonus_xp
            ],
            "total_awarded_xp_raw": total_awarded_xp_raw,
        },
        "previous_total_xp": prev_total_xp,
        "total_xp": new_total_xp,
        "previous_level": prev_level,
        "new_level": new_level,
        "leveled_up": new_level > prev_level,
        "xp_progress": XPService.progress_for_total_xp(new_total_xp),
    }

    # User state may have changed (new achievements and/or level). Invalidate cached user
    # so immediate subsequent GET /api/users/<id> returns fresh data.
    invalidate_user_cache(session.user_id)

    return create_success_response({
        "session": {
            "id": session.id,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": session.accuracy,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "mode": session.mode,
            "level": session.level,
            "concept_id": session.concept_id,
        },
        "achievements": [AchievementService.serialize_achievement(a) for a in new_achievements],
        "level_up": level_up_result,
    })



