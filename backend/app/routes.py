from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List
from uuid import uuid4

from flask import Blueprint, jsonify, request
from sqlalchemy import case, func

from .models import Achievement, Question, Response, User, db

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

    errors: list[str] = []
    if len(display_name) < 2:
        errors.append("Name must be at least 2 characters long.")
    if not pin.isdigit() or len(pin) != 4:
        errors.append("PIN must be a 4-digit number.")
    if User.query.filter_by(display_name=display_name).first():
        errors.append("Name is already taken.")

    if errors:
        return jsonify({"errors": errors}), 400

    user = User(avatar=avatar, display_name=display_name, pin=pin)
    db.session.add(user)
    db.session.commit()

    return jsonify(_serialize_user(user)), 201


@api_bp.get("/users")
def list_users():
    """Return all learners with derived dashboard metrics."""

    users = User.query.order_by(User.created_at.asc()).all()
    return jsonify({"users": [_serialize_user(user) for user in users]})


@api_bp.get("/users/<int:user_id>")
def retrieve_user(user_id: int):
    """Return dashboard metrics for a single learner."""

    user = User.query.get_or_404(user_id)
    return jsonify(_serialize_user(user))


@api_bp.get("/achievements")
def list_achievements():
    """Return persisted achievements, optionally filtered to a user."""

    user_id = request.args.get("user_id", type=int)

    users_query = User.query
    if user_id is not None:
        users_query = users_query.filter_by(id=user_id)

    for user in users_query.all():
        metrics = _compute_user_metrics(user.id)
        _ensure_achievements(user, metrics)

    query = Achievement.query
    if user_id is not None:
        query = query.filter_by(user_id=user_id)

    achievements = query.order_by(Achievement.earned_at.desc()).limit(50).all()
    return jsonify({"achievements": [_serialize_achievement(a) for a in achievements]})


@api_bp.post("/practice/submissions")
def submit_practice_attempts():
    """Mock practice submissions while verifying the learner PIN."""

    payload = request.get_json(silent=True) or {}
    pin = (payload.get("pin") or "").strip()
    user_id = payload.get("userId") or payload.get("user_id")
    user_name = (payload.get("userName") or payload.get("user_name") or "").strip()

    if not pin.isdigit() or len(pin) != 4:
        return jsonify({"error": "A 4-digit PIN is required to submit practice."}), 400

    user: User | None = None
    if user_id is not None:
        try:
            user = User.query.get(int(user_id))
        except (TypeError, ValueError):
            user = None

    if user is None and user_name:
        user = (
            User.query.filter(func.lower(User.display_name) == user_name.lower())
            .order_by(User.id.asc())
            .first()
        )

    if user is None:
        return jsonify({"error": "Learner not found. Create the profile before practicing."}), 404

    if user.pin != pin:
        return jsonify({"error": "PIN verification failed for this learner."}), 403

    attempts_payload = payload.get("attempts") or []
    normalized_attempts: List[Dict[str, Any]] = []
    correct_count = 0

    for attempt in attempts_payload:
        question_id = attempt.get("questionId") or attempt.get("question_id") or f"mock-{uuid4().hex[:6]}"
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

    session_payload = {
        "id": f"practice-{uuid4().hex[:8]}",
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
        "status": "mocked",
        "message": payload.get("notes") or "Practice submissions captured for the session.",
    }

    return jsonify({"session": session_payload})


def _serialize_user(user: User) -> Dict[str, Any]:
    metrics = _compute_user_metrics(user.id)
    achievements = _ensure_achievements(user, metrics)
    share_url = {"user": user.display_name, "pin": user.pin}

    return {
        "id": user.id,
        "name": user.display_name,
        "avatar": user.avatar,
        "pin": user.pin,
        "level": user.level,
        "questionsAnswered": metrics["questions_answered"],
        "averageSpeed": metrics["average_speed_seconds"],
        "stats": metrics["operation_stats"],
        "achievements": achievements,
        "share_url_params": share_url,
    }


def _serialize_achievement(achievement: Achievement) -> Dict[str, Any]:
    return {
        "id": achievement.id,
        "userId": achievement.user_id,
        "title": achievement.title,
        "description": achievement.description,
        "icon": achievement.icon,
        "category": achievement.category,
        "earnedAt": achievement.earned_at.isoformat(),
    }


def _compute_user_metrics(user_id: int) -> Dict[str, Any]:
    total_answers = (
        db.session.query(func.count())
        .select_from(Response)
        .filter_by(user_id=user_id)
        .scalar()
        or 0
    )

    avg_duration_ms = (
        db.session.query(func.avg(Response.duration_ms))
        .filter(Response.user_id == user_id, Response.duration_ms.isnot(None))
        .scalar()
    )

    last_activity_at = (
        db.session.query(func.max(Response.answered_at)).filter_by(user_id=user_id).scalar()
    )

    operation_rows = (
        db.session.query(
            Question.operation.label("operation"),
            func.count(Response.id).label("attempts"),
            func.sum(
                case((Response.is_correct.is_(True), 1), else_=0)
            ).label("correct"),
            func.avg(Response.duration_ms).label("avg_duration_ms"),
        )
        .join(Response.question)
        .filter(Response.user_id == user_id)
        .group_by(Question.operation)
        .all()
    )

    operation_stats = _build_operation_stats(operation_rows)
    streaks = _calculate_streaks(user_id)

    return {
        "questions_answered": total_answers,
        "average_speed_seconds": _format_speed(avg_duration_ms),
        "last_activity_at": last_activity_at,
        "operation_stats": {
            **operation_stats,
            "currentStreak": streaks["current"],
            "bestStreak": streaks["best"],
        },
    }


