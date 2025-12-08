"""User service for CRUD operations, PIN verification, and level management."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ..database import log_query, transaction
from ..models import Achievement, LevelProgression, User, db


class UserService:
    """Service for user-related operations."""

    @staticmethod
    @log_query
    def create_user(display_name: str, pin: str, avatar: str | None = None) -> tuple[User, list[str]]:
        """Create a new user with validation.

        Returns:
            Tuple of (User object, list of error messages)
        """
        errors: list[str] = []

        if len(display_name.strip()) < 2:
            errors.append("Name must be at least 2 characters long.")
        if not pin.isdigit() or len(pin) != 4:
            errors.append("PIN must be a 4-digit number.")

        if errors:
            return None, errors  # type: ignore

        # Check for duplicate name
        existing = User.query.filter_by(display_name=display_name).first()
        if existing:
            errors.append("Name is already taken.")
            return None, errors  # type: ignore

        with transaction():
            user = User(avatar=avatar, display_name=display_name.strip(), pin=pin, level=1)
            db.session.add(user)
            db.session.flush()  # Get the ID without committing

        return user, []

    @staticmethod
    @log_query
    def get_user(user_id: int) -> User | None:
        """Get a user by ID."""
        return User.query.get(user_id)

    @staticmethod
    @log_query
    def get_user_by_name(display_name: str) -> User | None:
        """Get a user by display name (case-insensitive)."""
        return User.query.filter(func.lower(User.display_name) == display_name.lower()).first()

    @staticmethod
    @log_query
    def list_users() -> list[User]:
        """List all users ordered by creation date with eager-loaded relationships."""
        return (
            User.query
            .options(
                joinedload(User.achievements),
                # Note: We don't eager load responses/practice_sessions as they can be large
                # We'll batch query them in analytics service instead
            )
            .order_by(User.created_at.asc())
            .all()
        )

    @staticmethod
    @log_query
    def verify_pin(user: User, pin: str) -> bool:
        """Verify a PIN for a user."""
        return user.pin == pin

    @staticmethod
    @log_query
    def can_level_up(user: User, target_level: int) -> tuple[bool, list[str]]:
        """Check if a user can level up to the target level.

        Returns:
            Tuple of (can_level_up: bool, missing_achievements: list[str])
        """
        if target_level <= user.level:
            return False, ["Target level must be greater than current level."]

        if target_level == 1:
            return True, []  # Level 1 has no requirements

        # Get required achievements for target level from config (includes quantity)
        from ..config.level_progression_config import LEVEL_PROGRESSION_CONFIG
        config_requirements = LEVEL_PROGRESSION_CONFIG.get(target_level, [])
        
        # Also get from database for backward compatibility
        db_requirements = (
            LevelProgression.query.filter_by(target_level=target_level)
            .order_by(LevelProgression.order.asc())
            .all()
        )

        # Use config if available, otherwise fall back to database
        if config_requirements:
            requirements = config_requirements
        elif db_requirements:
            # Convert database requirements to config format
            requirements = [
                {"achievement_code": req.required_achievement_code, "quantity": 1, "order": req.order or 1}
                for req in db_requirements
            ]
        else:
            # No requirements defined, allow level up
            return True, []

        # Check which requirements are missing
        missing = []
        for req in requirements:
            achievement_code = req.get("achievement_code", "")
            quantity = req.get("quantity", 1)
            metadata_filter = req.get("metadata_filter")
            
            # Count achievements with metadata filter support
            from .achievement_service import AchievementService
            count = AchievementService.count_achievements_by_code_with_filters(
                user_id=user.id,
                achievement_code=achievement_code,
                metadata_filter=metadata_filter,
            )
            
            if count < quantity:
                filter_str = f" with metadata {metadata_filter}" if metadata_filter else ""
                missing.append(f"{achievement_code}{filter_str} (need {quantity}, have {count})")

        return len(missing) == 0, missing

    @staticmethod
    @log_query
    def level_up(user: User, target_level: int) -> tuple[bool, list[str]]:
        """Level up a user to the target level if requirements are met.

        Returns:
            Tuple of (success: bool, error_messages: list[str])
        """
        can_up, missing = UserService.can_level_up(user, target_level)

        if not can_up:
            return False, [f"Missing required achievements: {', '.join(missing)}"]

        with transaction():
            user.level = target_level
            user.updated_at = datetime.utcnow()
            db.session.add(user)

        return True, []

    @staticmethod
    @log_query
    def update_user(user: User, **kwargs: Any) -> User:
        """Update user fields."""
        with transaction():
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            db.session.add(user)

        return user

    @staticmethod
    @log_query
    def delete_user(user_id: int) -> tuple[bool, str | None]:
        """Delete a user and all associated data.
        
        Returns:
            Tuple of (success: bool, error_message: str | None)
        """
        user = UserService.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Cascading deletes will handle related data (achievements, sessions, responses, etc.)
        # due to cascade="all, delete" relationships in models
        with transaction():
            db.session.delete(user)
        
        return True, None

