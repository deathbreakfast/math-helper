"""API routes using service layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from flask import Blueprint, jsonify, request

from .services.achievement_service import AchievementService
from .services.analytics_service import AnalyticsService
from .services.level_config_service import LevelConfigService
from .services.practice_service import PracticeService
from .services.session_engine_service import SessionEngineService
from .services.user_service import UserService

api_bp = Blueprint("api", __name__)


@api_bp.get("/hello")
def hello_world():
    """Return a simple greeting to verify the end-to-end flow."""
    return jsonify(message="Hello from Math Helper API")


@api_bp.post("/users")
def create_user():
    """Persist a new learner with a plain-text 4-digit PIN."""
    payload = request.get_json(silent=True) or {}
    avatar = payload.get("avatar")
    display_name = (payload.get("name") or "").strip()
    pin = (payload.get("pin") or "").strip()

    user, errors = UserService.create_user(display_name, pin, avatar)

    if errors:
        return jsonify({"errors": errors}), 400

    return jsonify(_serialize_user(user)), 201


@api_bp.get("/users")
def list_users():
    """Return all learners with derived dashboard metrics."""
    users = UserService.list_users()
    return jsonify({"users": [_serialize_user(user) for user in users]})


@api_bp.get("/users/<int:user_id>")
def retrieve_user(user_id: int):
    """Return dashboard metrics for a single learner."""
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(_serialize_user(user))


@api_bp.get("/achievements")
def list_achievements():
    """Return persisted achievements, optionally filtered to a user."""
    user_id = request.args.get("user_id", type=int)

    # Ensure achievements are up to date for all users or specific user
    if user_id:
        user = UserService.get_user(user_id)
        if user:
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics)
    else:
        users = UserService.list_users()
        for user in users:
            metrics = AnalyticsService.compute_user_metrics(user.id)
            AchievementService.ensure_achievements(user, metrics)

    achievements = AchievementService.get_achievements_by_category(user_id=user_id, limit=50)
    return jsonify({"achievements": [AchievementService.serialize_achievement(a) for a in achievements]})


@api_bp.post("/practice/submissions")
def submit_practice_attempts():
    """Submit practice attempts while verifying the learner PIN."""
    payload = request.get_json(silent=True) or {}
    pin = (payload.get("pin") or "").strip()
    user_id = payload.get("userId") or payload.get("user_id")
    user_name = (payload.get("userName") or payload.get("user_name") or "").strip()

    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"error": "A 4-digit PIN is required to submit practice."}), 400

    # Find user
    user = None
    if user_id is not None:
        try:
            user = UserService.get_user(int(user_id))
        except (TypeError, ValueError):
            user = None

    if user is None and user_name:
        user = UserService.get_user_by_name(user_name)

    if user is None:
        return jsonify({"error": "Learner not found. Create the profile before practicing."}), 404

    if not UserService.verify_pin(user, pin):
        return jsonify({"error": "PIN verification failed for this learner."}), 403

    attempts_payload = payload.get("attempts") or []
    normalized_attempts: list[dict[str, Any]] = []
    correct_count = 0

    # Create practice session
    mode = payload.get("mode", "standard")
    session = PracticeService.create_session(user.id, mode=mode, level=user.level)

    # Process each attempt
    for attempt in attempts_payload:
        question_id = attempt.get("questionId") or attempt.get("question_id")
        prompt = attempt.get("prompt") or "Practice prompt"
        submitted = attempt.get("submittedAnswer")
        expected = attempt.get("correctAnswer")
        elapsed_ms = attempt.get("elapsedMs") or attempt.get("durationMs")

        is_correct = (
            submitted is not None
            and expected is not None
            and str(submitted).strip() != ""
            and str(submitted).strip() == str(expected).strip()
        )

        if is_correct:
            correct_count += 1

        # If we have a real question_id, record the response
        if question_id and isinstance(question_id, int):
            PracticeService.record_response(
                session_id=session.id,
                question_id=question_id,
                user_id=user.id,
                submitted_answer=str(submitted) if submitted else "",
                correct_answer=str(expected) if expected else "",
                is_correct=is_correct,
                duration_ms=elapsed_ms,
            )

        normalized_attempts.append(
            {
                "questionId": question_id,
                "prompt": prompt,
                "submittedAnswer": submitted,
                "correctAnswer": expected,
                "isCorrect": is_correct,
                "elapsedMs": elapsed_ms,
                "awardedPoints": 10 if is_correct else 0,
            }
        )

    total_attempts = len(normalized_attempts)
    accuracy = round((correct_count / total_attempts) * 100) if total_attempts else 0

    # Complete the session
    total_duration_ms = sum(
        (a.get("elapsedMs") or 0) for a in normalized_attempts if a.get("elapsedMs")
    )
    PracticeService.complete_session(
        session.id, total_attempts, correct_count, total_duration_ms if total_duration_ms > 0 else None
    )

    # Aggregate daily stats for analytics
    AnalyticsService.aggregate_daily_stats(user.id)

    # Update achievements
    metrics = AnalyticsService.compute_user_metrics(user.id)
    AchievementService.ensure_achievements(user, metrics)

    session_payload = {
        "id": str(session.id),
        "submittedAt": datetime.utcnow().isoformat(),
        "user": {
            "id": user.id,
            "name": user.display_name,
            "avatar": user.avatar,
            "level": user.level,
            "share_url_params": {"user": user.display_name, "pin": user.pin},
        },
        "attempts": normalized_attempts,
        "totals": {
            "questions": total_attempts,
            "correct": correct_count,
            "accuracy": accuracy,
        },
        "status": "completed",
        "message": payload.get("notes") or "Practice submissions captured for the session.",
    }

    return jsonify({"session": session_payload})


@api_bp.post("/practice/sessions/start")
def start_practice_session():
    """Start a new practice or test session with generated questions."""
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id") or payload.get("userId")
    mode = payload.get("mode", "standard")
    is_test = payload.get("is_test", False) or payload.get("isTest", False)
    test_type = payload.get("test_type") or payload.get("testType")
    level = payload.get("level")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    try:
        session_data = SessionEngineService.generate_session(
            user_id=user_id,
            mode=mode,
            is_test=is_test,
            test_type=test_type,
            level=level,
        )
        return jsonify(session_data), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create session: {str(e)}"}), 500


@api_bp.get("/practice/sessions/eligible-tests")
def get_eligible_tests():
    """Get list of eligible test types for a user."""
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    eligible_tests = SessionEngineService.get_eligible_tests(user)
    return jsonify({"eligible_tests": eligible_tests})


@api_bp.post("/practice/questions/check")
def check_answer():
    """Check if an answer is correct and store the response."""
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id") or payload.get("sessionId")
    question_id = payload.get("question_id") or payload.get("questionId")
    submitted_answer = payload.get("submitted_answer") or payload.get("submittedAnswer")
    duration_ms = payload.get("duration_ms") or payload.get("durationMs")

    if not session_id or not question_id or submitted_answer is None:
        return jsonify({"error": "session_id, question_id, and submitted_answer are required"}), 400

    # Get question
    question = PracticeService.get_question(question_id)
    if not question:
        return jsonify({"error": "Question not found"}), 404

    # Get session to get user_id
    from .models import PracticeSession

    session = PracticeSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

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

    return jsonify({
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
    })


@api_bp.post("/practice/sessions/<int:session_id>/complete")
def complete_session(session_id: int):
    """Complete a practice session, award achievements, and check leveling."""
    payload = request.get_json(silent=True) or {}
    total_duration_ms = payload.get("total_duration_ms") or payload.get("totalDurationMs")

    from .models import PracticeSession, Response

    # Get session
    session = PracticeSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Get all responses for this session
    responses = Response.query.filter_by(session_id=session_id).all()

    # Calculate statistics
    total_questions = len(responses)
    correct_count = sum(1 for r in responses if r.is_correct)
    calculated_duration = sum(r.duration_ms or 0 for r in responses if r.duration_ms)

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
        return jsonify({"error": "User not found"}), 404

    # Aggregate daily stats
    AnalyticsService.aggregate_daily_stats(user.id)

    # Update achievements
    metrics = AnalyticsService.compute_user_metrics(user.id)
    achievements = AchievementService.ensure_achievements(user, metrics)
    
    # Check for consecutive correct achievements (30 in a row)
    consecutive_achievements = AchievementService.check_consecutive_correct_achievements(
        user, session.test_type
    )
    
    # Combine all new achievements
    all_achievements = AchievementService.get_user_achievements(user.id)
    new_achievements = [
        a for a in all_achievements
        if a.earned_at >= session.started_at or a in consecutive_achievements
    ]

    # Check leveling
    next_level = user.level + 1
    can_level_up, missing_achievements = UserService.can_level_up(user, next_level)
    level_up_result = {
        "eligible": can_level_up,
        "missing_achievements": missing_achievements,
    }

    if can_level_up:
        success, errors = UserService.level_up(user, next_level)
        if success:
            level_up_result["new_level"] = next_level
            # Refresh user
            user = UserService.get_user(session.user_id)
        else:
            level_up_result["errors"] = errors

    return jsonify({
        "session": {
            "id": session.id,
            "is_test": session.is_test,
            "test_type": session.test_type,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": session.accuracy,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        },
        "achievements": [AchievementService.serialize_achievement(a) for a in new_achievements],
        "level_up": level_up_result,
    })


def _serialize_user(user) -> dict[str, Any]:
    """Serialize a user with metrics and achievements."""
    metrics = AnalyticsService.compute_user_metrics(user.id)
    achievements_list = AchievementService.ensure_achievements(user, metrics)
    share_url = {"user": user.display_name, "pin": user.pin}

    weekly_gain = AnalyticsService.get_weekly_gain(user.id)

    return {
        "id": user.id,
        "name": user.display_name,
        "avatar": user.avatar,
        "pin": user.pin,
        "level": user.level,
        "questionsAnswered": metrics["questions_answered"],
        "averageSpeed": metrics["average_speed_seconds"],
        "weeklyGain": weekly_gain,
        "stats": metrics["operation_stats"],
        "achievements": [AchievementService.serialize_achievement(a) for a in achievements_list],
        "share_url_params": share_url,
    }


@api_bp.get("/levels")
def list_levels():
    """Get all level configurations."""
    levels = LevelConfigService.get_all_level_configs()
    return jsonify({"levels": levels})


@api_bp.get("/levels/<int:level>")
def get_level(level: int):
    """Get configuration for a specific level."""
    config = LevelConfigService.get_level_config(level)
    if not config:
        return jsonify({"error": f"Level {level} not found"}), 404
    return jsonify({"level": level, "config": config})


@api_bp.get("/levels/<int:level>/requirements")
def get_level_requirements(level: int):
    """Get achievement requirements for a specific level."""
    requirements = LevelConfigService.get_level_progression_config(level)
    return jsonify({"level": level, "requirements": requirements})


@api_bp.get("/achievements/definitions")
def list_achievement_definitions():
    """Get all achievement definitions."""
    achievements = LevelConfigService.get_all_achievement_configs()
    return jsonify({"achievements": achievements})


@api_bp.get("/achievements/<code>/requirements")
def get_achievement_requirements(code: str):
    """Get requirements for a specific achievement."""
    config = LevelConfigService.get_achievement_config(code)
    if not config:
        return jsonify({"error": f"Achievement {code} not found"}), 404
    return jsonify({"achievement_code": code, "requirements": config.get("requirements", {})})
