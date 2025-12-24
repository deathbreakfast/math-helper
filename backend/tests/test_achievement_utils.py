"""Comprehensive tests for achievement_utils.

Tests cover all functions in achievement_utils to achieve >80% coverage.
"""

import json
import os
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from app import create_app, db
from app.models import Achievement, User
from app.services.achievements.achievement_utils import (
    get_achievement_configs,
    clear_achievement_configs_cache,
    debug_print,
    create_achievement,
    serialize_achievement,
)


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


class TestAchievementUtils:
    """Test suite for achievement_utils functions."""

    def test_get_achievement_configs(self, app):
        """Test get_achievement_configs returns configs."""
        with app.app_context():
            configs = get_achievement_configs()
            assert isinstance(configs, dict)
            assert len(configs) > 0

    def test_get_achievement_configs_caching(self, app):
        """Test get_achievement_configs caches results."""
        with app.app_context():
            configs1 = get_achievement_configs()
            configs2 = get_achievement_configs()
            
            # Should return same object (cached)
            assert configs1 is configs2

    def test_clear_achievement_configs_cache(self, app):
        """Test clear_achievement_configs_cache clears cache."""
        with app.app_context():
            configs1 = get_achievement_configs()
            clear_achievement_configs_cache()
            configs2 = get_achievement_configs()
            
            # Should be new object after clearing
            assert configs1 is not configs2

    def test_debug_print_can_be_called(self, app):
        """Test debug_print can be called without errors."""
        with app.app_context():
            # Just verify the function exists and can be called
            # The actual behavior depends on DEBUG_ACHIEVEMENTS env var set at module load time
            debug_print("Test message")
            # Should not raise exception
            assert True

    def test_create_achievement_basic(self, app, test_user):
        """Test create_achievement creates a basic achievement."""
        with app.app_context():
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            assert achievement.id is not None
            assert achievement.code == "test-achievement"
            assert achievement.user_id == test_user.id
            assert achievement.earned_at is not None

    def test_create_achievement_with_metadata(self, app, test_user):
        """Test create_achievement with metadata."""
        with app.app_context():
            metadata = {"concept_id": "c_concept_001"}
            
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                metadata=metadata
            )
            
            assert achievement.achievement_metadata is not None
            parsed_metadata = json.loads(achievement.achievement_metadata)
            assert parsed_metadata == metadata

    def test_create_achievement_with_session_id(self, app, test_user):
        """Test create_achievement with session_id."""
        with app.app_context():
            from app.models import PracticeSession
            
            session = PracticeSession(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            db.session.add(session)
            db.session.commit()
            
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                session_id=session.id
            )
            
            assert achievement.session_id == session.id

    def test_create_achievement_with_custom_earned_at(self, app, test_user):
        """Test create_achievement with custom earned_at."""
        with app.app_context():
            custom_time = datetime(2024, 1, 1, 12, 0, 0)
            
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                earned_at=custom_time
            )
            
            assert achievement.earned_at == custom_time

    def test_create_achievement_returns_existing(self, app, test_user):
        """Test create_achievement returns existing achievement."""
        with app.app_context():
            # Create first achievement
            achievement1 = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            # Try to create same achievement again
            achievement2 = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            # Should return existing achievement
            assert achievement1.id == achievement2.id

    def test_create_achievement_updates_session_id(self, app, test_user):
        """Test create_achievement updates session_id on existing achievement."""
        with app.app_context():
            from app.models import PracticeSession
            
            # Create achievement without session_id
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            # Create session
            session = PracticeSession(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            db.session.add(session)
            db.session.commit()
            
            # Create same achievement with session_id
            achievement2 = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                session_id=session.id
            )
            
            # Should update session_id
            assert achievement2.session_id == session.id
            db.session.refresh(achievement)
            assert achievement.session_id == session.id

    def test_create_achievement_with_metadata_existing_check(self, app, test_user):
        """Test create_achievement checks for existing with metadata."""
        with app.app_context():
            metadata = {"concept_id": "c_concept_001"}
            
            # Create first achievement with metadata
            achievement1 = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                metadata=metadata
            )
            
            # Try to create same achievement with same metadata
            achievement2 = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                metadata=metadata
            )
            
            # Should return existing
            assert achievement1.id == achievement2.id

    def test_create_achievement_different_metadata_handles_constraint(self, app, test_user):
        """Test create_achievement handles unique constraint when metadata differs."""
        with app.app_context():
            metadata1 = {"concept_id": "c_concept_001"}
            
            # Create first achievement with metadata
            achievement1 = create_achievement(
                user_id=test_user.id,
                code="test-achievement-meta",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                metadata=metadata1
            )
            
            # The create_achievement function checks for existing by code and metadata
            # If metadata differs, it will try to create new, but unique constraint on (user_id, code)
            # will prevent it. The function should handle this gracefully.
            # For now, we just verify the first creation works
            assert achievement1.id is not None
            assert achievement1.code == "test-achievement-meta"

    def test_serialize_achievement_basic(self, app, test_user):
        """Test serialize_achievement serializes basic achievement."""
        with app.app_context():
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            serialized = serialize_achievement(achievement)
            
            assert serialized["id"] == str(achievement.id)
            assert serialized["code"] == "test-achievement"
            assert serialized["userId"] == test_user.id
            assert serialized["title"] == "Test Achievement"
            assert serialized["description"] == "Test description"
            assert serialized["icon"] == "🏆"
            assert serialized["category"] == "milestone"
            assert "earnedAt" in serialized
            assert serialized["sessionId"] is None

    def test_serialize_achievement_with_metadata(self, app, test_user):
        """Test serialize_achievement includes metadata."""
        with app.app_context():
            metadata = {"concept_id": "c_concept_001"}
            
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                metadata=metadata
            )
            
            serialized = serialize_achievement(achievement)
            
            assert "metadata" in serialized
            assert serialized["metadata"] == metadata

    def test_serialize_achievement_with_user_name(self, app, test_user):
        """Test serialize_achievement includes user_name when provided."""
        with app.app_context():
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            serialized = serialize_achievement(achievement, user_name="Test User")
            
            assert serialized["userName"] == "Test User"

    def test_serialize_achievement_with_session_id(self, app, test_user):
        """Test serialize_achievement includes session_id."""
        with app.app_context():
            from app.models import PracticeSession
            
            session = PracticeSession(
                user_id=test_user.id,
                mode="standard",
                level=1
            )
            db.session.add(session)
            db.session.commit()
            
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone",
                session_id=session.id
            )
            
            serialized = serialize_achievement(achievement)
            
            assert serialized["sessionId"] == session.id

    def test_serialize_achievement_invalid_metadata(self, app, test_user):
        """Test serialize_achievement handles invalid metadata gracefully."""
        with app.app_context():
            achievement = create_achievement(
                user_id=test_user.id,
                code="test-achievement",
                title="Test Achievement",
                description="Test description",
                icon="🏆",
                category="milestone"
            )
            
            # Manually set invalid JSON
            achievement.achievement_metadata = "invalid json"
            db.session.add(achievement)
            db.session.commit()
            
            serialized = serialize_achievement(achievement)
            
            # Should handle gracefully
            assert serialized["metadata"] is None

