"""API routes using service layer."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from flask import Blueprint, jsonify, request

from .config.test_requirements import get_all_test_requirements, get_test_requirements
from .services.achievement_service import AchievementService
from .services.analytics_service import AnalyticsService
from .services.level_config_service import LevelConfigService
from .services.practice_service import PracticeService
from .services.session_engine_service import SessionEngineService
from .services.test_eligibility_service import TestEligibilityService
from .services.test_service import TestService
from .services.user_service import UserService

api_bp = Blueprint("api", __name__)

# Simple in-memory cache for user data (1-2 second TTL to handle rapid duplicate requests)
_user_cache: dict[int, tuple[dict[str, Any], float]] = {}
_CACHE_TTL = 2.0  # 2 seconds TTL


def _get_cached_user(user_id: int) -> dict[str, Any] | None:
    """Get cached user data if still valid."""
    if user_id in _user_cache:
        data, timestamp = _user_cache[user_id]
        if time.time() - timestamp < _CACHE_TTL:
            return data
        else:
            # Expired, remove from cache
            del _user_cache[user_id]
    return None


def _cache_user(user_id: int, data: dict[str, Any]) -> None:
    """Cache user data with current timestamp."""
    _user_cache[user_id] = (data, time.time())
    # Clean up old entries (keep cache size reasonable)
    if len(_user_cache) > 100:
        current_time = time.time()
        expired_keys = [
            uid for uid, (_, ts) in _user_cache.items()
            if current_time - ts >= _CACHE_TTL
        ]
        for key in expired_keys:
            del _user_cache[key]


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
    """Return all learners with derived dashboard metrics (optimized with batch queries).
    
    Query parameters:
    - minimal: if true, returns only id, name, avatar, level (for fast initial load)
    """
    minimal = request.args.get('minimal', 'false').lower() == 'true'
    
    users = UserService.list_users()
    
    if not users:
        return jsonify({"users": []})
    
    # If minimal mode, return lightweight data for fast initial load
    if minimal:
        return jsonify({
            "users": [
                {
                    "id": user.id,
                    "name": user.display_name,
                    "avatar": user.avatar,
                    "level": user.level,
                }
                for user in users
            ]
        })
    
    # Full data mode - use batch operations
    # Extract user IDs for batch operations
    user_ids = [user.id for user in users]
    
    # Batch compute metrics for all users at once
    all_metrics = AnalyticsService.compute_user_metrics_batch(user_ids)
    
    # Batch ensure achievements for all users
    all_achievements = AchievementService.ensure_achievements_batch(users, all_metrics)
    
    # Batch compute weekly gains
    all_weekly_gains = AnalyticsService.get_weekly_gain_batch(user_ids)
    
    # Serialize with pre-computed data
    return jsonify({
        "users": [
            _serialize_user_fast(
                user,
                all_metrics.get(user.id, {}),
                all_achievements.get(user.id, []),
                all_weekly_gains.get(user.id, 0)
            )
            for user in users
        ]
    })


@api_bp.get("/users/<int:user_id>")
def retrieve_user(user_id: int):
    """Return dashboard metrics for a single learner.
    
    Uses request-level caching (1-2 second TTL) to handle rapid duplicate requests
    during parallel test execution.
    """
    # Check cache first
    cached_data = _get_cached_user(user_id)
    if cached_data is not None:
        return jsonify(cached_data)
    
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    serialized = _serialize_user(user)
    
    # Cache the result
    _cache_user(user_id, serialized)
    
    return jsonify(serialized)


@api_bp.post("/users/<int:user_id>/verify-pin")
def verify_user_pin(user_id: int):
    """Verify a PIN for a user. Returns success/failure without exposing the PIN.
    
    This endpoint should be used for PIN verification instead of sending PINs
    to the frontend in user data.
    """
    payload = request.get_json(silent=True) or {}
    pin = (payload.get("pin") or "").strip()
    
    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"error": "PIN must be a 4-digit number", "verified": False}), 400
    
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found", "verified": False}), 404
    
    is_valid = UserService.verify_pin(user, pin)
    
    if is_valid:
        return jsonify({"verified": True})
    else:
        return jsonify({"error": "Incorrect PIN", "verified": False}), 403


@api_bp.get("/achievements")
def list_achievements():
    """Return persisted achievements, optionally filtered to a user.
    
    Query parameters:
    - user_id: Optional user ID to filter achievements
    - code: Optional achievement code to filter by
    - limit: Optional limit for number of achievements (default: 50, max: 100)
    """
    user_id = request.args.get("user_id", type=int)
    achievement_code = request.args.get("code", type=str)
    limit = request.args.get("limit", type=int, default=50)
    # Cap limit at 100 to prevent excessive queries
    limit = min(limit, 100) if limit else 50

    # If filtering by code and user_id, fetch achievements by code
    if achievement_code and user_id:
        achievements = AchievementService.get_achievements_by_code(
            user_id=user_id,
            achievement_code=achievement_code
        )
        return jsonify({"achievements": [AchievementService.serialize_achievement(a) for a in achievements]})

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

    # Use optimized SQL query with ORDER BY earned_at DESC LIMIT
    # The earned_at column is indexed for performance
    # Include user names when fetching all users' achievements (for dashboard)
    include_user_name = user_id is None
    achievements = AchievementService.get_achievements_by_category(
        user_id=user_id, 
        limit=limit, 
        include_user_name=include_user_name
    )
    
    # Serialize achievements with user names if available
    if include_user_name:
        # User name is available via join in the query
        serialized = []
        for achievement in achievements:
            user_name = achievement.user.display_name if achievement.user else None
            serialized.append(AchievementService.serialize_achievement(achievement, user_name=user_name))
        return jsonify({"achievements": serialized})
    else:
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


@api_bp.get("/practice/sessions/incomplete")
def get_incomplete_session():
    """Get the most recent incomplete session for a user.
    
    Returns session details along with response count to help determine if session has unanswered questions.
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    mode = request.args.get("mode")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    incomplete_session, response_count, _ = PracticeService.get_incomplete_session(user_id, mode)
    
    if not incomplete_session:
        return jsonify({"session": None, "response_count": 0}), 200

    # Get session details with questions and responses
    session_data = PracticeService.get_session_with_details(incomplete_session.id)
    
    return jsonify({
        "session": {
            "id": incomplete_session.id,
            "user_id": incomplete_session.user_id,
            "mode": incomplete_session.mode,
            "level": incomplete_session.level,
            "is_test": incomplete_session.is_test,
            "test_type": incomplete_session.test_type,
            "started_at": incomplete_session.started_at.isoformat() if incomplete_session.started_at else None,
        },
        "response_count": response_count,
        "questions": session_data["questions"] if session_data else [],
    }), 200


