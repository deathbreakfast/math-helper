"""User service for CRUD operations, PIN verification, and level management."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ..database import log_query, transaction
from ..models import Achievement, User, db


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
        return db.session.get(User, user_id)

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

