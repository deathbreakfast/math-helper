"""User-related API routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Blueprint, jsonify, request

from ..services.achievement_service import AchievementService
from ..services.analytics_service import AnalyticsService
from ..services.user_service import UserService
from .common import cache_user, get_cached_user, invalidate_user_cache, serialize_user, serialize_user_fast

users_bp = Blueprint("users", __name__)


@users_bp.post("/users")
def create_user():
    """Persist a new learner with a plain-text 4-digit PIN."""
    payload = request.get_json(silent=True) or {}
    avatar = payload.get("avatar")
    display_name = (payload.get("name") or "").strip()
    pin = (payload.get("pin") or "").strip()

    user, errors = UserService.create_user(display_name, pin, avatar)

    if errors:
        return jsonify({"errors": errors}), 400

    return jsonify(serialize_user(user)), 201


@users_bp.get("/users")
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
            serialize_user_fast(
                user,
                all_metrics.get(user.id, {}),
                all_achievements.get(user.id, []),
                all_weekly_gains.get(user.id, 0)
            )
            for user in users
        ]
    })


@users_bp.get("/users/<int:user_id>")
def retrieve_user(user_id: int):
    """Return dashboard metrics for a single learner.
    
    Uses request-level caching (1-2 second TTL) to handle rapid duplicate requests
    during parallel test execution.
    """
    # Check cache first
    cached_data = get_cached_user(user_id)
    if cached_data is not None:
        return jsonify(cached_data)
    
    user = UserService.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    serialized = serialize_user(user)
    
    # Cache the result
    cache_user(user_id, serialized)
    
    return jsonify(serialized)


@users_bp.post("/users/<int:user_id>/verify-pin")
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


# Legacy achievement-based level up endpoints removed
# User level is now automatically calculated from XP (XPService)


@users_bp.delete("/users/<int:user_id>/reset")
def reset_user_data(user_id: int):
    """Reset all user data (achievements, sessions, responses) - DEV ONLY."""
    from flask import current_app
    from ..models import Achievement, PracticeSession, Response, DailyStat, FlaggedQuestion, db
    from ..database import transaction
    
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
    
    # Prevent stale cached user responses after mutating user state
    invalidate_user_cache(user_id)

    return jsonify({
        "success": True,
        "message": f"All data for user {user_id} has been reset. User level set to 1.",
    })


@users_bp.post("/users/<int:user_id>/test-setup")
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
    from ..models import Achievement, db
    from ..config.achievements import ACHIEVEMENTS_CONFIG
    
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
        # Object format: [{"code": "accuracy-ace-platinum", "metadata": {"concept_id": "c_concept_001"}}]
        # Legacy: [{"code": "accuracy-ace-platinum", "metadata": {"test_type": "addition-1digit"}}] (will be translated)
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
            
            # Translate legacy test_type to concept_id if present
            if metadata and isinstance(metadata, dict) and metadata.get("test_type"):
                from ..config.legacy_test_type_to_level import LEGACY_TEST_TYPE_TO_LEVEL
                test_type = str(metadata.get("test_type"))
                mapped_level = LEGACY_TEST_TYPE_TO_LEVEL.get(test_type)
                if mapped_level is not None:
                    # Convert level to concept_id format: c_concept_{level:03d}
                    concept_id = f"c_concept_{mapped_level:03d}"
                    metadata = {**metadata, "concept_id": concept_id}
                    metadata.pop("test_type", None)
                else:
                    # Unknown test_type, remove it
                    metadata = {**metadata}
                    metadata.pop("test_type", None)
            
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
    # Prevent stale cached user responses after mutating user state
    invalidate_user_cache(user_id)
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "level": user.level,
        "message": f"Test setup completed for user {user_id}"
    })


@users_bp.delete("/users/<int:user_id>")
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