@api_bp.get("/practice/sessions/<int:session_id>")
def get_session_details(session_id: int):
    """Get session details including questions and responses."""
    session_data = PracticeService.get_session_with_details(session_id)
    
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(session_data), 200


@api_bp.get("/practice/sessions/<int:session_id>/answers")
def get_session_answers(session_id: int):
    """Get all questions with their correct answers for a given session.
    
    This endpoint is useful for E2E tests to verify answers programmatically.
    Returns questions with their correct answers without requiring responses to be submitted.
    """
    session_data = PracticeService.get_session_with_details(session_id)
    
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
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
    
    return jsonify({
        "session_id": session_id,
        "questions": questions_with_answers,
    }), 200


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


@api_bp.get("/practice/test-requirements")
def get_test_requirements_endpoint():
    """Get test requirements for all levels or a specific level."""
    level = request.args.get("level", type=int)
    
    if level:
        requirements = get_test_requirements(level)
        if not requirements:
            return jsonify({"error": f"No test requirements found for level {level}"}), 404
        return jsonify({"level": level, "requirements": requirements})
    else:
        all_requirements = get_all_test_requirements()
        return jsonify({"requirements": all_requirements})


@api_bp.get("/practice/test-eligibility")
def get_test_eligibility():
    """Check if user is eligible for any test or a specific level test."""
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    level = request.args.get("level", type=int)

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if level:
        # Check eligibility for specific level
        is_eligible, reason, details = TestEligibilityService.check_test_eligibility(user, level)
        return jsonify({
            "level": level,
            "is_eligible": is_eligible,
            "reason": reason,
            "details": details,
        })
    else:
        # Get all available tests
        available_tests = TestEligibilityService.get_available_tests(user)
        return jsonify({"available_tests": available_tests})


