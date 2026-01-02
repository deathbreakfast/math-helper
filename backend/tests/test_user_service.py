"""Comprehensive tests for UserService.

Tests cover all methods in UserService to achieve >80% coverage.
"""

import pytest
from datetime import datetime

from app import create_app, db
from app.models import Achievement, User
from app.services.user_service import UserService
from app.services.achievement_service import AchievementService


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(test_config={'TESTING': True})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(display_name="Test User", pin="1234", avatar="🐯", level=1)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


class TestUserService:
    """Test suite for UserService static methods."""

    def test_create_user_basic(self, app):
        """Test create_user creates a basic user."""
        with app.app_context():
            user, errors = UserService.create_user("New User", "5678", "🐰")
            
            assert user is not None
            assert user.display_name == "New User"
            assert user.pin == "5678"
            assert user.avatar == "🐰"
            assert user.level == 1
            assert errors == []

    def test_create_user_no_avatar(self, app):
        """Test create_user without avatar."""
        with app.app_context():
            user, errors = UserService.create_user("New User", "5678")
            
            assert user is not None
            assert user.avatar is None
            assert errors == []

    def test_create_user_name_too_short(self, app):
        """Test create_user validates name length."""
        with app.app_context():
            user, errors = UserService.create_user("A", "5678")
            
            assert user is None
            assert len(errors) > 0
            assert "at least 2 characters" in errors[0]

    def test_create_user_name_whitespace(self, app):
        """Test create_user trims whitespace from name."""
        with app.app_context():
            user, errors = UserService.create_user("  Test User  ", "5678")
            
            assert user is not None
            assert user.display_name == "Test User"
            assert errors == []

    def test_create_user_pin_not_digits(self, app):
        """Test create_user validates PIN is digits only."""
        with app.app_context():
            user, errors = UserService.create_user("Test User", "abcd")
            
            assert user is None
            assert len(errors) > 0
            assert "4-digit number" in errors[0]

    def test_create_user_pin_wrong_length(self, app):
        """Test create_user validates PIN length."""
        with app.app_context():
            user, errors = UserService.create_user("Test User", "123")
            
            assert user is None
            assert len(errors) > 0
            assert "4-digit number" in errors[0]

    def test_create_user_duplicate_name(self, app, test_user):
        """Test create_user rejects duplicate names."""
        with app.app_context():
            user, errors = UserService.create_user(test_user.display_name, "5678")
            
            assert user is None
            assert len(errors) > 0
            assert "already taken" in errors[0]

    def test_get_user(self, app, test_user):
        """Test get_user retrieves user by ID."""
        with app.app_context():
            user = UserService.get_user(test_user.id)
            
            assert user is not None
            assert user.id == test_user.id
            assert user.display_name == test_user.display_name

    def test_get_user_not_found(self, app):
        """Test get_user returns None for non-existent user."""
        with app.app_context():
            user = UserService.get_user(99999)
            assert user is None

    def test_get_user_by_name(self, app, test_user):
        """Test get_user_by_name retrieves user case-insensitively."""
        with app.app_context():
            user = UserService.get_user_by_name(test_user.display_name.upper())
            
            assert user is not None
            assert user.id == test_user.id

    def test_get_user_by_name_not_found(self, app):
        """Test get_user_by_name returns None for non-existent name."""
        with app.app_context():
            user = UserService.get_user_by_name("Non Existent")
            assert user is None

    def test_list_users(self, app):
        """Test list_users returns all users."""
        with app.app_context():
            user1 = User(display_name="User 1", pin="1111", avatar="🐯", level=1)
            user2 = User(display_name="User 2", pin="2222", avatar="🐰", level=1)
            db.session.add_all([user1, user2])
            db.session.commit()
            
            users = UserService.list_users()
            
            assert len(users) >= 2
            user_names = [u.display_name for u in users]
            assert "User 1" in user_names
            assert "User 2" in user_names

    def test_list_users_ordered_by_created_at(self, app):
        """Test list_users orders by creation date."""
        with app.app_context():
            user1 = User(display_name="User 1", pin="1111", avatar="🐯", level=1)
            db.session.add(user1)
            db.session.commit()
            
            import time
            time.sleep(0.1)  # Small delay to ensure different timestamps
            
            user2 = User(display_name="User 2", pin="2222", avatar="🐰", level=1)
            db.session.add(user2)
            db.session.commit()
            
            users = UserService.list_users()
            
            # Should be ordered by created_at ascending
            assert users[0].created_at <= users[1].created_at

    def test_verify_pin_correct(self, app, test_user):
        """Test verify_pin returns True for correct PIN."""
        with app.app_context():
            result = UserService.verify_pin(test_user, "1234")
            assert result is True

    def test_verify_pin_incorrect(self, app, test_user):
        """Test verify_pin returns False for incorrect PIN."""
        with app.app_context():
            result = UserService.verify_pin(test_user, "9999")
            assert result is False

    # Legacy level up tests removed - achievement-based level up system no longer exists
    # User level is now automatically calculated from XP

    def test_update_user(self, app, test_user):
        """Test update_user updates user fields."""
        with app.app_context():
            updated = UserService.update_user(
                test_user,
                display_name="Updated Name",
                avatar="🦁"
            )
            
            assert updated.display_name == "Updated Name"
            assert updated.avatar == "🦁"
            assert updated.updated_at is not None

    def test_update_user_updates_updated_at(self, app, test_user):
        """Test update_user updates updated_at timestamp."""
        with app.app_context():
            original_updated_at = test_user.updated_at
            
            UserService.update_user(test_user, display_name="New Name")
            
            db.session.refresh(test_user)
            assert test_user.updated_at is not None
            assert test_user.updated_at >= original_updated_at

    def test_update_user_ignores_invalid_fields(self, app, test_user):
        """Test update_user ignores fields that don't exist."""
        with app.app_context():
            original_name = test_user.display_name
            
            UserService.update_user(test_user, invalid_field="value")
            
            db.session.refresh(test_user)
            assert test_user.display_name == original_name
            assert not hasattr(test_user, "invalid_field")

    def test_delete_user_success(self, app, test_user):
        """Test delete_user successfully deletes user."""
        with app.app_context():
            user_id = test_user.id
            
            success, error = UserService.delete_user(user_id)
            
            assert success is True
            assert error is None
            
            # Verify user is deleted
            deleted_user = UserService.get_user(user_id)
            assert deleted_user is None

    def test_delete_user_not_found(self, app):
        """Test delete_user returns False for non-existent user."""
        with app.app_context():
            success, error = UserService.delete_user(99999)
            
            assert success is False
            assert error == "User not found"

    def test_delete_user_cascades(self, app, test_user):
        """Test delete_user cascades to related data."""
        with app.app_context():
            # Create achievement for user
            achievement = Achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test",
                description="Test",
                icon="🏆",
                category="milestone"
            )
            db.session.add(achievement)
            db.session.commit()
            
            user_id = test_user.id
            achievement_id = achievement.id
            
            success, _ = UserService.delete_user(user_id)
            
            assert success is True
            
            # Verify achievement is also deleted (cascade)
            deleted_achievement = db.session.get(Achievement, achievement_id)
            assert deleted_achievement is None

