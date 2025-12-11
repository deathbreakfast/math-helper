"""Utility functions for achievement operations."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from ...models import Achievement
from ... import db
from ...database import transaction
from ...services.level_config_service import LevelConfigService

# Debug logging configuration
DEBUG_ACHIEVEMENTS = os.getenv("DEBUG_ACHIEVEMENTS", "false").lower() == "true"
DEBUG_LOG_FILE = os.getenv("DEBUG_ACHIEVEMENTS_LOG", "achievements_debug.log")

# Cache for achievement configs (rarely changes, so cache indefinitely)
_achievement_configs_cache: dict[str, Any] | None = None


def get_achievement_configs() -> dict[str, Any]:
    """Get achievement configs with caching."""
    global _achievement_configs_cache
    if _achievement_configs_cache is None:
        _achievement_configs_cache = LevelConfigService.get_all_achievement_configs()
    return _achievement_configs_cache


def clear_achievement_configs_cache() -> None:
    """Clear the achievement configs cache (for testing or config updates)."""
    global _achievement_configs_cache
    _achievement_configs_cache = None


def debug_print(*args, **kwargs):
    """Print debug info to console and/or file based on configuration."""
    if not DEBUG_ACHIEVEMENTS:
        return
    
    message = " ".join(str(arg) for arg in args)
    
    # Print to console
    print(message, **kwargs)
    
    # Write to file
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
    except Exception:
        pass  # Silently fail if file write fails


def create_achievement(
    user_id: int,
    code: str,
    title: str,
    description: str,
    icon: str,
    category: str,
    earned_at: datetime | None = None,
    session_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> Achievement:
    """Manually create an achievement for a user.
    
    Args:
        user_id: User ID
        code: Achievement code
        title: Achievement title
        description: Achievement description
        icon: Achievement icon
        category: Achievement category
        earned_at: When achievement was earned (defaults to now)
        session_id: Optional session ID to link achievement
        metadata: Optional metadata dict (will be stored as JSON string)
    """
    if earned_at is None:
        earned_at = datetime.utcnow()

    # Serialize metadata to JSON string if provided
    metadata_json = json.dumps(metadata) if metadata else None

    # Check if already exists - need to check both code and metadata
    # For achievements without metadata, check by code only
    # For achievements with metadata, check by code and metadata
    if metadata_json:
        existing = Achievement.query.filter_by(
            user_id=user_id, code=code, achievement_metadata=metadata_json
        ).first()
    else:
        existing = Achievement.query.filter_by(
            user_id=user_id, code=code
        ).filter(
            (Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == "")
        ).first()
    
    if existing:
        # If we have a session_id and the existing achievement doesn't have one (or has a different one),
        # update it to link to this session. This ensures achievements earned in this session are properly linked.
        if session_id and existing.session_id != session_id:
            existing.session_id = session_id
            db.session.add(existing)
            db.session.commit()
        return existing

    with transaction():
        achievement = Achievement(
            user_id=user_id,
            code=code,
            title=title,
            description=description,
            icon=icon,
            category=category,
            earned_at=earned_at,
            session_id=session_id,
            achievement_metadata=metadata_json,
        )
        db.session.add(achievement)
        db.session.flush()

    return achievement


def serialize_achievement(achievement: Achievement, user_name: str | None = None) -> dict[str, Any]:
    """Serialize an achievement to a dictionary.
    
    Args:
        achievement: The achievement object to serialize
        user_name: Optional user name to include in serialization
    """
    result = {
        "id": str(achievement.id),
        "code": achievement.code,
        "userId": achievement.user_id,
        "title": achievement.title,
        "description": achievement.description,
        "icon": achievement.icon,
        "category": achievement.category,
        "earnedAt": achievement.earned_at.isoformat(),
        "sessionId": achievement.session_id if achievement.session_id else None,
    }
    if achievement.achievement_metadata:
        try:
            result["metadata"] = json.loads(achievement.achievement_metadata)
        except (json.JSONDecodeError, TypeError):
            result["metadata"] = None
    if user_name:
        result["userName"] = user_name
    return result