@api_bp.get("/tests/definitions")
def get_test_definitions():
    """Get all test definitions (legacy + new).
    
    Query parameters:
        user_id: Optional user ID to filter by user level or check unlock status
        include_unlock_status: Optional boolean to include unlock_status for each test (requires user_id)
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    include_unlock_status = request.args.get("include_unlock_status", "false").lower() == "true"
    user_level = None
    
    if user_id:
        user = UserService.get_user(user_id)
        if user:
            user_level = user.level
    
    definitions = TestService.get_all_test_definitions(
        user_level=user_level,
        user_id=user_id if include_unlock_status else None,
        include_unlock_status=include_unlock_status,
    )
    return jsonify({"definitions": definitions})


@api_bp.get("/tests/attempts")
def get_all_test_attempts():
    """Get all test attempts for a user across all test types.
    
    Query parameters:
        user_id: Required user ID
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    attempts = TestService.get_test_attempts(user_id, test_type=None)
    return jsonify({"attempts": attempts})


@api_bp.get("/tests/<test_type>/attempts")
def get_test_attempts(test_type: str):
    """Get test attempts for a specific test type.
    
    Query parameters:
        user_id: Required user ID
    """
    user_id = request.args.get("user_id", type=int) or request.args.get("userId", type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    attempts = TestService.get_test_attempts(user_id, test_type=test_type)
    return jsonify({"test_type": test_type, "attempts": attempts})


@api_bp.get("/tests/attempts/<int:attempt_id>/details")
def get_test_attempt_details(attempt_id: int):
    """Get detailed test attempt with all questions and responses."""
    attempt_detail = TestService.get_test_attempt_detail(attempt_id)
    
    if not attempt_detail:
        return jsonify({"error": "Test attempt not found"}), 404
    
    return jsonify(attempt_detail)


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

    # Record test attempt if this is a test session
    if session.is_test and session.test_type and session.level:
        from .models import TestAttempt, db
        from .config.test_requirements import get_test_requirements
        
        test_requirements = get_test_requirements(session.level)
        if test_requirements:
            passing_score = test_requirements["passing_score"]
            score = session.accuracy / 100.0  # Convert percentage to decimal
            passed = score >= passing_score
            
            # Calculate average time per question
            avg_time_per_question_ms = None
            if total_questions > 0 and calculated_duration > 0:
                avg_time_per_question_ms = calculated_duration // total_questions
            
            # Create test attempt record
            test_attempt = TestAttempt(
                user_id=user.id,
                level=session.level,
                test_type=session.test_type,
                score=score,
                avg_time_per_question_ms=avg_time_per_question_ms,
                total_duration_ms=total_duration_ms or calculated_duration,
                passed=passed,
            )
            db.session.add(test_attempt)
            db.session.commit()

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
        return jsonify({"error": f"Failed to award achievements: {str(e)}"}), 500
    
    # Check for consecutive correct achievements (30 in a row)
    consecutive_achievements = AchievementService.check_consecutive_correct_achievements(
        user, session.test_type
    )
    
    # Test achievements removed - no longer checking for test achievements
    
    # Check for generic accuracy achievements (new metal/prestige tier system)
    generic_accuracy_achievements = AchievementService.check_generic_accuracy_achievements(session)
    
    # Check for lightning-fast achievements (level-specific speed)
    lightning_fast_achievements = AchievementService.check_lightning_fast_achievements(user, session.id)
    
    # Check for level-master achievements (per-level consecutive correct)
    level_master_achievements = AchievementService.check_level_master_achievements(user)
    
    # Ensure all achievements are committed before querying
    from .models import db
    db.session.commit()
    db.session.flush()
    
    # Simple query: get all achievements for this session using indexed field
    new_achievements = AchievementService.get_achievements_by_session(session_id)

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
    """Serialize a user with metrics and achievements (single user version).
    
    NOTE: PIN is NOT included in the response for security reasons.
    PIN verification must be done via the /api/users/<id>/verify-pin endpoint.
    
    NOTE: This function should NOT award new achievements - it should only return existing ones.
    Achievement awarding should only happen during session completion.
    """
    metrics = AnalyticsService.compute_user_metrics(user.id)
    # Get existing achievements only - do NOT award new ones during user fetch
    # Achievement awarding should only happen during session completion with session_id
    achievements_list = AchievementService.get_user_achievements(user.id)

    weekly_gain = AnalyticsService.get_weekly_gain(user.id)

    return _serialize_user_fast(user, metrics, achievements_list, weekly_gain)


def _serialize_user_fast(
    user: Any,
    metrics: dict[str, Any],
    achievements_list: list[Any],
    weekly_gain: int
) -> dict[str, Any]:
    """Serialize a user with pre-computed metrics and achievements (optimized version).
    
    This version accepts pre-computed data to avoid redundant queries when
    serializing multiple users in batch.
    
    NOTE: PIN is NOT included in the response for security reasons.
    PIN verification must be done via the /api/users/<id>/verify-pin endpoint.
    """
    # Do not include PIN in response - security best practice
    share_url = {"user": user.display_name}

    return {
        "id": user.id,
        "name": user.display_name,
        "avatar": user.avatar,
        # PIN removed for security - use /api/users/<id>/verify-pin endpoint
        "level": user.level,
        "questionsAnswered": metrics.get("questions_answered", 0),
        "averageSpeed": metrics.get("average_speed_seconds", 0.0),
        "weeklyGain": weekly_gain,
        "stats": metrics.get("operation_stats", {}),
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


@api_bp.get("/levels/requirements")
def get_batch_level_requirements():
    """Get achievement requirements for multiple levels in one request.
    
    Query parameter: levels (comma-separated list of level numbers)
    Example: /api/levels/requirements?levels=1,2,3,4,5
    """
    levels_param = request.args.get('levels', '')
    if not levels_param:
        return jsonify({"error": "levels parameter is required (comma-separated list)"}), 400
    
    try:
        levels = [int(level.strip()) for level in levels_param.split(',') if level.strip()]
    except ValueError:
        return jsonify({"error": "Invalid levels parameter. Must be comma-separated integers"}), 400
    
    if not levels:
        return jsonify({"error": "No valid levels provided"}), 400
    
    # Fetch requirements for all requested levels
    requirements_by_level = {}
    for level in levels:
        requirements = LevelConfigService.get_level_progression_config(level)
        requirements_by_level[level] = requirements
    
    return jsonify({"requirements": requirements_by_level})


@api_bp.get("/achievements/definitions")
def list_achievement_definitions():
    """Get all achievement definitions from config with full display information."""
    achievements = LevelConfigService.get_all_achievement_configs()
    
    # Format for frontend consumption
    formatted_achievements = {}
    for code, config in achievements.items():
        formatted_achievements[code] = {
            "code": code,
            "title": config.get("title", ""),
            "description": config.get("description", ""),
            "icon": config.get("icon", "🏆"),
            "category": config.get("category", "milestone"),
            "requirements": config.get("requirements", {}),
        }
    
    return jsonify({"achievements": formatted_achievements})


@api_bp.get("/achievements/<code>/requirements")
def get_achievement_requirements(code: str):
    """Get requirements for a specific achievement."""
    config = LevelConfigService.get_achievement_config(code)
    if not config:
        return jsonify({"error": f"Achievement {code} not found"}), 404
    return jsonify({"achievement_code": code, "requirements": config.get("requirements", {})})


@api_bp.post("/users/<int:user_id>/level-up")
def manual_level_up(user_id: int):
    """Manually trigger level up for a user if requirements are met."""
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    next_level = user.level + 1
    can_level_up, missing_achievements = UserService.can_level_up(user, next_level)
    
    if not can_level_up:
        return jsonify({
            "success": False,
            "eligible": False,
            "missing_achievements": missing_achievements,
            "message": f"Cannot level up to level {next_level}. Missing achievements: {', '.join(missing_achievements)}"
        }), 400

    success, errors = UserService.level_up(user, next_level)
    
    if success:
        # Refresh user to get updated level
        user = UserService.get_user(user_id)
        return jsonify({
            "success": True,
            "eligible": True,
            "new_level": user.level,
            "message": f"Successfully leveled up to level {user.level}!"
        })
    else:
        return jsonify({
            "success": False,
            "eligible": False,
            "errors": errors,
            "message": "Failed to level up"
        }), 400


@api_bp.get("/users/<int:user_id>/level-up/eligibility")
def check_level_up_eligibility(user_id: int):
    """Check if a user is eligible to level up."""
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    next_level = user.level + 1
    can_level_up, missing_achievements = UserService.can_level_up(user, next_level)
    
    return jsonify({
        "eligible": can_level_up,
        "current_level": user.level,
        "next_level": next_level,
        "missing_achievements": missing_achievements,
    })


@api_bp.delete("/users/<int:user_id>/reset")
def reset_user_data(user_id: int):
    """Reset all user data (achievements, sessions, responses) - DEV ONLY."""
    from flask import current_app
    from .models import Achievement, PracticeSession, Response, DailyStat, FlaggedQuestion, db
    from .database import transaction
    
    # Check if TESTING mode is enabled
    if not current_app.config.get('TESTING'):
        return jsonify({"error": "Not available in production"}), 403
    
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Delete all user data
    with transaction():
        # Delete achievements
        Achievement.query.filter_by(user_id=user_id).delete()
        
        # Delete flagged questions
        FlaggedQuestion.query.filter_by(user_id=user_id).delete()
        
        # Delete responses (cascade should handle this, but being explicit)
        Response.query.filter_by(user_id=user_id).delete()
        
        # Delete practice sessions (cascade should handle responses, but being explicit)
        PracticeSession.query.filter_by(user_id=user_id).delete()
        
        # Delete daily stats
        DailyStat.query.filter_by(user_id=user_id).delete()
        
        # Reset user level to 1
        user.level = 1
        user.updated_at = datetime.utcnow()
        db.session.add(user)
    
    return jsonify({
        "success": True,
        "message": f"All data for user {user_id} has been reset. User level set to 1.",
    })


@api_bp.post("/users/<int:user_id>/test-setup")
def test_setup_user(user_id: int):
    """Test setup endpoint - DEV ONLY. Set user state for E2E tests.
    
    Allows setting:
    - User level (directly, bypassing achievement requirements)
    - Awards achievements (directly, without meeting requirements)
    - Creates test data state
    
    Request body:
    {
        "level": 5,  # Optional: set user level directly
        "achievements": ["addition-basics", "level-2-mastery"],  # Optional: award achievements
    }
    
    Only available in development/test environments.
    """
    from flask import current_app
    from .models import Achievement, db
    from .config.achievements import ACHIEVEMENTS_CONFIG
    
    # Check if TESTING mode is enabled
    if not current_app.config.get('TESTING'):
        return jsonify({"error": "Not available in production"}), 403
    
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json() or {}
    
    # Set level if specified (bypasses achievement checks)
    if 'level' in data:
        level = data['level']
        if level < 1 or level > 45:
            return jsonify({"error": f"Invalid level: {level}. Must be 1-45."}), 400
        
        user.level = level
        user.updated_at = datetime.utcnow()
        db.session.add(user)
    
    # Award achievements if specified (bypasses requirement checks)
    if 'achievements' in data:
        import json
        achievements_list = data['achievements']
        
        # Support both string array and object array formats
        # String format: ["first-steps", "first-victory"]
        # Object format: [{"code": "accuracy-ace-platinum", "metadata": {"test_type": "addition-1digit"}}]
        for achievement_item in achievements_list:
            # Handle string format (backward compatible)
            if isinstance(achievement_item, str):
                achievement_code = achievement_item
                metadata = None
            # Handle object format with metadata
            elif isinstance(achievement_item, dict):
                achievement_code = achievement_item.get('code') or achievement_item.get('achievement_code')
                metadata = achievement_item.get('metadata') or achievement_item.get('metadata_filter')
            else:
                continue  # Skip invalid format
            
            if not achievement_code:
                continue
            
            # Check if achievement exists in config
            if achievement_code not in ACHIEVEMENTS_CONFIG:
                continue  # Skip invalid achievement codes
            
            # Check if user already has this achievement (with same metadata if applicable)
            existing_query = Achievement.query.filter_by(
                user_id=user_id,
                code=achievement_code
            )
            
            # If metadata is provided, check for exact match
            if metadata:
                metadata_json = json.dumps(metadata, sort_keys=True)
                existing = existing_query.filter_by(achievement_metadata=metadata_json).first()
            else:
                existing = existing_query.filter_by(achievement_metadata=None).first()
            
            if not existing:
                # Get achievement config to populate required fields
                achievement_config = ACHIEVEMENTS_CONFIG[achievement_code]
                
                # Serialize metadata to JSON string if present
                metadata_json = json.dumps(metadata, sort_keys=True) if metadata else None
                
                # Create achievement record with all required fields
                achievement = Achievement(
                    user_id=user_id,
                    code=achievement_code,
                    title=achievement_config.get('title', achievement_code),
                    description=achievement_config.get('description', ''),
                    icon=achievement_config.get('icon', '🏆'),
                    category=achievement_config.get('category', 'milestone'),
                    earned_at=datetime.utcnow(),
                    achievement_metadata=metadata_json
                )
                db.session.add(achievement)
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "level": user.level,
        "message": f"Test setup completed for user {user_id}"
    })


