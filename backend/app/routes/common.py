"""Common utilities and shared routes."""

from __future__ import annotations

import time
from typing import Any

from flask import Blueprint, jsonify

from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService

common_bp = Blueprint("common", __name__)

# Simple in-memory cache for user data (1-2 second TTL to handle rapid duplicate requests)
_user_cache: dict[int, tuple[dict[str, Any], float]] = {}
_CACHE_TTL = 2.0  # 2 seconds TTL


def get_cached_user(user_id: int) -> dict[str, Any] | None:
    """Get cached user data if still valid."""
    if user_id in _user_cache:
        data, timestamp = _user_cache[user_id]
        if time.time() - timestamp < _CACHE_TTL:
            return data
        else:
            # Expired, remove from cache
            del _user_cache[user_id]
    return None


def cache_user(user_id: int, data: dict[str, Any]) -> None:
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


def serialize_user(user, metrics: dict[str, Any] | None = None, achievements_list: list[Any] | None = None, weekly_gain: int | None = None) -> dict[str, Any]:
    """Serialize a user with metrics and achievements (single user version).
    
    NOTE: PIN is NOT included in the response for security reasons.
    PIN verification must be done via the /api/users/<id>/verify-pin endpoint.
    
    NOTE: This function should NOT award new achievements - it should only return existing ones.
    Achievement awarding should only happen during session completion.
    """
    from ..services.user_service import UserService
    
    if metrics is None:
        metrics = AnalyticsService.compute_user_metrics(user.id)
    # Get existing achievements only - do NOT award new ones during user fetch
    # Achievement awarding should only happen during session completion with session_id
    if achievements_list is None:
        achievements_list = AchievementService.get_user_achievements(user.id)

    if weekly_gain is None:
        weekly_gain = AnalyticsService.get_weekly_gain(user.id)

    return serialize_user_fast(user, metrics, achievements_list, weekly_gain)


def serialize_user_fast(
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


@common_bp.get("/hello")
def hello_world():
    """Return a simple greeting to verify the end-to-end flow."""
    return jsonify(message="Hello from Math Helper API")


@common_bp.delete("/reset")
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
    from ..models import (
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
    from ..database import transaction
    
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