def _build_operation_stats(rows: List[Any]) -> Dict[str, Any]:
    stats = {
        "additionAccuracy": 0,
        "subtractionAccuracy": 0,
        "multiplicationAccuracy": 0,
        "divisionAccuracy": 0,
        "additionSpeed": 0.0,
        "subtractionSpeed": 0.0,
        "multiplicationSpeed": 0.0,
        "divisionSpeed": 0.0,
    }

    key_map = {
        "addition": ("additionAccuracy", "additionSpeed"),
        "subtraction": ("subtractionAccuracy", "subtractionSpeed"),
        "multiplication": ("multiplicationAccuracy", "multiplicationSpeed"),
        "division": ("divisionAccuracy", "divisionSpeed"),
    }

    for row in rows:
        operation = (row.operation or "").lower()
        mapping = key_map.get(operation)
        if not mapping or row.attempts == 0:
            continue

        accuracy_key, speed_key = mapping
        correct = row.correct or 0
        stats[accuracy_key] = round((correct / row.attempts) * 100)
        stats[speed_key] = _format_speed(row.avg_duration_ms)

    return stats


def _format_speed(duration_ms: float | None) -> float:
    if duration_ms is None:
        return 0.0
    return round(duration_ms / 1000, 1)


def _ensure_achievements(user: User, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Ensure required achievements exist in the database for this user."""

    total_answers = metrics["questions_answered"]
    avg_speed = metrics["average_speed_seconds"]
    stats = metrics["operation_stats"]
    earned_at = metrics["last_activity_at"] or user.created_at or datetime.utcnow()

    accuracy_candidates = [
        stats.get("additionAccuracy", 0),
        stats.get("subtractionAccuracy", 0),
        stats.get("multiplicationAccuracy", 0),
        stats.get("divisionAccuracy", 0),
    ]
    max_accuracy = max(accuracy_candidates) if accuracy_candidates else 0

    rules = [
        (
            "century",
            total_answers >= 100,
            "Century Club",
            "Answered 100+ questions.",
            "💯",
            "milestone",
        ),
        (
            "speed-demon",
            avg_speed > 0 and avg_speed <= 3 and total_answers >= 10,
            "Speed Demon",
            "Average response time under 3 seconds.",
            "⚡",
            "speed",
        ),
        (
            "perfect-week",
            stats.get("currentStreak", 0) >= 7,
            "Perfect Week",
            "Practiced every day this week.",
            "🌟",
            "consistency",
        ),
        (
            "accuracy-ace",
            max_accuracy >= 95,
            "Accuracy Ace",
            "Maintained 95%+ accuracy in at least one operation.",
            "🎯",
            "accuracy",
        ),
    ]

    created = False
    for code, condition, title, description, icon, category in rules:
        if not condition:
            continue
        exists = Achievement.query.filter_by(user_id=user.id, code=code).first()
        if exists:
            continue

        db.session.add(
            Achievement(
                user=user,
                code=code,
                title=title,
                description=description,
                icon=icon,
                category=category,
                earned_at=earned_at,
            )
        )
        created = True

    if created:
        db.session.commit()

    achievements = (
        Achievement.query.filter_by(user_id=user.id)
        .order_by(Achievement.earned_at.desc())
        .all()
    )
    return [_serialize_achievement(a) for a in achievements]


def _calculate_streaks(user_id: int) -> Dict[str, int]:
    response_dates = [
        row[0].date()
        for row in db.session.query(Response.answered_at)
        .filter_by(user_id=user_id)
        .order_by(Response.answered_at.asc())
        .all()
    ]

    if not response_dates:
        return {"current": 0, "best": 0}

    unique_dates = sorted(set(response_dates))

    best = _longest_consecutive_run(unique_dates)
    current = _current_run(unique_dates)

    return {"current": current, "best": best}


def _longest_consecutive_run(sorted_dates: List[date]) -> int:
    best = 1
    streak = 1
    for prev, curr in zip(sorted_dates, sorted_dates[1:]):
        if (curr - prev).days == 1:
            streak += 1
            best = max(best, streak)
        else:
            streak = 1
    return best


def _current_run(sorted_dates: List[date]) -> int:
    streak = 1
    last = sorted_dates[-1]
    today = date.today()
    if (today - last).days > 1:
        return 0

    for curr in reversed(sorted_dates[:-1]):
        if (last - curr).days == 1:
            streak += 1
            last = curr
        else:
            break
    return streak