@api_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    """Delete a user and all associated data - TEST ONLY.
    
    This endpoint permanently deletes a user and all related data including:
    - Achievements
    - Practice sessions
    - Responses
    - Daily stats
    - Flagged questions
    
    Use with caution - this operation cannot be undone.
    """
    from flask import current_app
    
    # Check if TESTING mode is enabled
    if not current_app.config.get('TESTING'):
        return jsonify({"error": "Not available in production"}), 403
    
    success, error = UserService.delete_user(user_id)
    
    if not success:
        return jsonify({"error": error}), 404
    
    return jsonify({
        "success": True,
        "message": f"User {user_id} and all associated data have been deleted.",
    })


@api_bp.delete("/reset")
def reset_all_data():
    """Reset all data in the database - TEST ONLY.
    
    This endpoint permanently deletes ALL data from the database including:
    - All users
    - All achievements
    - All practice sessions
    - All responses
    - All daily stats
    - All flagged questions
    - All test attempts
    - All questions
    - All level progression configs
    - All level problem configs
    
    This is intended for E2E test cleanup. Use with extreme caution - this operation cannot be undone.
    """
    from flask import current_app
    from .models import (
        Achievement,
        DailyStat,
        FlaggedQuestion,
        LevelProblemConfig,
        LevelProgression,
        PracticeSession,
        Question,
        Response,
        TestAttempt,
        User,
        db,
    )
    from .database import transaction
    
    # Check if TESTING mode is enabled
    if not current_app.config.get('TESTING'):
        return jsonify({"error": "Not available in production"}), 403
    
    # Delete all data in proper order to respect foreign key constraints
    with transaction():
        # Delete child records first (order matters for foreign keys)
        TestAttempt.query.delete()
        DailyStat.query.delete()
        FlaggedQuestion.query.delete()
        Response.query.delete()
        Achievement.query.delete()
        PracticeSession.query.delete()
        
        # Delete parent records
        User.query.delete()
        Question.query.delete()
        
        # Delete config tables (optional - these can be re-seeded)
        LevelProblemConfig.query.delete()
        LevelProgression.query.delete()
    
    return jsonify({
        "success": True,
        "message": "All data has been reset. Database is now empty.",
    })
