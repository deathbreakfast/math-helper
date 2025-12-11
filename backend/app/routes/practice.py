"""Practice session-related API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Blueprint, jsonify, request

from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService
from ..services.practice_service import PracticeService
from ..services.session_engine_service import SessionEngineService
from ..services.test_eligibility_service import TestEligibilityService
from ..services.user_service import UserService
from ..config.test_requirements import get_all_test_requirements, get_test_requirements

practice_bp = Blueprint("practice", __name__)


@practice_bp.post("/practice/submissions")
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


@practice_bp.get("/practice/sessions/incomplete")
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


@practice_bp.get("/practice/sessions/<int:session_id>")
def get_session_details(session_id: int):
    """Get session details including questions and responses."""
    session_data = PracticeService.get_session_with_details(session_id)
    
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(session_data), 200


@practice_bp.get("/practice/sessions/<int:session_id>/answers")
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


@practice_bp.post("/practice/sessions/start")
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


@practice_bp.get("/practice/sessions/eligible-tests")
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


@practice_bp.get("/practice/test-requirements")
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


@practice_bp.get("/practice/test-eligibility")
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


@practice_bp.post("/practice/questions/check")
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
    from ..models import PracticeSession

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


@practice_bp.post("/practice/sessions/<int:session_id>/complete")
def complete_session(session_id: int):
    """Complete a practice session, award achievements, and check leveling."""
    payload = request.get_json(silent=True) or {}
    total_duration_ms = payload.get("total_duration_ms") or payload.get("totalDurationMs")

    from ..models import PracticeSession, Response

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
        from ..models import TestAttempt, db
        
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



