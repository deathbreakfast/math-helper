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


def get_achievement_constraint(achievement_code: str) -> dict[str, Any]:
    """Get constraint configuration for an achievement code.
    
    Args:
        achievement_code: The achievement code to look up
        
    Returns:
        Constraint dict with allow_multiple_per_tier, allow_multiple_per_session, unique_achievement
        Defaults to unique behavior if not specified (backward compatibility)
    """
    configs = get_achievement_configs()
    config = configs.get(achievement_code, {})
    constraint = config.get("constraint", {})
    
    # Default constraint (unique behavior) for backward compatibility
    if not constraint:
        return {
            "allow_multiple_per_tier": False,
            "allow_multiple_per_session": False,
            "unique_achievement": True,
        }
    
    return constraint


def _check_existing_achievement(
    user_id: int,
    code: str,
    metadata: dict[str, Any] | None,
    session_id: int | None,
    constraint: dict[str, Any]
) -> Achievement | None:
    """Check for existing achievement based on constraint rules.
    
    Args:
        user_id: User ID
        code: Achievement code
        metadata: Achievement metadata dict
        session_id: Session ID
        constraint: Constraint configuration
        
    Returns:
        Existing Achievement if found, None otherwise
    """
    # Unique achievements: check if any instance exists (ignoring metadata and session)
    if constraint.get("unique_achievement"):
        existing = Achievement.query.filter_by(
            user_id=user_id, 
            code=code
        ).first()
        return existing
    
    # Multiple per tier, once per session: check if same tier awarded in this session
    if constraint.get("allow_multiple_per_tier") and not constraint.get("allow_multiple_per_session"):
        if session_id:
            # Check if achievement with this code already exists for this session
            # We check by session_id column (database field) and code
            # Note: Metadata may or may not include session_id depending on when it was stored
            existing = Achievement.query.filter_by(
                user_id=user_id,
                code=code,
                session_id=session_id
            ).first()
            return existing
        # No session_id provided, fall through to one-per-tier check
    
    # One per tier (with or without multiple per session): check by code + metadata
    # For achievements without metadata, check by code only
    metadata_json = json.dumps(metadata, sort_keys=True) if metadata else None
    if metadata_json:
        existing = Achievement.query.filter_by(
            user_id=user_id,
            code=code,
            achievement_metadata=metadata_json
        ).first()
    else:
        existing = Achievement.query.filter_by(
            user_id=user_id,
            code=code
        ).filter(
            (Achievement.achievement_metadata.is_(None)) | (Achievement.achievement_metadata == "")
        ).first()
    
    return existing


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

    # Get constraint rules for this achievement
    constraint = get_achievement_constraint(code)
    
    # Check if already exists based on constraint rules
    existing = _check_existing_achievement(
        user_id=user_id,
        code=code,
        metadata=metadata,
        session_id=session_id,
        constraint=constraint
    )
    
    if existing:
        # If we have a session_id and the existing achievement doesn't have one (or has a different one),
        # update it to link to this session. This ensures achievements earned in this session are properly linked.
        if session_id and existing.session_id != session_id:
            existing.session_id = session_id
            db.session.add(existing)
            db.session.commit()
        return existing
    
    # For achievements that allow multiple per tier but once per session, add session_id to metadata
    # This makes each instance unique in the database (bypassing unique constraint)
    final_metadata = metadata.copy() if metadata else {}
    if (constraint.get("allow_multiple_per_tier") and 
        not constraint.get("allow_multiple_per_session") and 
        session_id and 
        not constraint.get("unique_achievement")):
        # Add session_id to metadata to make this instance unique
        final_metadata["session_id"] = session_id
    
    # Serialize metadata to JSON string if provided (sort keys for consistency)
    metadata_json = json.dumps(final_metadata, sort_keys=True) if final_metadata else None

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

