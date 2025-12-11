"""Achievement-related API routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService
from ..services.level_config_service import LevelConfigService
from ..services.user_service import UserService

achievements_bp = Blueprint("achievements", __name__)


@achievements_bp.get("/achievements")
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


@achievements_bp.get("/achievements/definitions")
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


@achievements_bp.get("/achievements/<code>/requirements")
def get_achievement_requirements(code: str):
    """Get requirements for a specific achievement."""
    config = LevelConfigService.get_achievement_config(code)
    if not config:
        return jsonify({"error": f"Achievement {code} not found"}), 404
    return jsonify({"achievement_code": code, "requirements": config.get("requirements", {})})

